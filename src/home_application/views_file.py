# -*- coding: utf-8 -*-
import json

from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.core.files import File

from lib import armor, get_file_put_params, get_file_get_params, readfile


@armor('POST', 'json')
def file_put(request, **kwargs):
    params = get_file_put_params(request, kwargs['me'])

    if params['success']:
        params['me'] = kwargs['me']
        cell = params['group'].put_file(params)
        data = {
            'id': cell.id,
            'name': cell.name,
            'ext': cell.name_ex
        }
        success = True
    else:
        data = {}
        success = False

    info = 'Success' if success else u'保存失败'

    response = json.dumps({'success': success, 'info': info, 'data': data})
    return HttpResponse(response)


@armor('GET', 'json')
def file_get(request, **kwargs):
    params = get_file_get_params(request, kwargs['me'])

    if params['success']:
        f = params['file']
        response = HttpResponse(f.content_new, content_type="application/octet-stream")
        response["Content-Disposition"] = "attachment; filename=%s" % smart_str(f.name)

    else:
        response = HttpResponse(json.dumps({'success': False, 'info': params['info']}))

    return response
