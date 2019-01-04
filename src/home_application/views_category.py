# -*- coding: utf-8 -*-
import json

from django.http import HttpResponse

from lib import (
    armor, get_category_params, get_category_sort_params, get_category_combine_params, get_category_recycle_params,
    get_category_edit_params, get_category_remove_params, get_category_list_params
)


@armor('POST', 'json')
def category_add(request, **kwargs):
    params = get_category_params(request, kwargs['me'])

    if params['success']:
        params['me'] = kwargs['me']
        success = params['group'].repository.add_category(params) is not None
    else:
        success = False
    info = 'Success' if success else u'类别名称已存在'
    response = json.dumps({'success': success, 'info': info})
    return HttpResponse(response)


@armor('POST', 'json')
def category_sort(request, **kwargs):
    params = get_category_sort_params(request, kwargs['me'])

    if params['success']:
        params['me'] = kwargs['me']
        success = params['group'].repository.sort_category(params)
    else:
        success = False
    info = 'Success' if success else u'类别列表已更新，请先关闭刷新'
    response = json.dumps({'success': success, 'info': info})
    return HttpResponse(response)


@armor('POST', 'json')
def category_combine(request, **kwargs):
    params = get_category_combine_params(request, kwargs['me'])

    if params['success']:
        params['me'] = kwargs['me']
        success = params['group'].repository.combine_category(params)
        if not success:
            params['info'] = u'操作失败'
    else:
        success = False
    info = 'Success' if success else params['info']
    response = json.dumps({'success': success, 'info': info})
    return HttpResponse(response)


@armor('POST', 'json')
def category_recycle(request, **kwargs):
    params = get_category_recycle_params(request, kwargs['me'])

    if params['success']:
        params['me'] = kwargs['me']
        success = params['group'].repository.recycle_category(params)
        if not success:
            params['info'] = u'操作失败'
    else:
        success = False
    info = 'Success' if success else params['info']
    response = json.dumps({'success': success, 'info': info})
    return HttpResponse(response)


@armor('POST', 'json')
def category_edit(request, **kwargs):
    params = get_category_edit_params(request, kwargs['me'])

    if params['success']:
        params['me'] = kwargs['me']
        success = params['group'].repository.edit_category(params)
    else:
        success = False
    info = 'Success' if success else u'类别名称已存在'
    response = json.dumps({'success': success, 'info': info})
    return HttpResponse(response)


@armor('POST', 'json')
def category_remove(request, **kwargs):
    params = get_category_remove_params(request, kwargs['me'])

    if params['success']:
        params['me'] = kwargs['me']
        success = params['group'].repository.remove_category(params)
    else:
        success = False
    info = 'Success' if success else u'删除失败'
    response = json.dumps({'success': success, 'info': info})
    return HttpResponse(response)


@armor('GET', 'json')
def get_category_list(request, **kwargs):
    params = get_category_list_params(request, kwargs['me'])

    if params['success']:
        params['me'] = kwargs['me']
        data = params['group'].repository.get_category_info()
        success = True
    else:
        data = []
        success = False
    info = 'Success' if success else u'获取失败'
    response = json.dumps({'success': success, 'info': info, 'data': data})
    return HttpResponse(response)
