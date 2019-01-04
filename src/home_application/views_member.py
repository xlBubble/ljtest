# -*- coding: utf-8 -*-
import json

from django.http import HttpResponseRedirect, HttpResponse

from common.mymako import render_mako_context
from lib import (
    armor, get_group_params, get_host_params, get_host_next_params, get_get_groups_params, get_get_group_params,
    get_group_remove_params
)
from models import Group, Member
from settings import SITE_URL


@armor('POST', 'html')
def group_save(request, **kwargs):
    params = get_group_params(request)
    group = None

    if params['success']:
        params['me'] = kwargs['me']
        # Make Modify
        group = Group.modify(params)

    if isinstance(group, Group):
        # new one and enter it
        response = HttpResponseRedirect(SITE_URL + "meeting/%d/" % group.id)
    else:
        response = render_mako_context(request, '403.html', kwargs)
    return response


@armor('POST', 'json')
def host_save(request, **kwargs):
    params = get_host_params(request, kwargs['me'])

    if params['success']:
        params['group'].host.modify(params['order'], kwargs['me'])
        info = 'Success'
        success = True
    else:
        info = u'保存主持人失败'
        success = False
    response = json.dumps({'success': success, 'info': info})
    return HttpResponse(response)


@armor('POST', 'json')
def host_next(request, **kwargs):
    params = get_host_next_params(request, kwargs['me'])

    if params['success']:
        params['group'].host.cycle_host()
        info = 'Success'
        success = True
    else:
        info = u'主持人轮转失败'
        success = False
    response = json.dumps({'success': success, 'info': info})
    return HttpResponse(response)


@armor('GET', 'json')
def get_groups(request, **kwargs):
    params = get_get_groups_params(request)

    if params['success']:
        data = kwargs['me'].get_groups_as_manager(params)
    else:
        data = {
            'total_count': 0,
            'data': []
        }

    response = json.dumps(data)
    return HttpResponse(response)


@armor('GET', 'json')
def get_group(request, **kwargs):
    params = get_get_group_params(request, kwargs['me'])

    if params['success']:
        group = params['group']
        data = {
            'name': group.name,
            'group_id': group.id,
            'manager': [m.username for m in group.manager.filter(isActive=True) or []],
            'member': [m.username for m in group.member.filter(isActive=True) or []],
            'focus': [m.username for m in group.focus.filter(isActive=True) or []],
        }
        success = True
    else:
        data = {}
        success = False

    response = json.dumps({'success': success, 'data': data})
    return HttpResponse(response)


@armor('POST', 'json')
def group_remove(request, **kwargs):
    params = get_group_remove_params(request, kwargs['me'])

    if params['success']:
        group = params['group']
        group.remove()
        success = True
    else:
        success = False

    info = 'Success' if success else u'注销失败'

    response = json.dumps({'success': success, 'info': info})
    return HttpResponse(response)
