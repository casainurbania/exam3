# -*- coding: utf-8 -*-
import json
# TODO optimize import
from django.db.models import Q
from django.core import serializers

from account.decorators import login_exempt
from account.models import BkUser
from common.mymako import render_mako_context, render_json
from conf.default import APP_ID
from home_application.celery_tasks import *

from home_application.models import *
from home_application.utils.ESB import ESBApi, ESBComponentApi
import base64
import datetime, time

BIZ_MAP = {
    "2": "蓝鲸",
    "3": "考试用业务"
}


# 获取全部业务
def get_all_biz(req):
    print "=" * 100
    try:
        result = ESBApi(req).search_business()
        if result['message'] == 'success':
            biz_list = []
            for biz_info in result['data']['info']:
                biz_list.append({
                    'bk_biz_id': biz_info['bk_biz_id'],
                    'bk_biz_name': biz_info['bk_biz_name']
                })

            resp = {
                'result': True,
                'message': 'success',
                'data': biz_list,
            }

            return render_json(resp)

        else:
            return result

    except Exception as e:
        print e
        resp = {
            'result': False,
            'message': u'获取主机信息失败 %s' % e,
            'data': None,
        }

        return render_json(resp)


def get_operator_list(req):
    try:
        print "======get_operator_list======"
        operator_list = []
        for t in Template.objects.all():
            operator_list.append(t.operator)

        resp = {
            'result': True,
            'message': u'成功',
            'data': operator_list,
        }
    except Exception as e:
        resp = {
            'result': False,
            'message': u'获取操作者列表失败 %s' % e,
            'data': None,
        }

    return render_json(resp)


# def add_template(req):
#     try:
#         print "=========add"
#         bk_biz_id = req.POST["bk_biz_id"]
#         typ = req.POST["type"]
#         name = req.user.username
#
#         Template.objects.create(
#             bk_biz_id=bk_biz_id,
#             type=typ,
#             bk_biz_name=BIZ_MAP[bk_biz_id],
#             creator=name
#         ).save()
#
#         resp = {
#             'result': True,
#             'message': u'成功',
#             'data': None,
#         }
#     except Exception as e:
#         resp = {
#             'result': False,
#             'message': u' %s' % e,
#             'data': None,
#         }
#
#     return render_json(resp)
