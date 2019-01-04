# -*- coding: utf-8 -*-
import datetime
import base64

from django.db import models
from django.db.models import Q

from account.models import BkUser


class ROLE(object):
    """
    用户角色
    """
    ADMIN = 'Admin'
    MEMBER = 'Member'
    STRANGER = 'Stranger'


class STATUS(object):
    """
    工作事项状态
    """
    PENDING = 'Pending'
    PROCESSING = 'Processing'
    FINISHED = 'Finished'


ROLES = ((ROLE.ADMIN, u'管理员',), (ROLE.MEMBER, u'普通成员',), (ROLE.STRANGER, u'陌生人',),)
STATUSES = ((STATUS.PENDING, u'挂起',), (STATUS.PROCESSING, u'进行中',), (STATUS.FINISHED, u'已完成',),)


class Member(models.Model):
    """
    用户
    """
    user = models.ForeignKey(BkUser, blank=True, null=True)
    username = models.CharField(u"用户名", max_length=128)
    role = models.CharField(u'角色', choices=ROLES, max_length=10)
    theme = models.CharField(u'主题', max_length=100, default='theme1')
    last_group_id = models.IntegerField(u'最近进入的小组', default=0)
    # 伪删除
    isActive = models.BooleanField(u'是否激活', default=True)

    class Meta:
        verbose_name = u'用户'
        verbose_name_plural = u'用户'

    def __unicode__(self):
        return self.username

    # 获取所有已存在的用户
    @classmethod
    def get_selectable_members(cls, bk_token):
        from lib import get_all_user
        data = get_all_user(bk_token)
        if data['result']:
            for d in data['data']:
                Member.get_or_create_member_by_username(d['username'])

            members = Member.objects.filter(isActive=True)
            return members
        else:
            return []

    # 通过username获取或创建一个member
    @classmethod
    def get_or_create_member_by_username(cls, username):
        member = Member.get_member_by_username(username)
        if not isinstance(member, Member):
            # create without BkUser
            member = Member(username=username, role=ROLE.STRANGER)
            member.save()
        return member

    # 通过BkUser获取或创建一个member
    @classmethod
    def get_or_create_member_by_user(cls, user):
        member = Member.get_member_by_username(user.username)
        if isinstance(member, Member):
            # if it was created without user, then add user to it
            if not member.user:
                member.user = user
                member.save()
                member.make_default_group()
        else:
            # or create a new one
            member = Member(user=user, username=user.username, role=ROLE.STRANGER)
            member.save()
            member.make_default_group()
        return member

    def make_default_group(self):
        from default_case import make_default_case
        make_default_case(self)

    # 通过username获取一个member
    @classmethod
    def get_member_by_username(cls, username):
        try:
            # with username
            member = cls.objects.get(username=username, isActive=True)
        except cls.DoesNotExist:
            try:
                # with user
                member = cls.objects.get(user__username=username, isActive=True)
            except cls.DoesNotExist:
                member = None
        return member

    # 判断用户是否为该id的group的管理员
    def is_manager_of_group(self, group_id):
        try:
            group = Group.objects.get(id=int(group_id), isActive=True)
            group.manager.get(id=self.id, isActive=True)
            return True
        except (Group.DoesNotExist, Member.DoesNotExist, ValueError):
            return False

    # 通过group_id获取用户加入过的group
    def get_group_by_id(self, group_id):
        try:
            group = Group.objects.get(id=int(group_id), isActive=True)
            group.member.get(id=self.id, isActive=True)
            return group
        except (Group.DoesNotExist, Member.DoesNotExist, ValueError):
            return None

    # 通过group_id获取用户加入过且为管理员的group
    def get_group_as_manager_by_id(self, group_id):
        if self.is_manager_of_group(group_id):
            group = self.get_group_by_id(group_id)
        else:
            group = None
        return group

    # 获取所有管理的group信息
    def get_groups_as_manager(self, params):
        offset = params['offset']
        length = params['length']
        groups = self.group_as_manager.filter(isActive=True)
        data = {
            'total': groups.count(),
            'data': [
                {
                    'name': g.name,
                    'members': [m.username for m in g.member.filter(isActive=True) or []],
                    'creator': g.creator.username,
                    'create_time': g.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                    'updater': g.updater.username,
                    'update_time': g.update_time.strftime("%Y-%m-%d %H:%M:%S"),
                    'group_id': g.id
                } for g in groups[offset: length] or []
            ]
        }
        return data

    # 获取所有加入过的group信息
    def get_groups(self):
        groups = self.group_as_member.filter(isActive=True)
        data = [
            {
                'id': group.id,
                'name': base64.b64encode(group.name.encode('utf-8')),
            }
            for group in groups
        ]
        return data


