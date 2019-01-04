# -*- coding: utf-8 -*-
import json

from django.http import HttpResponse, HttpResponseRedirect

from lib import (
    armor, get_item_params, get_item_by_category_params, get_category_change_params, get_item_tools_params,
    get_item_and_record_params
)
from common.mymako import render_mako_context
from models import Item
from settings import SITE_URL


@armor('POST', 'html')
def item_save(request, **kwargs):
    params = get_item_params(request, kwargs['me'])
    item = None

    if params['success']:

        params['me'] = kwargs['me']
        # Make Modify
        item = Item.modify(params)

    if isinstance(item, Item):
        # enter meeting
        response = HttpResponseRedirect(SITE_URL + "meeting/%d/" % params['group'].id)
    else:
        response = render_mako_context(request, '403.html', kwargs)
    return response


@armor('GET', 'json')
def get_item_by_category(request, **kwargs):
    params = get_item_by_category_params(request, kwargs['me'])

    if params['success']:
        params['me'] = kwargs['me']
        data = params['category'].get_families(params['tp'])
        success = True
    else:
        data = []
        success = False

    info = 'Success' if success else u'获取失败'
    response = json.dumps({'success': success, 'info': info, 'data': data})
    return HttpResponse(response)


@armor('POST', 'json')
def category_change(request, **kwargs):
    params = get_category_change_params(request, kwargs['me'])

    if params['success']:
        params['me'] = kwargs['me']
        success = params['item'].change_category(params)
    else:
        success = False

    info = 'Success' if success else u'类别变更失败'
    response = json.dumps({'success': success, 'info': info})
    return HttpResponse(response)


@armor('POST', 'json')
def item_finish(request, **kwargs):
    params = get_item_tools_params(request, kwargs['me'])

    if params['success']:
        params['me'] = kwargs['me']
        success = params['item'].change_finish()
    else:
        success = False

    info = 'Success' if success else u'结项操作失败'
    response = json.dumps({'success': success, 'info': info})
    return HttpResponse(response)


@armor('POST', 'json')
def item_top(request, **kwargs):
    params = get_item_tools_params(request, kwargs['me'])
    if params['success']:
        params['me'] = kwargs['me']
        success = params['item'].change_top()
    else:
        success = False

    info = 'Success' if success else u'置顶操作失败'
    response = json.dumps({'success': success, 'info': info})
    return HttpResponse(response)


@armor('GET', 'json')
def get_item_and_record(request, **kwargs):
    params = get_item_and_record_params(request, kwargs['me'])

    if params['success']:
        data = params['item'].get_full_info()
        success = True
    else:
        data = {}
        success = False
    info = 'Success' if success else u'获取失败'
    response = json.dumps({'success': success, 'info': info, 'data': data})
    return HttpResponse(response)


@armor('POST', 'json')
def item_remove(request, **kwargs):
    params = get_item_tools_params(request, kwargs['me'])
    if params['success']:
        params['me'] = kwargs['me']
        success = params['item'].remove(params)
    else:
        success = False

    info = 'Success' if success else u'删除操作失败'
    response = json.dumps({'success': success, 'info': info})
    return HttpResponse(response)
