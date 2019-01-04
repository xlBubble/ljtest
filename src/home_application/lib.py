# -*- coding: utf-8 -*-
import json
import operator
import requests

from django.http import HttpResponse

from common.mymako import render_mako_context
from models import Member, Category, Group, FileCell, Item
from common.log import logger
from settings import APP_ID, APP_TOKEN, BK_PAAS_HOST


def error_response(expect_return, info=u'操作失败', kwargs=None, request=None):
    """
    通用的错误返回
    """
    if expect_return == 'json':
        return HttpResponse(json.dumps({'success': False, 'info': info}))
    if expect_return == 'html':
        return render_mako_context(request, '403.html', kwargs)
    return HttpResponse('Invalid')


def armor(expect_method, expect_return):
    """
    视图函数预处理
    检测http.method
    获取old_url
    """
    def _armor(func):
        def new_func(request, **kwargs):
            # 如果request-method错误，返回错误页面/数据
            if request.method != expect_method:
                return error_response(expect_return=expect_return, info='HTTP %s is required' % expect_method)
            try:
                # 通用数据获取
                kwargs.update(
                    me=Member.get_or_create_member_by_user(user=request.user),
                    old_url=int(request.REQUEST.get('old_url', 0))
                )
                # 原始视图函数
                return func(request, **kwargs)
            except (Exception,):
                # 捕获视图函数中抛出的错误，保护逻辑层
                return error_response(expect_return=expect_return, request=request, kwargs=kwargs)

        return new_func
    return _armor


def remove_duplicate(data):
    """
    list顺序去重
    """
    new_set = set()
    return [item for item in data if item not in new_set and (new_set.add(item) or True)]


ESCAPE_BLACK_NAME_LIST = ['&amp;', '&gt;', '&lt;', '&quot;', '&#39;', '&nbsp;']


def check_name_format(data):
    """
    检查名称类参数是否符合规范。
    """
    return data and len(data) <= 50 \
        and all(s not in data for s in ESCAPE_BLACK_NAME_LIST)


def get_group_params(request):
    """
    获取更新group所需参数
    """
    try:
        name = request.POST.get('name', '')
        # save type: new or update or etc.
        tp = request.POST.get('type', '')
        if tp != 'update' and not check_name_format(name):
            logger.error(u'get_group_params | 参数错误: name = %s' % name)
            raise ValueError

        manager = list(set(request.POST.getlist('manager', [])))
        member = list(set(request.POST.getlist('member', [])))
        focus = list(set(request.POST.getlist('focus', [])))
        success = bool(name) and bool(manager)
        # 取并集
        manager = list(set(manager).union([request.user.username]))
        member = list(set(manager).union(member))

    except (Exception,):
        tp = ''
        name = ''
        manager = []
        member = []
        focus = []
        success = False

    try:
        group_id = int(request.POST.get('group_id', 0))
    except (ValueError,):
        group_id = 0

    data = {
        'success': success,
        'tp': tp,
        'group_id': group_id,
        'name': name,
        'manager': manager,
        'member': member,
        'focus': focus
    }
    return data


def make_group_manager(request, me):
    """
    生成会议管理数据
    """
    tp = request.GET.get('type', 'list')

    if tp == 'manage':
        try:
            group_id = int(request.GET.get('group_id', 0))
            group = me.get_group_as_manager_by_id(group_id)
            if not isinstance(group, Group):
                group = None
                tp = 'list'
        except (ValueError,):
            logger.error(u'make_group_manager | 参数缺少或错误: group_id')
            raise ValueError
    elif tp == 'list' or tp == 'new':
        group = None
    else:
        raise ValueError

    data = {
        'type': tp,
        'group': group
    }

    return data


def make_category_manager(request, me):
    """
    生成类别管理数据
    """
    try:
        group_id = int(request.GET.get('group_id', 0))
        group = me.get_group_as_manager_by_id(group_id)
        if not isinstance(group, Group):
            raise ValueError
    except (ValueError,):
        logger.error(u'make_category_manager | 参数缺少或错误: group_id')
        raise ValueError
    data = {
        'group': group
    }
    return data