class Host(models.Model):
    """
    主持人顺序
    """
    host_order = models.TextField(u'主持人顺序', default='')
    updater = models.ForeignKey(Member, verbose_name=u'最后操作者', blank=True, related_name='host_as_updater')
    update_time = models.DateTimeField(u'最后更新', auto_now=True)
    # 伪删除
    isActive = models.BooleanField(u'是否激活', default=True)

    class Meta:
        verbose_name = u'主持人列表'
        verbose_name_plural = u'主持人列表'

    def __unicode__(self):
        try:
            return self.host_order.split(',')[0]
        except (ValueError, IndexError, Member.DoesNotExist):
            return ''

    # 通过group，获取该group中用户的username列表
    @classmethod
    def make_order_by_group(cls, group):
        order = []
        for member in group.member.filter(isActive=True):
            order.append(member.username)
        return order

    # 创建一个group的host对象
    @classmethod
    def build(cls, group, updater):
        if not isinstance(updater, Member):
            raise None

        order = Host.make_order_by_group(group)
        host = Host()
        host.host_order = ','.join(order)
        host.updater = updater
        host.save()
        return host

    # 更新一个group的host对象
    @classmethod
    def update(cls, group, updater):
        if not isinstance(updater, Member):
            raise None

        order = Host.make_order_by_group(group)
        host = group.host
        host.host_order = ','.join(order)
        host.updater = updater
        host.save()
        return host

    # 替换主持人顺序列表host-order
    def modify(self, order, updater):
        if not isinstance(updater, Member):
            raise None

        self.host_order = ','.join(order)
        self.updater = updater
        self.save()

    # 获取当前、上一个、下一个主持人信息，当前主持人在位置0
    def get_host_username(self):
        order = self.host_order.split(',')
        data = {'pre': '', 'now': '', 'next': '', 'list': []}
        if order:
            data['pre'] = order[-1]
            data['now'] = order[0]
            data['next'] = order[1] if len(order) > 1 else order[0]
            data['list'] = order
        return data

    # 循环主持人队列
    def cycle_host(self):
        order = self.host_order.split(',')
        new_order = order[1:]
        new_order.append(order[0])
        self.host_order = ','.join(new_order)
        self.save()


