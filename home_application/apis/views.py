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



def add_template(req):
    print "========= add_template ======="
    try:
        bk_biz_name = req.POST["bk_biz_name"]
        typ = req.POST["type"]
        name = req.POST["name"]
        obj = req.FILES.get("file", None)

        pwd = os.getcwd()

        # father_path = os.path.abspath(os.path.dirname(pwd))
        save_path = os.path.join(pwd, UPLOAD_DIR, obj.name)
        print save_path
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
    print "====== search_template_list ====="
    bk_biz_name = req.POST.get("bk_biz_name", u"")
    typ = req.POST.get("type", u"")
    name = req.POST.get("name", u"")
    creator = req.POST.get("user",u"")
    print bk_biz_name
    print typ
    print name
    print creator
    q_set = Q()
    q_set.connector = 'AND'
    for k, v in {'bk_biz_name': bk_biz_name, 'type': typ, 'name': name, 'creator': creator}.items():
        if v is not u"":
            q_set.children.append((k, v))
    res = []
    for t in Template.objects.filter(q_set):
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
    print res
    return render_json(resp)


# 创建任务 todo
def create_task(req):
    try:
        print "=======create_task====="
        name = req.POST['name']
        key = req.POST['key']
        creator = req.user.username
        tpl = Template.objects.get(name=name)
        Task.objects.create(creator=creator, key=key, template=tpl)
        resp = {
            'result': True,
            'message': u'成功',
            'data': None,
        }

    except Exception as e:
        resp = {
            'result': False,
            'message': u'失败: %s' % e,
            'data': None,
        }
    return render_json(resp)


# 获取全部用户
def get_all_user(req):
    res = ESBApi(req).get_all_users()
    res = {
        'result': True,
        'message': u'成功',
        'data': [i['bk_username'] for i in res['data']]
    }
    return render_json(res)
