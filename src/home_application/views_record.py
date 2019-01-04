# -*- coding: utf-8 -*-
import json

from django.http import HttpResponse

from lib import armor, get_record_params, get_record_remove_params
from models import Record


@armor('POST', 'json')
def record_save(request, **kwargs):
    params = get_record_params(request, kwargs['me'])

    if params['success']:

        params['me'] = kwargs['me']
        # Make Modify
        record = Record.modify(params)
        success = isinstance(record, Record)
    else:
        success = False

    info = 'Success' if success else u'保存操作失败'
    response = json.dumps({'success': success, 'info': info})
    return HttpResponse(response)


@armor('POST', 'json')
def record_remove(request, **kwargs):
    params = get_record_remove_params(request, kwargs['me'])

    if params['success']:

        params['me'] = kwargs['me']
        success = params['record'].remove(params)
    else:
        success = False

    info = 'Success' if success else u'删除操作失败'
    response = json.dumps({'success': success, 'info': info})
    return HttpResponse(response)