class Repository(models.Model):
    """
    仓库
    """
    # Make order[id,] prevent name-change
    category_order = models.TextField(u'类别顺序(id)', default='')
    updater = models.ForeignKey(Member, verbose_name=u'最后操作者', blank=True, related_name='repository_as_updater')
    update_time = models.DateTimeField(u'最后更新', auto_now=True)
    # 伪删除
    isActive = models.BooleanField(u'是否激活', default=True)

    class Meta:
        verbose_name = u'仓库'
        verbose_name_plural = u'仓库'

    def __unicode__(self):
        return self.group.all()[0].name

    # 创建一个repository对象
    @classmethod
    def build(cls, updater):
        if not isinstance(updater, Member):
            raise None

        repository = Repository()
        repository.host_order = ''
        repository.updater = updater
        repository.save()
        return repository

    # 检查该category-name是否已存在
    def check_category_name(self, name):
        # including active=false because it can be recovered
        category = self.category.filter(name=name)
        return not bool(category)

    # 添加一个新的category
    def add_category(self, params):
        try:
            if self.check_category_name(params['name']):
                updater = params['me']
                category = Category.build(params['name'], params['show_count'], params['describe'])
                if not isinstance(category, Category):
                    raise ValueError
                category.repository = self
                category.save()

                self.category_order += (',%d' if self.category_order else '%d') % category.id
                self.updater = updater
                self.save()
                return category
            else:
                raise ValueError
        except (Exception,):
            return None

    # 获取该repository下所有的category信息
    def get_category_info(self):
        order = self.category_order.split(',')
        cate_list = []
        try:
            for uid in order:
                o = self.category.get(id=int(uid), isActive=True)
                cate_list.append({
                    'id': o.id,
                    'name': base64.b64encode(o.name.encode('utf-8')),
                    'show_count': o.show_count,
                    'describe': base64.b64encode(o.describe.encode('utf-8'))
                })
        except (Exception,):
            cate_list = []

        return cate_list

    # 通过category_id获取该repository中的category
    def get_category_by_id(self, uid):
        try:
            return self.category.get(id=int(uid))
        except (Exception,):
            return None

    # 获取该repository中所有被删除的category
    def get_category_from_dustbin(self):
        categories = self.category.filter(isActive=False)
        cate_list = [
            {
                'id': category.id,
                'name': base64.b64encode(category.name.encode('utf-8'))
            } for category in categories
        ]
        return cate_list

    # 检查该order是否与category-order是同一个集合
    def check_order_equal(self, order):
        category_order = self.category_order.split(',')
        # if is the same set
        return set(order) == set(category_order)

    # 检查该order是否为category-order的一个子集
    def check_order_contain(self, order):
        category_order = self.category_order.split(',')
        # if is the subset of category-order
        return set(order).issubset(set(category_order))

    # 用给定的order替换category-order(重排序
    def sort_category(self, params):
        try:
            if self.check_order_equal(params['order']):
                self.category_order = ','.join(params['order'])
                self.updater = params['me']
                self.save()
                return True
            else:
                raise ValueError
        except (Exception,):
            return False

    # 将多个category合并为一个新的category
    def combine_category(self, params):
        try:
            updater = params['me']
            if self.check_order_contain(params['order']) and self.check_category_name(params['name']):
                new_category = Category.build(params['name'])
                if not isinstance(new_category, Category):
                    raise ValueError
                new_category.repository = self
                new_category.save()
                for o in params['order']:
                    category = self.remove_category_by_id(int(o))
                    if isinstance(category, Category):
                        category.father = new_category
                        category.ancient = new_category
                        category.save()
                self.category_order += (',%d' if self.category_order else '%d') % new_category.id
                self.updater = updater
                self.save()
                return True
            else:
                raise ValueError
        except (Exception,):
            return False

    # 将category-order中的category_id移除
    def remove_from_order_by_id(self, uid):
        # remove a category_id from order
        category_order = self.category_order.split(',')
        if str(uid) in category_order:
            index = category_order.index(str(uid))
            self.category_order = ','.join(category_order[:index] + category_order[index+1:])
            self.save()
            return True
        return False

    # 通过category_id将repository中的category移除
    def remove_category_by_id(self, uid):
        try:
            category = Category.objects.get(id=int(uid), isActive=True)
            if self.remove_from_order_by_id(int(uid)):
                category.isActive = False
            category.save()
            return category
        except (Exception,):
            return None

    # 恢复删除的category
    def recycle_category(self, params):
        try:
            updater = params['me']
            category = params['category']
            if not category.isActive:
                category.isActive = True
                category.father = category
                category.save()
                category.make_families_ancient(category)
                self.category_order += (',%d' if self.category_order else '%d') % category.id
                self.updater = updater
                self.save()
                return True
            else:
                raise ValueError
        except (Exception,):
            return False

    # 编辑category
    def edit_category(self, params):
        try:
            if params['category'].name == params['name'] or self.check_category_name(params['name']):
                updater = params['me']
                category = params['category']
                if not isinstance(category, Category):
                    raise ValueError
                category.name = params['name']
                category.show_count = params['show_count']
                category.describe = params['describe']
                category.save()

                self.updater = updater
                self.save()
                return True
            else:
                raise ValueError
        except (Exception,):
            return False

    # 删除category
    def remove_category(self, params):
        try:
            updater = params['me']
            category = params['category']
            if not isinstance(category, Category):
                raise ValueError
            if category.isActive:
                self.remove_category_by_id(category.id)
                self.updater = updater
                self.save()
                return True
            else:
                raise ValueError

        except (Exception,):
            return False


