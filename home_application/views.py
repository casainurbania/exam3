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

from common.mymako import render_mako_context, render_json


def test(req):
    a = req.GET.get("a")
    b = req.GET.get("b")
    resp = {
        "result": True,
        "message": "success",
        "data": {
            "a": a,
            "b": b,
        }
    }
    return render_json(resp)


# 主页面
def home(req):
    return render_mako_context(req, '/home.html', )


def template(req):
    return render_mako_context(req, '/template.html', )


def add(req):
    return render_mako_context(req, '/add.html')
