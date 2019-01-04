# -*- coding: utf-8 -*-

from django.conf.urls import patterns

urlpatterns = patterns('home_application.views',
                       (r'^$', 'home'),
                       (r'group/manager/', 'group_manager'),
                       (r'meeting/(?P<group_id>[0-9]+)/', 'meeting'),
                       (r'item/manager/', 'item_manager'),
                       (r'record/manager/', 'record_manager'),
                       (r'category/manager', 'category_manager'),
                       (r'theme/save/', 'theme_save'),
                       )

urlpatterns += patterns('home_application.views_member',
                        (r'group/save/', 'group_save'),
                        (r'host/save/', 'host_save'),
                        (r'host/next/', 'host_next'),
                        (r'group/get/', 'get_groups'),
                        (r'group/fetch/', 'get_group'),
                        (r'group/remove/', 'group_remove'),
                        )

urlpatterns += patterns('home_application.views_category',
                        (r'category/add/', 'category_add'),
                        (r'category/sort/', 'category_sort'),
                        (r'category/combine/', 'category_combine'),
                        (r'category/recycle/', 'category_recycle'),
                        (r'category/edit/', 'category_edit'),
                        (r'category/remove/', 'category_remove'),
                        (r'category/get/', 'get_category_list'),
                        )

urlpatterns += patterns('home_application.views_item',
                        (r'item/save/', 'item_save'),
                        (r'item/get/', 'get_item_by_category'),
                        (r'category/change/', 'category_change'),
                        (r'item/finish/', 'item_finish'),
                        (r'item/top/', 'item_top'),
                        (r'item/full/', 'get_item_and_record'),
                        (r'item/remove/', 'item_remove'),
                        )

urlpatterns += patterns('home_application.views_record',
                        (r'record/save/$', 'record_save'),
                        (r'record/remove/$', 'record_remove'),
                        )


urlpatterns += patterns('home_application.views_file',
                        (r'file/put/', 'file_put'),
                        (r'file/get/', 'file_get'),
                        )