class Group(models.Model):
    """
    会议组
    """
    name = models.CharField(u'名称', max_length=300)
    repository = models.ForeignKey(Repository, verbose_name=u'仓库', blank=True, null=True, related_name='group')
    manager = models.ManyToManyField(Member, verbose_name=u'管理员', blank=True, related_name='group_as_manager')
    member = models.ManyToManyField(Member, verbose_name=u'成员', blank=True, related_name='group_as_member')
    focus = models.ManyToManyField(Member, verbose_name=u'关注人', blank=True, related_name='group_as_focus')
    host = models.ForeignKey(Host, verbose_name=u'主持人列表', blank=True, null=True, related_name='group')
    updater = models.ForeignKey(Member, verbose_name=u'最后操作者', blank=True, related_name='group_as_updater')
    update_time = models.DateTimeField(u'最后更新', auto_now=True)
    creator = models.ForeignKey(Member, verbose_name=u'创建者', blank=True, null=True, related_name='group_as_creator')
    create_time = models.DateTimeField(u'创建时间', auto_now_add=True, blank=True, null=True)
    # 伪删除
    isActive = models.BooleanField(u'是否激活', default=True)

    class Meta:
        verbose_name = u'会议组'
        verbose_name_plural = u'会议组'

    def __unicode__(self):
        return self.name

    # 检查提交的username是否都存在
    @classmethod
    def check_params(cls, params):
        for key in ['manager', 'member', 'focus']:
            for username in params[key]:
                member = Member.get_member_by_username(username)
                if not member:
                    return False
        return True

    # 接收参数，生成group
    def accept_params(self, params):
        self.updater = params['me']
        self.save()
        for key in ['manager', 'member', 'focus']:
            # 清除原先的连表结构
            exec ("self.%s.clear()" % key) in {'self': self}
            for username in params[key]:
                member = Member.get_member_by_username(username)
                # 建立新的关系
                exec("self.%s.add(member)" % key) in {'self': self, 'member': member}
        self.save()

    # 创建一个新的group
    @classmethod
    def build(cls, params):
        group = Group()
        try:
            group.name = params['name']
            group.creator = params['me']
            if Group.check_params(params):
                group.accept_params(params)
            else:
                raise ValueError

            # build host
            host = Host.build(group, group.updater)
            if not isinstance(host, Host):
                raise ValueError

            # build repository
            repository = Repository.build(group.updater)
            if not isinstance(repository, Repository):
                raise ValueError

            group.host = host
            group.repository = repository
            group.save()
        except (ValueError, KeyError):
            return None
        return group

    # 更新一个group
    @classmethod
    def update(cls, params):
        try:
            updater = params['me']
            # Check if is manager
            if not updater.is_manager_of_group(int(params['group_id'])):
                raise ValueError
            group = Group.objects.get(id=int(params['group_id']), isActive=True)
            if Group.check_params(params):
                group.name = params['name']
                group.accept_params(params)
            else:
                raise ValueError

            # update host
            host = Host.update(group, group.updater)
            if not isinstance(host, Host):
                raise ValueError

        except (Group.DoesNotExist, KeyError, ValueError):
            group = None
        return group

    # 对group进行操作(创建/更新
    @classmethod
    def modify(cls, params):
        # new group
        if params['tp'] == 'new':
            group = Group.build(params)
        # update group
        elif params['tp'] == 'update':
            group = Group.update(params)
        # others
        else:
            group = None
        return group

    # 获取该group下的所有成员
    def get_members(self):
        members = self.member.filter(isActive=True)
        return members

    # 判断一个username属否属于该group
    def is_member(self, username):
        try:
            Member.get_member_by_username(username).get_group_by_id(self.id)
            return True
        except (Member.DoesNotExist, Group.DoesNotExist,):
            return False

    # 上传文件
    def put_file(self, params):
        cell = FileCell.build(params)
        if isinstance(cell, FileCell):
            cell.group = self
            cell.save()
        return cell

    # 根据file_cell_id下载文件
    def get_file(self, uid):
        try:
            return self.file.get(id=int(uid), isActive=True)
        except FileCell.DoesNotExist:
            return None

    # 注销group
    def remove(self):
        self.isActive = False
        self.save()