def get_host_params(request, me):
    """
    获取更新host所需参数
    """
    try:
        group_id = int(request.POST.get('group_id', 0))
        now = request.POST.get('now', '')
        order = remove_duplicate(request.POST.getlist('order[]', []))

        group = me.get_group_by_id(group_id)
        if not isinstance(group, Group):
            logger.error(u'get_host_params | 参数缺少或错误: group_id = %d' % group_id)
            raise Group.DoesNotExist

        # check if guys in order[] are all member of this group
        # and if now is in order[]
        success = now and order and (now in order) and reduce(operator.and_, [group.is_member(guy) for guy in order])

        if success:
            index = order.index(now)
            order = order[index:] + order[:index]

    except (Exception,):
        order = []
        group = None
        success = False

    data = {
        'success': success,
        'order': order,
        'group': group
    }
    return data


def get_host_next_params(request, me):
    """
    获取轮转host所需参数
    """
    try:
        group_id = int(request.POST.get('group_id', 0))
        group = me.get_group_by_id(group_id)
        if not isinstance(group, Group):
            logger.error(u'get_host_next_params | 参数缺少或错误: group_id = %d' % group_id)
            raise Group.DoesNotExist

        success = True
    except (Exception,):
        group = None
        success = False

    data = {
        'success': success,
        'group': group
    }
    return data


def get_add_member_params(request):
    """
    获取添加member所需参数
    """
    info = ''
    try:
        name = request.POST.get('name', '')
        if not check_name_format(name):
            logger.error(u'get_add_member_params | 参数错误: name = %s' % name)
            raise ValueError
        member = Member.get_member_by_username(name)
        if not name or isinstance(member, Member):
            logger.error(u'get_add_member_params | 参数错误或已存在: name = %s' % name)
            info = u'该用户已添加'
            raise ValueError

        success = True

    except (Exception,):
        name = None
        success = False

    data = {
        'success': success,
        'name': name,
        'info': info
    }
    return data


def get_category_params(request, me):
    """
    获取创建category所需参数
    """
    try:
        name = request.POST.get('name', '')
        if not check_name_format(name):
            logger.error(u'get_category_params | 参数错误: name = %s' % name)
            raise ValueError
        show_count = int(request.POST.get('show_count', 0))
        describe = request.POST.get('describe', '')
        group_id = int(request.POST.get('group_id', 0))
        group = me.get_group_as_manager_by_id(group_id)
        if not isinstance(group, Group):
            logger.error(u'get_category_params | 参数缺少或错误: group_id = %d' % group_id)
            raise Group.DoesNotExist

        success = name and show_count >= 0

    except (Exception,):
        name = ''
        show_count = 0
        describe = ''
        group = None
        success = False

    data = {
        'success': success,
        'name': name,
        'show_count': show_count,
        'describe': describe,
        'group': group
    }
    return data


def get_category_sort_params(request, me):
    """
    获取排序category所需参数
    """
    try:
        order = remove_duplicate(request.POST.getlist('order[]', []))
        group_id = int(request.POST.get('group_id', 0))
        group = me.get_group_as_manager_by_id(group_id)
        if not isinstance(group, Group):
            logger.error(u'get_category_sort_params | 参数缺少或错误: group_id = %d' % group_id)
            raise Group.DoesNotExist

        if not group.repository.check_order_equal(order):
            logger.error(u'get_category_sort_params | 参数缺少或错误: order 与 数据库中的待排序的category序列不符')
            raise ValueError
        success = True

    except (Exception,):
        group = None
        order = []
        success = False

    data = {
        'success': success,
        'order': order,
        'group': group
    }
    return data


