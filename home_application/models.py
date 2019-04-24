# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云(BlueKing) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
"""

from django.db import models
import time
import json
from home_application.utils.ex import parse_excel


class Template(models.Model):
    name = models.CharField(verbose_name="模板名称", max_length=64, unique=True)
    type = models.TextField(verbose_name="模板类型")
    # 变更发布  扩容类  上线类 下架类  例行维护
    # bk_biz_id = models.TextField(verbose_name="业务ID")
    bk_biz_name = models.TextField(verbose_name="业务名称")
    file = models.TextField(verbose_name="文件", blank=True, null=True)
    other = models.TextField(verbose_name="备注", blank=True, null=True)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, )
    creator = models.TextField(verbose_name="创建者", blank=True, null=True)
    change_time = models.DateTimeField(verbose_name="更新时间", auto_now=True, )
    changer = models.TextField(verbose_name="更新者", blank=True, null=True)
    objects = models.Manager()

    class Meta:
        db_table = 'saas_template'
        verbose_name = '模板表'
        verbose_name_plural = '模板表'


class TaskManager(models.Manager):
    # 根据任务现状,同步自身可操作者
    def sync_operators(self, key):
        obj = self.get(key=key)
        task_contents = json.loads(obj.content)
        operators = []
        uncomplate = 0
        completed = 0
        for content in task_contents:
            if content["done"]:
                completed += 1
            else:
                operators.append(content["operator"])
                uncomplate += 1
        if completed > 0:
            if uncomplate == 0:
                obj.status = "已完成"
            else:
                obj.status = "未完成"
        else:
            obj.status = "未操作"
        obj.operators = ",".join(list(set(operators)))
        obj.save()


class Task(models.Model):
    key = models.CharField(verbose_name="任务识别码", max_length=64, unique=True)
    content = models.TextField(verbose_name="详情", blank=True)
    status = models.TextField(verbose_name="状态", blank=True, null=True)
    # 未操作,操作中,已完成
    template = models.ForeignKey(Template)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, )
    change_time = models.DateTimeField(verbose_name="更新时间", auto_now=True, blank=True, null=True)
    operators = models.TextField(verbose_name="可操作人", blank=True, null=True)
    creator = models.TextField(verbose_name="创建者", blank=True, null=True)
    other = models.TextField(verbose_name="备注", blank=True, null=True)

    objects = TaskManager()

    class Meta:
        db_table = 'saas_task'
        verbose_name = '任务表'
        verbose_name_plural = '任务表'

# class Queue(models.Model):
#     ip = models.CharField(verbose_name="ip", max_length=30, primary_key=True)
#     bk_biz_id = models.CharField(verbose_name="业务ID", max_length=20)
#     status = models.IntegerField(verbose_name="状态", blank=True, null=True)
#     objects = models.Manager()
#
#     class Meta:
#         db_table = 'saas_queue'
#         verbose_name = 'celery周期队列'
#         verbose_name_plural = 'celery周期队列'