class Category(models.Model):
    """
    工作项类别
    """
    name = models.CharField(u'分类名称', max_length=300)
    describe = models.TextField(u'分类说明', default='')
    show_count = models.IntegerField(u'跟进记录默认显示数量', default=1)

    repository = models.ForeignKey(Repository, verbose_name=u'所属仓库', blank=True, null=True, related_name='category')
    father = models.ForeignKey('self', verbose_name=u'父类', blank=True, null=True, related_name='son')
    ancient = models.ForeignKey('self', verbose_name=u'祖先', blank=True, null=True, related_name='family')
    # 伪删除
    isActive = models.BooleanField(u'是否激活', default=True)

    class Meta:
        verbose_name = u'内容分类'
        verbose_name_plural = u'内容分类'

    def __unicode__(self):
        return self.name

    # 创建一个新的category
    @classmethod
    def build(cls, name, show_count=1, describe=''):
        try:
            category = Category()
            category.name = name
            category.show_count = show_count
            category.describe = describe
            category.save()
            category.father = category
            category.ancient = category
            category.save()
        except (Exception,):
            category = None
        return category

    # 为所有儿子节点确定祖先
    def make_families_ancient(self, ancient):
        self.ancient = ancient
        self.save()
        sons = self.son.filter(~Q(id=self.id))
        for son in sons:
            son.make_families_ancient()

    # 获取所有儿子节点的信息(包含item数据
    def get_families(self, tp='unfinished'):
        # 未结项
        if tp == 'unfinished':
            # all items refers to it
            item = self.item.filter(Q(isActive=True) & ~Q(status=STATUS.FINISHED))
        # 包含已结项
        elif tp == 'all':
            item = self.item.filter(isActive=True)
        else:
            item = []
        # 所有儿子节点
        family = self.family.filter(~Q(id=self.id))

        data = [i.get_full_info(show_count=self.show_count) for i in item]
        for f in family:
            # 递归
            data += f.get_families(tp)

        # 按照创建时间、是否置顶、置顶权重以此排序
        return sorted(
                    sorted(
                        sorted(
                            # 1. sorted by create time
                            data, key=lambda x: x['item']['create_time']
                            # 2. sorted by if keep top
                        ), key=lambda x: x['item']['keep_top'], reverse=True
                        # 3. sorted by top-point
                    ), key=lambda x: x['item']['top_point'], reverse=True
                )

    # 获取所有儿子节点中置顶权重最高的值
    def get_max_top_point(self):
        item = self.item.filter(isActive=True)
        family = self.family.filter(~Q(id=self.id))

        point = max([i.top_point for i in item] if item else [0])

        # 递归
        for f in family:
            point = max(point, f.get_max_top_point())

        return point

    # 获取祖先
    def get_ancient(self):
        if self.ancient.id == self.id:
            return self
        # 路径压缩
        self.ancient = self.ancient.get_ancient()
        self.save()
        return self.ancient