def get_category_combine_params(request, me):
    """
    获取合并category所需参数
    """
    info = 'Success'
    try:
        name = request.POST.get('name', '')
        if not check_name_format(name):
            logger.error(u'get_category_combine_params | 参数错误: name = %s' % name)
            raise ValueError
        order = remove_duplicate(request.POST.getlist('order[]', []))
        group_id = int(request.POST.get('group_id', 0))
        group = me.get_group_as_manager_by_id(group_id)

        if not isinstance(group, Group):
            info = u'没有权限'
            logger.error(u'get_category_combine_params | 参数缺少或错误: group_id = %d' % group_id)
            raise Group.DoesNotExist
        if not name:
            info = u'类别名称为必填'
            logger.error(u'get_category_combine_params | 参数缺少: name')
            raise ValueError
        if not group.repository.check_order_contain(order):
            info = u'类别列表已更新，请先关闭刷新'
            logger.error(u'get_category_combine_params | 参数错误: order 与 数据库中待合并的category序列不符')
            raise ValueError
        if not group.repository.check_category_name(name):
            info = u'类别名称已存在'
            logger.error(u'get_category_combine_params | 参数错误或已存在: name = %s' % name)
            raise ValueError
        success = True

    except (Exception,):
        name = ''
        order = []
        group = None
        success = False

    data = {
        'success': success,
        'info': info,
        'name': name,
        'order': order,
        'group': group,
    }
    return data


def get_category_recycle_params(request, me):
    """
    获取还原删除的category所需参数
    """
    info = ''
    try:
        category_id = int(request.POST.get('category_id', 0))
        group_id = int(request.POST.get('group_id', 0))
        group = me.get_group_as_manager_by_id(group_id)
        if not isinstance(group, Group):
            info = u'没有权限'
            logger.error(u'get_category_recycle_params | 参数缺少或错误: group_id = %d' % group_id)
            raise Group.DoesNotExist

        category = group.repository.get_category_by_id(category_id)
        if not isinstance(category, Category):
            info = u'类别不存在'
            logger.error(u'get_category_recycle_params | 参数缺少或错误: category_id = %d' % category_id)
            raise ValueError

        if category.isActive:
            info = u'该类别已不在回收站中，请关闭刷新'
            logger.error(u'get_category_recycle_params | 参数缺少或错误: category = %s 已不在回收站中' % category.name)
            raise ValueError

        success = True
    except (Exception,):
        category = None
        group = None
        success = False

    data = {
        'success': success,
        'info': info,
        'category': category,
        'group': group,
    }
    return data


def get_category_edit_params(request, me):
    """
    获取编辑category所需参数
    """
    # get basic params
    data = get_category_params(request, me)
    info = ''
    try:
        if data['success']:
            category_id = int(request.POST.get('category_id', 0))
            category = data['group'].repository.get_category_by_id(category_id)
            if not isinstance(category, Category):
                info = u'类别不存在'
                logger.error(u'get_category_edit_params | 参数缺少或错误: category_id = %d' % category_id)
                raise ValueError
            success = True
        else:
            raise ValueError
    except (Exception,):
        success = False
        category = None
    data['category'] = category
    data['info'] = info
    data['success'] = data['success'] and success
    return data


def get_category_remove_params(request, me):
    """
    获取删除category所需参数
    """
    try:
        group_id = int(request.POST.get('group_id', 0))
        group = me.get_group_as_manager_by_id(group_id)
        if not isinstance(group, Group):
            logger.error(u'get_category_remove_params | 参数缺少或错误: group_id = %d' % group_id)
            raise Group.DoesNotExist

        category_id = int(request.POST.get('category_id', 0))
        category = group.repository.get_category_by_id(category_id)
        if not isinstance(category, Category) or not category.isActive:
            logger.error(u'get_category_remove_params | 参数缺少或错误或 category 已删除: category_id = %d'
                         % category_id)
            raise ValueError

        success = True
    except (Exception,):
        category = None
        group = None
        success = False

    data = {
        'success': success,
        'group': group,
        'category': category
    }
    return data


def get_category_list_params(request, me):
    """
    获取拉取category所需参数
    """
    try:
        group_id = int(request.GET.get('group_id', 0))
        group = me.get_group_by_id(group_id)
        if not isinstance(group, Group):
            logger.error(u'get_category_list_params | 参数缺少或错误: group_id = %d' % group_id)
            raise Group.DoesNotExist

        success = True
    except (Exception,):
        group = None
        success = False

    data = {
        'success': success,
        'group': group,
    }
    return data


