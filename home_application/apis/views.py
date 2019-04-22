# -*- coding: utf-8 -*-
import json
# TODO optimize import
import os

from django.db.models import Q
from django.core import serializers

from account.decorators import login_exempt
from account.models import BkUser
from common.mymako import render_mako_context, render_json
from conf.default import APP_ID, UPLOAD_PATH
from home_application.celery_tasks import *
from home_application.models import *
from home_application.models import *
from home_application.utils.ESB import ESBApi, ESBComponentApi
import base64
import datetime, time


# 获取全部业务
def get_all_biz(req):
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


def add_template(req):
    print "========= add_template ======="
    try:
        bk_biz_name = req.POST["bk_biz_name"]
        typ = req.POST["type"]
        name = req.POST["name"]
        obj = req.FILES.get("file", None)

        print ">" * 100
        print obj.name
        save_path = os.path.join(UPLOAD_PATH, obj.name)
        print [t.file for t in Template.objects.all()]
        if save_path not in [t.file for t in Template.objects.all()]:
            f = open(save_path, 'wb')
            for line in obj.chunks():
                f.write(line)
            f.close()
            Template.objects.create(
                bk_biz_name=bk_biz_name,
                type=typ,
                name=name,
                file=save_path
            ).save()
            print ">" * 100, 'saved'
            resp = {
                'result': True,
                'message': u'插入成功',
                'data': None,
            }
        else:
            resp = {
                'result': False,
                'message': u'该文件名已存在',
                'data': None,
            }

    except Exception as e:
        resp = {
            'result': False,
            'message': u' %s' % e,
            'data': None,
        }
        if e[0] == 1062:
            resp['message'] = "模板名已存在"

    return render_json(resp)


def search_template_list(req):
    print "======search====="
    bk_biz_name = req.POST.get("bk_biz_name", u"")
    typ = req.POST.get("type", u"")
    name = req.POST.get("name", u"")
    Q_set = Q()
    Q_set.connector = 'AND'
    for k, v in {'bk_biz_name': bk_biz_name, 'type': typ, 'name': name}.items():
        if v is not u"":
            Q_set.children.append((k, v))
    res = []
    for t in Template.objects.filter(Q_set):
        res.append({
            'name': t.name,
            'bk_biz_name': t.bk_biz_name,
            'type': t.type,
        })
    resp = {
        'result': True,
        'message': u'成功',
        'data': res,
    }
    return render_json(resp)


def create_task(req):
    id = req.POST['id']
    creator = req.user.username
    Task.objects.create()


def get_all_user(req):
    res = ESBApi(req).get_all_users()
    print [i['bk_username'] for i in res['data']]
    res = {
        'result': True,
        'message': u'成功',
        'data': [i['bk_username'] for i in res['data']]
    }
    return render_json(res)
