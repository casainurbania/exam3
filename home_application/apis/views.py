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
    "2":"蓝鲸",
    "3":"考试用业务"
}

# 获取主机
def get_hosts(req):
    bk_biz_id = req.POST.get("bk_biz_id", None)
    ip_list = req.POST.get("ip_list", None)
    if ip_list is not None:
        ip_list = ip_list.split(",")
    try:
        result = ESBApi(req).search_host(biz_id=bk_biz_id, ip_list=ip_list)
        if result['message'] == 'success':
            host_list = []
            for host in result["data"]["info"]:
                # assemble cloud list
                # cloud_list = []
                # for cloud_info in host["host"]["bk_cloud_id"]:
                #     cloud_list.append(cloud_info["id"])
                #     _cloud_id_list.append(cloud_id["id"])
                host_list.append(
                    {
                        "ip": host["host"]["bk_host_innerip"],
                        "os": host["host"]["bk_os_name"] + " " + host["host"]["bk_os_bit"],
                        "cloud": host["host"]["bk_cloud_id"][0]["id"],
                        "name": host["host"]["bk_host_name"]
                    }
                )
            resp = {
                'result': True,
                'message': 'success',
                'data': host_list,
            }
        else:
            resp = result
    except Exception as e:
        resp = {
            'result': False,
            'message': u'获取主机信息失败 %s' % e,
            'data': None,
        }

    return render_json(resp)


# 获取全部业务
def get_all_biz(req):
    print "="*100
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

def get_opt_list(req):
    try:
        print "=========opt_list"
        opt_list = []
        for t in Task.objects.all():
            opt_list.append(t.template.creator)

        resp = {
            'result': True,
            'message': u'成功',
            'data': opt_list,
        }
    except Exception as e:
        resp = {
            'result': False,
            'message': u'获取操作者列表失败 %s' % e ,
            'data': None,
        }

    return render_json(resp)


def add_template(req):
    try:
        print "=========add"
        bk_biz_id = req.POST["bk_biz_id"]
        typ = req.POST["type"]
        name = req.user.username

        Template.objects.create(
            bk_biz_id=bk_biz_id,
            type=typ,
            bk_biz_name=BIZ_MAP[bk_biz_id],
            creator=name
        ).save()

        resp = {
            'result': True,
            'message': u'成功',
            'data': None,
        }
    except Exception as e:
        resp = {
            'result': False,
            'message': u' %s' % e ,
            'data': None,
        }

    return render_json(resp)

# # 快速执行脚本
# def exec_script(req):
#     bk_biz_id = req.POST.get("bk_biz_id", None)
#     ip_list = str(req.POST.get("ip_list", "")).split(",")
#     # script_content =
#     script_param = req.POST.get("script_param", None)
#     res = sync_exec_script(
#         bk_biz_id=bk_biz_id,
#         ip_list=ip_list,
#         script_content=SCRIPT_CONTENT,
#         script_param=SCRIPT_PARAM)
#     return res


# 添加到周期列表
#
# def queue_push(req):
#     try:
#         bk_biz_id = req.POST["bk_biz_id"]
#         ip = req.POST["ip"]
#         Queue.objects.create(ip=ip, bk_biz_id=bk_biz_id).save()
#         print "====== 已推入queue ======="
#     except Exception as e:
#         print e
#
#     return render_json({
#         'result': True,
#     })
#
#
# # 从周期列表中移除
# def queue_remove(req):
#     try:
#         ip = req.POST['ip']
#         Queue.objects.get(ip=ip).delete()
#         print "====== 已从queue删除 ======="
#     except Exception as e:
#         print e
#     return render_json({
#         'result': True,
#     })
#
#
# def chart_api(req, ip):
#     """
#     :param req:
#     :return: {
#                     "code":0,
#                     "result": true,
#                     "messge":"success",
#                     "data": {
#                         "series":[{
#                             "color": "#f9ce1d",
#                             "name":"项目一",
#                             "data": [200, 180, 190, 150, 125, 76, 135, 162, 32, 20, 6, 3]
#                         }],
#                         "categories": ["07:10", "07:10", "07:10", "07:10", "07:10", "07:10", "07:10", "07:10", "07:10", "07:10", "07:10", "07:10"]
#                     }
#                 }
#     """
#
#     res_set = Prof.objects.filter(time__gte=datetime.datetime.now() - datetime.timedelta(hours=1))
#
#     resp = {
#         "code": 0,
#         "result": True,
#         "messge": "success",
#         "data": {
#             "series": [{
#                 "color": "#f9ce1d",
#                 "name": ip,
#                 "data": [float(i.content.split("\n")[6].split(":")[1]) for i in res_set]  # TODO 此处根据需要自行对结果内容做处理
#             }],
#             "categories": [str(i.time) for i in res_set]
#         }
#
#     }
#
#     return render_json(resp)