def get_item_params(request, me):
    """
    获取更新item所需参数
    """
    try:
        name = request.POST.get('name', '')
        if not check_name_format(name):
            logger.error(u'get_item_params | 参数错误: name = %s' % name)
            raise ValueError
        content = request.POST.get('content', '')
        manager = request.POST.getlist('manager', [])
        member = request.POST.getlist('member', [])
        group_id = int(request.POST.get('group_id', 0))
        category_id = int(request.POST.get('category_id', 0))
        # 取并集
        member = list(set(manager).union(member))

        if not name or not content:
            logger.error(u'get_item_params | 参数缺少: name = %s, content = %s' % (name, content))
            raise ValueError

        group = me.get_group_by_id(group_id)
        if not isinstance(group, Group):
            logger.error(u'get_item_params | 参数缺少或错误: group_id = %d' % group_id)
            raise ValueError

        category = group.repository.get_category_by_id(category_id)
        if not isinstance(category, Category):
            logger.error(u'get_item_params | 参数缺少或错误: category_id = %d' % category_id)
            raise ValueError

        manager_list = [Member.get_member_by_username(m) for m in manager]
        member_list = [Member.get_member_by_username(m) for m in member]

        success = reduce(operator.and_, [isinstance(m, Member) for m in manager_list + member_list]) and reduce(
            operator.and_,
            [isinstance(m.get_group_by_id(group.id), Group) for m in manager_list + member_list]
        )

    except (Exception,):
        name = ''
        content = ''
        manager = []
        member = []
        group = None
        category = None
        success = False

    # save type: new or update or etc.
    tp = request.POST.get('type', '')
    try:
        item_id = int(request.POST.get('item_id', 0))
    except (ValueError,):
        item_id = 0
        logger.info(u'get_item_params | 参数缺少: item_id')

    data = {
        'success': success,
        'tp': tp,
        'item_id': item_id,
        'group': group,
        'category': category,
        'name': name,
        'content': content,
        'manager': manager,
        'member': member,
    }
    return data


def make_item_manager(request):
    """
    生成已有项目数据
    """
    try:
        item_id = int(request.GET.get('item_id', 0))
    except (ValueError,):
        item_id = 0
        logger.info(u'make_item_manager | 参数缺少: item_id')

    if item_id == 0:
        old_url = int(request.GET.get('old_url', 0))
        group = Group.objects.get(id=old_url, isActive=True) if old_url != 0 else None
        data = {
            'new': True,
            'group': group
        }
    else:
        item = Item.objects.get(id=item_id, isActive=True)
        category = item.category
        group = category.repository.group.all()[0]
        manager = item.manager.filter(isActive=True)
        member = item.member.filter(isActive=True)
        data = {
            'new': False,
            'item': item,
            'manager': [guy.username for guy in (manager if manager else [])],
            'member': [guy.username for guy in (member if member else [])],
            'group': group,
            'category': category
        }
    return data


def get_item_by_category_params(request, me):
    """
    获取分category加载item的参数
    """
    try:
        group_id = int(request.GET.get('group_id', 0))
        category_id = int(request.GET.get('category_id', 0))
        tp = request.GET.get('type', 'unfinished')

        group = me.get_group_by_id(group_id)
        if not isinstance(group, Group):
            logger.error(u'get_item_by_category_params | 参数缺少或错误: group_id = %d' % group_id)
            raise ValueError

        category = group.repository.get_category_by_id(category_id)
        if not isinstance(category, Category) or not category.isActive:
            logger.error(u'get_item_by_category_params | 参数缺少或错误: category_id = %d' % category_id)
            raise ValueError

        success = True

    except (Exception,):
        success = False
        group = None
        category = None
        tp = 'unfinished'

    data = {
        'success': success,
        'group': group,
        'category': category,
        'tp': tp
    }
    return data