class Item(models.Model):
    """
    工作事项/项目
    """
    name = models.CharField(u'名称', max_length=50, default='')
    content = models.TextField(u'内容', default='')
    status = models.CharField(u'状态', choices=STATUSES, max_length=10)

    category = models.ForeignKey(Category, verbose_name=u'分类', related_name='item')
    creator = models.ForeignKey(Member, verbose_name=u'创建者', related_name='item_as_creator')
    updater = models.ForeignKey(Member, verbose_name=u'最后一次编辑者', related_name='item_as_updater')
    manager = models.ManyToManyField(Member, verbose_name=u'责任者', related_name='item_as_manager')
    member = models.ManyToManyField(Member, verbose_name=u'负责成员', blank=True, related_name='item_as_member')

    create_time = models.DateTimeField(u'创建时间', auto_now_add=True)
    update_time = models.DateTimeField(u'最后更新', auto_now=True)
    finish_time = models.DateTimeField(u'完成时间', blank=True, null=True)
    keep_top = models.BooleanField(u'是否置顶', default=False)
    top_point = models.IntegerField(u'置顶指数', default=0)
    # 伪删除
    isActive = models.BooleanField(u'是否激活', default=True)

    class Meta:
        verbose_name = u'工作项'
        verbose_name_plural = u'工作项'

    def __unicode__(self):
        return self.name

    # 接收参数，生成item
    def accept_params(self, params):
        self.name = params['name']
        self.content = params['content']
        self.updater = params['me']
        self.save()
        for key in ['manager', 'member']:
            # 清除原先的连表结构
            exec ("self.%s.clear()" % key) in {'self': self}
            for username in params[key]:
                member = Member.get_member_by_username(username)
                # 建立新的关系
                exec("self.%s.add(member)" % key) in {'self': self, 'member': member}
        self.save()

    # 创建一个新的item
    @classmethod
    def build(cls, params):
        item = Item()
        try:
            item.status = STATUS.PROCESSING
            item.creator = params['me']
            item.category = params['category']
            item.accept_params(params)
        except (ValueError, KeyError), e:
            return e
        return item

    # 更新一个item
    @classmethod
    def update(cls, params):
        try:
            item = Item.objects.get(id=int(params['item_id']), isActive=True)
            # check if belong to this category
            if item.category.id != params['category'].id:
                raise ValueError
            item.accept_params(params)

        except (Item.DoesNotExist, KeyError, ValueError,):
            item = None
        return item

    # 对item进行操作 (创建/更新
    @classmethod
    def modify(cls, params):
        # new item
        if params['tp'] == 'new':
            item = Item.build(params)
        # update items
        elif params['tp'] == 'update':
            item = Item.update(params)
        # others
        else:
            item = None
        return item

    # 获取该item的信息
    def get_info(self):
        data = {
            'name': base64.b64encode(self.name.encode('utf-8')),
            'manager': [m.username for m in self.manager.filter(isActive=True)] if self.manager else [],
            'content': self.content,
            'keep_top': self.keep_top,
            'top_point': self.top_point,
            'create_time': (self.create_time - datetime.datetime(1970, 1, 1)).total_seconds(),
            'item_id': self.id,
            'finished': bool(self.status == STATUS.FINISHED)
        }
        return data

    # 变更该item所属的category
    def change_category(self, params):
        category = params['category']
        if isinstance(category, Category):
            self.keep_top = False
            self.top_point = 0
            self.category = category
            self.save()
            return True
        else:
            return False

    # 结项
    def change_finish(self):
        if self.status == STATUS.FINISHED:
            self.status = STATUS.PROCESSING
        else:
            self.keep_top = False
            self.top_point = 0
            self.status = STATUS.FINISHED
        self.save()
        return True

    # 置顶/取消置顶
    def change_top(self):
        if self.keep_top:
            self.top_point = 0
            self.keep_top = False
        else:
            # 赋于所有儿子节点中最大权重+1，保证最大
            self.top_point = self.category.get_ancient().get_max_top_point() + 1
            self.keep_top = True
        self.save()
        return True

    # 获取该item的全部信息(包括record
    def get_full_info(self, show_count=None):
        data = {
            'item': self.get_info(),
            'record': [r.get_info() for r in self.record.filter(isActive=True).order_by('-create_time')[: show_count]]
            if self.record.filter(isActive=True) else []
        }
        return data

    # 删除该item
    def remove(self, params):
        self.updater = params['me']
        self.isActive = False
        self.save()
        return True


