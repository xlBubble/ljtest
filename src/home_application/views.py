# -*- coding: utf-8 -*-
import json

from django.http import HttpResponse, HttpResponseRedirect

from common.mymako import render_mako_context
from lib import armor, make_group_manager, make_item_manager, check_name_format, make_category_manager
from models import Member, Category, Group, Item
from common.log import logger
from settings import SITE_URL


@armor('GET', 'html')
def home(request, **kwargs):
    """
    首页
    """
    me = kwargs['me']
    kwargs['situation'] = 'index'
    kwargs['groups'] = me.get_groups()
    return render_mako_context(request, '/home_application/index.html', kwargs)


@armor('GET', 'html')
def group_manager(request, **kwargs):
    """
    新建会议组
    """
    kwargs['situation'] = 'group_manager'
    kwargs['data'] = make_group_manager(request, kwargs['me'])
    kwargs['header'] = u'会议管理'
    kwargs['members'] = Member.get_selectable_members(request.COOKIES.get('bk_token', ''))
    return render_mako_context(request, '/home_application/build_group.html', kwargs)


@armor('GET', 'html')
def meeting(request, **kwargs):
    """
    会议
    """
    group_id = int(kwargs.get('group_id', 0))
    if group_id == 0:
        return HttpResponseRedirect(SITE_URL)
    me = kwargs['me']
    group = me.get_group_by_id(group_id)
    if not isinstance(group, Group):
        raise ValueError

    me.last_group_id = group.id
    me.save()
    kwargs['situation'] = 'meeting'
    kwargs['header'] = u'会议'
    kwargs['is_manager'] = me.is_manager_of_group(group.id)
    kwargs['group'] = group
    kwargs['host'] = group.host.get_host_username()
    kwargs['members'] = group.get_members()
    kwargs['category'] = group.repository.get_category_info()
    kwargs['dustbin'] = group.repository.get_category_from_dustbin()
    return render_mako_context(request, '/home_application/meeting.html', kwargs)


@armor('GET', 'html')
def item_manager(request, **kwargs):
    """
    新建项目
    """
    group_id = int(request.GET.get('group_id', 0))
    category_id = int(request.GET.get('category_id', 0))
    me = kwargs['me']
    group = me.get_group_by_id(group_id)
    if not isinstance(group, Group):
        raise ValueError
    category = group.repository.get_category_by_id(category_id)
    if not isinstance(category, Category):
        raise ValueError

    kwargs['situation'] = 'item_manager'
    kwargs['data'] = make_item_manager(request)
    kwargs['header'] = u'新建项目' if kwargs['data']['new'] else u'管理项目'
    kwargs['groups'] = me.get_groups()
    kwargs['group'] = group
    kwargs['category'] = category
    kwargs['members'] = group.get_members()
    return render_mako_context(request, '/home_application/build_item.html', kwargs)


@armor('GET', 'html')
def record_manager(request, **kwargs):
    """
    添加跟进
    """
    group_id = int(request.GET.get('group_id', 0))
    item_id = int(request.GET.get('item_id', 0))
    me = kwargs['me']
    group = me.get_group_by_id(group_id)
    if not isinstance(group, Group):
        raise ValueError
    item = Item.objects.get(id=item_id, isActive=True)
    if item.category.repository.group.all()[0].id != group.id:
        raise ValueError

    kwargs['situation'] = 'record_manager'
    kwargs['item'] = item
    kwargs['group'] = group
    kwargs['header'] = u'项目跟进'
    return render_mako_context(request, '/home_application/build_record.html', kwargs)


@armor('POST', 'json')
def theme_save(request, **kwargs):
    """
    保存主题
    """
    try:
        theme = request.POST.get('theme', 'theme1')
        if not check_name_format(theme):
            logger.error(u'theme_save | 参数错误: theme = %s' % theme)
            raise ValueError
        if theme.isalnum():
            me = kwargs['me']
            me.theme = theme
            me.save()
            success = True
        else:
            raise ValueError
    except (Exception,):
        success = False
    info = 'Success' if success else u'保存失败'
    response = json.dumps({'success': success, 'info': info})
    return HttpResponse(response)


@armor('GET', 'html')
def category_manager(request, **kwargs):
    """
    管理类别
    """
    group_id = int(request.GET.get('group_id', 0))
    if group_id == 0:
        return HttpResponseRedirect(SITE_URL)
    me = kwargs['me']
    group = me.get_group_by_id(group_id)
    if not isinstance(group, Group):
        raise ValueError

    kwargs['situation'] = 'category_manage'
    kwargs['group'] = group
    kwargs['category'] = group.repository.get_category_info()
    kwargs['dustbin'] = group.repository.get_category_from_dustbin()
    kwargs['data'] = make_category_manager(request, kwargs['me'])
    kwargs['header'] = u'类别管理'
    return render_mako_context(request, '/home_application/manage_category.html', kwargs)