def get_category_change_params(request, me):
    """
    获取变更item的category所需参数
    """
    try:
        group_id = int(request.POST.get('group_id', 0))
        group = me.get_group_by_id(group_id)
        if not isinstance(group, Group):
            logger.error(u'get_category_change_params | 参数缺少或错误: group_id = %d' % group_id)
            raise Group.DoesNotExist

        category_id = int(request.POST.get('category_id', 0))
        category = group.repository.get_category_by_id(category_id)
        if not isinstance(category, Category) or not category.isActive:
            logger.error(u'get_category_change_params | 参数缺少或错误或 目标category已删除: category_id = %d'
                         % category_id)
            raise ValueError

        item_id = int(request.POST.get('item_id', 0))
        item = Item.objects.get(id=item_id, isActive=True)
        if item.category.repository.group.all()[0].id != group.id:
            logger.error(u'get_category_change_params | 参数错误: item.group.id = %d, 正确的 group.id = %d'
                         % (item.category.repository.group.all()[0].id, group.id))
            raise ValueError

        success = True
    except (Exception,):
        category = None
        group = None
        item = None
        success = False

    data = {
        'success': success,
        'group': group,
        'item': item,
        'category': category
    }
    return data


def get_item_tools_params(request, me):
    """
    获取item相关操作所需参数
    """
    try:
        group_id = int(request.POST.get('group_id', 0))
        group = me.get_group_by_id(group_id)
        if not isinstance(group, Group):
            logger.error(u'get_item_tools_params | 参数缺少或错误: group_id = %d' % group_id)
            raise Group.DoesNotExist

        item_id = int(request.POST.get('item_id', 0))
        item = Item.objects.get(id=item_id, isActive=True)
        if item.category.repository.group.all()[0].id != group.id:
            logger.error(u'get_item_tools_params | 参数错误: item.group.id = %d, 正确的 group.id = %d'
                         % (item.category.repository.group.all()[0].id, group.id))
            raise ValueError

        success = True
    except (Exception,):
        group = None
        item = None
        success = False

    data = {
        'success': success,
        'group': group,
        'item': item
    }
    return data


def get_item_and_record_params(request, me):
    """
       获取请求item和record信息所需参数
    """
    try:
        group_id = int(request.GET.get('group_id', 0))
        group = me.get_group_by_id(group_id)
        if not isinstance(group, Group):
            logger.error(u'get_item_and_record_params | 参数缺少或错误: group_id = %d' % group_id)
            raise Group.DoesNotExist

        item_id = int(request.GET.get('item_id', 0))
        item = Item.objects.get(id=item_id, isActive=True)
        if item.category.repository.group.all()[0].id != group.id:
            logger.error(u'get_item_and_record_params | 参数错误: item.group.id = %d, 正确的 group.id = %d'
                         % (item.category.repository.group.all()[0].id, group.id))
            raise ValueError

        success = True
    except (Exception,):
        group = None
        item = None
        success = False

    data = {
        'success': success,
        'group': group,
        'item': item
    }
    return data


def get_record_params(request, me):
    """
    获取更新record所需参数
    """
    try:
        content = request.POST.get('content', '')
        group_id = int(request.POST.get('group_id', 0))
        group = me.get_group_by_id(group_id)
        if not isinstance(group, Group):
            logger.error(u'get_record_params | 参数缺少或错误: group_id = %d' % group_id)
            raise Group.DoesNotExist

        item_id = int(request.POST.get('item_id', 0))
        item = Item.objects.get(id=item_id, isActive=True)
        if item.category.repository.group.all()[0].id != group.id:
            logger.error(u'get_record_params | 参数错误: item.group.id = %d, 正确的 group.id = %d'
                         % (item.category.repository.group.all()[0].id, group.id))
            raise ValueError

        if not content:
            raise ValueError

        success = True

    except (Exception,):
        success = False
        content = ''
        group = None
        item = None

    # save type: new or update or etc.
    tp = request.POST.get('type', '')
    try:
        record_id = int(request.POST.get('record_id', 0))
    except (ValueError,):
        record_id = 0

    data = {
        'success': success,
        'tp': tp,
        'record_id': record_id,
        'item': item,
        'group': group,
        'content': content,
    }
    return data


