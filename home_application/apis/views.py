# -*- coding: utf-8 -*-
import json
# TODO optimize import
import os

from django.db.models import Q
from django.core import serializers
from django.forms import model_to_dict
from django.http import StreamingHttpResponse, HttpResponse

from account.decorators import login_exempt
from account.models import BkUser
from common.mymako import render_mako_context, render_json
from conf.default import APP_ID, UPLOAD_DIR
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
                    'bk_biz_name': biz_info['bk_biz_name']
                })

            resp = {
                'result': True,
                'message': 'success',
                'data': biz_list,
            }

            return render_json(resp)
        else:
            resp = {
                'result': False,
                'message': '获取业务失败',
                'data': None,
            }

    except Exception as e:
        resp = {
            'result': False,
            'message': u'获取主机信息失败 %s' % e,
            'data': None,
        }

    return render_json(resp)


def add_template(req):
    try:
        bk_biz_name = req.POST["bk_biz_name"]
        typ = req.POST["type"]
        name = req.POST["name"]
        obj = req.FILES.get("file", None)

        pwd = os.getcwd()

        # father_path = os.path.abspath(os.path.dirname(pwd))
        save_path = os.path.join(pwd, UPLOAD_DIR, obj.name)
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
    bk_biz_name = req.POST.get("bk_biz_name", u"")
    typ = req.POST.get("type", u"")
    name = req.POST.get("name", u"")
    creator = req.POST.get("user", u"")
    q_set = Q()
    q_set.connector = 'AND'
    for k, v in {'bk_biz_name': bk_biz_name, 'type': typ, 'name': name, 'creator': creator}.items():
        if v is not u"":
            q_set.children.append((k, v))
    res = []
    for t in Template.objects.filter(q_set):
        res.append({
            'id':t.id,
            'name': t.name,
            'bk_biz_name': t.bk_biz_name,
            'type': t.type,
        })  # TODO 测试便是否可以遍历对每一个对象使用 model_to_dict  转化
    resp = {
        'result': True,
        'message': u'成功',
        'data': res,
    }
    return render_json(resp)


# 基于模板创建任务 todo
def create_task(req):
    try:
        name = req.POST['name']
        key = req.POST['key']
        creator = req.user.username
        tpl = Template.objects.get(name=name)
        path = tpl.file
        content = parse_excel(path)
        Task.objects.create(template=tpl, creator=creator, key=key, content=content, status="未操作")
        Task.objects.sync_operators(key=key)
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
    print res
    resp = {
        'result': True,
        'message': u'成功',
        'data': [i['bk_username'] for i in res['data']]
    }
    return render_json(resp)


# 下载示例模板文件
def download_sample_template(req):
    file_obj = open(r'upload/sample.xls', 'rb')
    response = StreamingHttpResponse(file_obj)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="sample.xls"'
    return response


# 下载指定模板文件
def download_template(req,id):
    file_path = Template.objects.get(id=id).file
    file_obj = open(file_path, 'rb')
    print file_path
    response = StreamingHttpResponse(file_obj)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="sample.xls"'
    return response


# 搜索任务
def search_task(req):
    bk_biz_name = req.GET.get('bk_biz_name', u'')
    typ = req.GET.get('type', u'')
    status = req.GET.get('status', u'')
    creator = req.GET.get('creator', u'')
    template_name = req.GET.get('template_name', u'')
    key = req.GET.get('key', u'')

    q_set = Q()
    q_set.connector = 'AND'
    for k, v in {'status': status, 'creator': creator, 'key': key, }.items():
        if v is not u"":
            q_set.children.append((k, v))
    res = Task.objects.filter(q_set)
    res_list = []
    if bk_biz_name is not u"":
        res = res.filter(template__bk_biz_name=bk_biz_name)
    if typ is not u"":
        res = res.filter(template__type=typ)
    if template_name is not u"":
        res = res.filter(template__name=template_name)

    for i in res:
        res_list.append({
            'name': i.template.name,
            'key': i.key,
            'bk_biz_name': i.template.bk_biz_name,
            'type': i.template.type,
            'operators': i.operators,
            'creator': i.creator,
            'create_time': '%s' % i.create_time,
            'status': i.status,
        })

    resp = {
        'result': True,
        'message': u'成功',
        'data': res_list
    }

    return render_json(resp)


# 查看任务详情
def get_task_content(req):
    key = req.GET.get('key')
    obj = Task.objects.get(key=key)
    task_contents = json.loads(obj.content)
    resp = {
        'result': True,
        'message': u'成功',
        'data': task_contents
    }
    return render_json(resp)


# 点击 确认  完成任务
def confirm(req):
    print "=======confirm========"
    index = int(req.POST["index"])
    key = req.POST["key"]
    obj = Task.objects.get(key=key)
    content = json.loads(obj.content)
    content[index]['done'] = 1
    content[index]['comfirm'] = req.user.username
    content[index]['time'] = time.strftime("%Y-%m-%d %H:%M:%S")
    obj.content = json.dumps(content)
    obj.save()
    resp = {
        'result': True,
        'message': u'成功',
        'data': content
    }
    return render_json(resp)


# 删除模板
def delete_template(req):
    print "=======delete_temp========"
    name = req.POST["name"]
    print name

    obj = Template.objects.get(name=name)
    os.remove(obj.file)
    obj.delete()
    resp = {
        'result': True,
    }
    return render_json(resp)