class Record(models.Model):
    """
    工作事项跟进
    """
    item = models.ForeignKey(Item, verbose_name=u'所属工作项', related_name='record')
    content = models.TextField(u'内容')

    creator = models.ForeignKey(Member, verbose_name=u'创建者', related_name='record_as_creator')
    updater = models.ForeignKey(Member, verbose_name=u'最后一次编辑者', related_name='record_as_updater')
    create_time = models.DateTimeField(u'创建于', auto_now_add=True)
    update_time = models.DateTimeField(u'最后更新', auto_now=True)
    # 伪删除
    isActive = models.BooleanField(u'是否激活', default=True)

    class Meta:
        verbose_name = u'事项跟进'
        verbose_name_plural = u'事项跟进'

    def __unicode__(self):
        return self.item.name

    # 获取该record的信息
    def get_info(self):
        data = {
            'record_id': self.id,
            'content': self.content,
            'creator': self.creator.username,
            'updater': self.updater.username,
            'create_time': self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            'update_time': self.update_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        return data

    # 接收参数，生成record
    def accept_params(self, params):
        self.content = params['content']
        self.updater = params['me']
        self.save()

    # 创建一个新的record
    @classmethod
    def build(cls, params):
        record = Record()
        try:
            record.creator = params['me']
            record.item = params['item']
            record.accept_params(params)
        except (ValueError, KeyError):
            return None
        return record

    # 更新一个record
    @classmethod
    def update(cls, params):
        try:
            record = Record.objects.get(id=int(params['record_id']), isActive=True)
            if record.item.id != params['item'].id:
                raise ValueError
            record.accept_params(params)

        except (Record.DoesNotExist, KeyError, ValueError,):
            record = None
        return record

    # 对record进行操作 (创建/更新
    @classmethod
    def modify(cls, params):
        # new record
        if params['tp'] == 'new':
            record = Record.build(params)
        # update record
        elif params['tp'] == 'update':
            record = Record.update(params)
        # others
        else:
            record = None
        return record

    # 删除一个record
    def remove(self, params):
        self.updater = params['me']
        self.isActive = False
        self.save()
        return True


class FileCell(models.Model):
    """
    文件管理
    """
    name = models.CharField(u'文件的真实名称', max_length=255)
    name_ex = models.CharField(u'文件拓展名，方便排序', max_length=255)
    size = models.IntegerField(u'文件大小', default=0)
    content = models.FileField(u'文件内容', upload_to='uploads/', blank=True, null=True)
    content_new = models.BinaryField(u'文件二进制类容', default='')
    group = models.ForeignKey(Group, verbose_name=u'所属会议组', related_name='file', blank=True, null=True)

    upload_time = models.DateTimeField(u'上传时间', auto_now_add=True)
    uploader = models.ForeignKey(Member, verbose_name=u'上传者', related_name='file_cell_as_uploader')
    # 伪删除
    isActive = models.BooleanField(u'是否激活', default=True)

    class Meta:
        verbose_name = u'文件管理'
        verbose_name_plural = u'文件管理'

    def __unicode__(self):
        return self.name

    # 创建一个新的file-cell
    @classmethod
    def build(cls, params):
        try:
            f = params['file']
            uploader = params['me']
            cell = FileCell()
            cell.name = f.name
            cell.name_ex = f.name.split('.')[-1] if '.' in f.name else ''
            cell.size = f.size
            cell.content_new = f.read()

            # f.name = "%s-%s-%s" % (f.name, uploader.user.username, str(time.time()))
            # cell.content = f
            cell.uploader = uploader
            cell.save()
            return cell
        except (Exception,):
            return None