def get_record_remove_params(request, me):
    """
    获取删除record所需参数
    """
    try:
        group_id = int(request.POST.get('group_id', 0))
        group = me.get_group_by_id(group_id)
        if not isinstance(group, Group):
            logger.error(u'get_record_remove_params | 参数缺少或错误: group_id = %d' % group_id)
            raise Group.DoesNotExist

        item_id = int(request.POST.get('item_id', 0))
        item = Item.objects.get(id=item_id, isActive=True)
        if item.category.repository.group.all()[0].id != group.id:
            logger.error(u'get_record_remove_params | 参数错误: item.group.id = %d, 正确的 group.id = %d'
                         % (item.category.repository.group.all()[0].id, group.id))
            raise ValueError

        record_id = int(request.POST.get('record_id', 0))
        record = item.record.get(id=record_id, isActive=True)
        success = True

    except (Exception,):
        success = False
        record = None
        group = None
        item = None

    data = {
        'success': success,
        'record': record,
        'item': item,
        'group': group,
    }
    return data


def get_file_put_params(request, me):
    """
    获取上传file所需参数
    """
    try:
        f = request.FILES.get('file', None)

        if f is None or f.size > 1024*1024*30:
            raise ValueError
        group_id = int(request.POST.get('group_id', 0))
        group = me.get_group_by_id(group_id)
        if not isinstance(group, Group):
            logger.error(u'get_file_put_params | 参数缺少或错误: group_id = %d' % group_id)
            raise Group.DoesNotExist
        success = True

    except (Exception,):
        success = False
        f = None
        group = None

    data = {
        'file': f,
        'group': group,
        'success': success
    }
    return data


def get_file_get_params(request, me):
    """
    获取下载file所需参数
    """
    info = ''
    try:
        group_id = int(request.GET.get('group_id', 0))
        group = me.get_group_by_id(group_id)
        if not isinstance(group, Group):
            logger.error(u'get_file_get_params | 参数缺少或错误: group_id = %d' % group_id)
            raise Group.DoesNotExist

        file_id = int(request.GET.get('file_id', 0))
        f = group.get_file(file_id)
        if not isinstance(f, FileCell):
            logger.error(u'get_file_get_params | 参数缺少或错误: file_id = %d' % file_id)
            raise ValueError

        success = True

    except (Exception,), e:
        success = False
        f = None
        group = None
        info = str(e)

    data = {
        'file': f,
        'group': group,
        'success': success,
        'info': info
    }
    return data


def readfile(f, buffer_size):
    """
    用来分布读取文件以供下载
    """
    while True:
        data = f.read(buffer_size)
        if data:
            yield data
        else:
            break
    f.close()


def get_all_user(bk_token):
    """
    获取平台所有用户
    """
    url = "%s/api/c/compapi/bk_login/get_all_user/" % BK_PAAS_HOST
    form_data = {
        'app_code':  APP_ID,
        'app_secret': APP_TOKEN,
        'bk_token': bk_token
    }
    try:
        result = requests.get(url, form_data)
        data = json.loads(result.text)
        return data
    except Exception, e:
        logger.error(u'get_all_user | 接口请求错误: %s' % e)
        return {}


def get_get_groups_params(request):
    """
    获取group_tables更新所需参数
    """
    try:
        offset = int(request.GET.get('offset', 0))
        length = int(request.GET.get('length', 10))
        success = True

    except (Exception,):
        logger.error(u'get_get_groups_params | 参数错误')
        offset = 0
        length = 0
        success = False

    data = {
        'success': success,
        'offset': offset,
        'length': length
    }

    return data


def get_get_group_params(request, me):
    """
    获取group_manage所需参数
    """
    try:
        group_id = int(request.GET.get('group_id', 0))
        group = me.get_group_as_manager_by_id(group_id)
        if not isinstance(group, Group):
            raise ValueError
        success = True
    except (Exception,):
        logger.error(u'get_get_group_params | 参数错误')
        group = None
        success = False

    data = {
        'success': success,
        'group': group
    }

    return data


def get_group_remove_params(request, me):
    """
    获取删除group所需参数
    """
    try:
        group_id = int(request.POST.get('group_id', 0))
        group = me.get_group_as_manager_by_id(group_id)
        if not isinstance(group, Group):
            raise ValueError
        success = True
    except (Exception,):
        logger.error(u'get_group_remove_params | 参数错误')
        group = None
        success = False

    data = {
        'success': success,
        'group': group
    }

    return data
