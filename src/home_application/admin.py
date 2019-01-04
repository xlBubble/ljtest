# -*- coding: utf-8 -*-
from django.contrib import admin

from models import Member, Host, Category, Group, FileCell, Item, Record, Repository


class MemberAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'get_chname', 'role', 'isActive',)
    list_filter = ('role', 'isActive',)
    search_fields = ('get_username', 'get_chname',)

    def get_username(self, obj):
        return obj.username

    def get_chname(self, obj):
        if obj.user:
            return obj.user.chname
        else:
            return ''

    get_username.short_description = u'用户名'
    get_chname.short_description = u'中文名'


class HostAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'updater', 'update_time', 'isActive',)
    list_filter = ('isActive',)
    search_fields = ('__unicode__', 'updater')


class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'updater', 'update_time', 'isActive',)
    list_filter = ('isActive',)
    search_fields = ('name', 'updater',)


class RepositoryAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'category_order', 'isActive',)
    list_filter = ('isActive',)
    search_fields = ('__unicode__',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'show_count', 'isActive',)
    list_filter = ('isActive',)
    search_fields = ('name',)


class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'isActive',)
    list_filter = ('status', 'isActive',)
    search_fields = ('name', 'status',)


class RecordAdmin(admin.ModelAdmin):
    list_display = ('item', 'creator', 'updater', 'create_time', 'update_time', 'isActive',)
    list_filter = ('isActive',)
    search_fields = ('item',)


class FileCellAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_ex', 'size', 'uploader', 'upload_time', 'isActive',)
    list_filter = ('name_ex', 'isActive',)
    search_fields = ('name', 'uploader',)


admin.site.register(Member, MemberAdmin)
admin.site.register(Host, HostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Repository, RepositoryAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Record, RecordAdmin)
admin.site.register(FileCell, FileCellAdmin)
