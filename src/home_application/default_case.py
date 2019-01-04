# -*- coding: utf-8 -*-
import copy

from django.core.files import File

from models import Group, Category, Item, Record
from settings import SITE_URL


def make_default_case(member):
    # 创建会议组
    group_data = {
        'tp': 'new',
        'name': u'快速上手',
        'creator': member,
        'manager': [member.username, ],
        'member': [member.username, ],
        'focus': [],
        'me': member,
    }
    group = Group.modify(group_data)
    if not isinstance(group, Group):
        return

    params = {
        'group': group,
        'me': member,
        'category': [
            {
                'name': u'写在开头',
                'show_count': 5,
                'describe': u'这里可以添加对这个类别的注释',
                'item': [
                    {
                        'name': u'快来试试吧',
                        'content': u'iwork提供的是一套方便的小组会议、项目管理的解决方案，旨在节省会议成本，提高会议效率。',
                        'record': [
                            {
                                'content': u'<img src="%s">',
                                'url': 'static/img/example.png'
                            }
                        ]
                    }
                ]
            },
            {
                'name': u'布局介绍',
                'show_count': 5,
                'describe': u'这里可以添加对这个类别的注释',
                'item': [
                    {
                        'name': u'导航栏',
                        'content': u'位于页面顶部的部分',
                        'record': [
                            {'content': u'右边的四个色块是主题选择，可以选择自己喜欢的颜色。'},
                        ]
                    },
                    {
                        'name': u'管理',
                        'content': u'位于页面右上角的管理',
                        'record': [
                            {'content': u'会议管理：如果你是会议管理员的话，可以添加或移除会议中的成员。'},
                            {'content': u'类别管理：如果你是会议管理员的话，可以使用添加、移除、排序、合并、还原等类别操作。'}
                        ]
                    },
                    {
                        'name': u'主页面',
                        'content': u'包含会议的内容',
                        'record': [
                            {'content': u'项目分类别展示在主页面上，可以在对应的类别中添加新的项目，在对应的项目中添加跟进。'}
                        ]
                    }
                ],
            },
            {
                'name': u'功能介绍',
                'show_count': 5,
                'describe': u'这里可以添加对这个类别的注释',
                'item': [
                    {
                        'name': u'成员管理',
                        'content': u'成员管理功能，仅限管理员',
                        'record': [
                            {'content': u'管理员拥有管理成员、管理类别的权限。'},
                            {'content': u'普通成员无法拉人，也不能添加新的类别。'},
                            {'content': u'关注人仅作一个备注，作为该会议组的知会人，没有进入会议的权限。'}
                        ]
                    },
                    {
                        'name': u'类别管理',
                        'content': u'类别管理功能，仅限管理员，入口在右上角管理中。',
                        'record': [
                            {'content': u'<span style="color:#66ccff">新增类别</span>可以添加一个新的类别。'},
                            {'content': u'<span style="color:#66ccff">类别排序</span>自定义页面上的类别顺序，通过拖拽来排序。'},
                            {'content': u'<span style="color:#66ccff">类别合并</span>合并两个类别，生成一个新的类别；'
                                        u'这些类别下的项目会被放到新类别中。'},
                            {'content': u'<span style="color:#66ccff">类别回收站</span>恢复删除或被合并的类别，之前这个类别下的项目会重新回到类别里。'},
                            {'content': u'管理员可以点击类别管理页面中，类别名右边的按钮，来编辑和删除类别；删除后的类别可以在回收站中找到。'}
                        ]
                    },
                    {
                        'name': u'项目、跟进管理',
                        'content': u'项目、跟进管理功能',
                        'record': [
                            {'content': u'点击任意类别右边的<span style="color:#66ccff">添加项目</span>可以在该类别下新增一个项目。'},
                            {'content': u'可以通过拖动表格的列分界线，来控制展示的宽度。'},
                            {'content': u'通过右键点击项目，可以添加跟进，跟进将会在项目进度一栏展示出来，展示的跟进条数可以在类别编辑中设置。'},
                            {'content': u'通过右键点击项目，可以编辑项目内容。'},
                            {'content': u'通过右键点击项目，可以更改项目所属的类别，将该项目移动到另一个类别中去。'},
                            {'content': u'通过右键点击项目，可以结束项目，表示项目已经完结；'
                                        u'结项的项目将不会再显示在页面，但可以点击类别右边的显示<span style="color:#66ccff">结项</span>来查看它们。'},
                            {'content': u'通过右键点击项目，可以将项目置顶，该项目会出现在这个类别的最上方。'}
                        ]
                    },
                ]
            },
        ]
    }
    # 用上述参数创建会议组
    make_default_detail(params)


def make_default_detail(params):
    # Get Group & Member
    group = params['group']
    me = params['me']
    # Make Category
    for category_raw in params['category']:
        category_data = copy.deepcopy(category_raw)
        category_data['group'] = group
        category_data['me'] = me
        category = group.repository.add_category(category_data)
        if not isinstance(category, Category):
            continue

        # Make Item Under Category
        for item_raw in category_raw['item']:
            item_data = copy.deepcopy(item_raw)
            item_data['group'] = group
            item_data['category'] = category
            item_data['me'] = me
            item_data['tp'] = 'new'
            item_data['manager'] = [me.username]
            item_data['member'] = [me.username]
            item = Item.modify(item_data)
            if not isinstance(item, Item):
                continue

            # Make Record Under Item
            for record_raw in reversed(item_raw['record']):
                record_data = copy.deepcopy(record_raw)
                record_data['group'] = group
                record_data['item'] = item
                record_data['me'] = me
                record_data['tp'] = 'new'

                if 'url' in record_data:
                    f = open(record_data['url'], 'rb')
                    df = File(f)
                    file_data = {
                        'file': df,
                        'me': me
                    }
                    cell = group.put_file(file_data)
                    record_data['content'] %= '%sfile/get/?group_id=%d&file_id=%d' % (SITE_URL, group.id, cell.id)

                record = Record.modify(record_data)
                if not isinstance(record, Record):
                    continue
