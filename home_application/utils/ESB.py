# -*- coding: utf-8 -*-

from conf.default import APP_ID, APP_TOKEN
from django.http.request import HttpRequest
from blueking.component.shortcuts import get_client_by_request, get_client_by_user
from blueking.component.client import ComponentClient
from home_application.models import *



class ESBApi(object):

    def __init__(self, param):
        if isinstance(param, HttpRequest):
            self.__client = get_client_by_request(param)  # 获取用户登陆态
            self.username = param.user.username
        else:
            self.__client = get_client_by_user(param)  # 获取到用户对象
            self.username = param
        self.__param = {
            "app_code": APP_ID,
            "app_secret": APP_TOKEN,
            'bk_username': self.username,
        }

    def get_app_by_user(self):
        try:
            param = self.__param
            self.__client.set_bk_api_ver('')
            result = self.__client.cc.get_app_by_user(param)
        except Exception, e:
            result = {'message': e}
        return result

    def search_host(self, biz_id, ip_list, page=None):
        try:
            if page is None:
                page = {"start": 0, "limit": 50}

            param = self.__param
            param['bk_biz_id'] = biz_id
            param['page'] = page

            if ip_list is not None:
                param["ip"] = {
                    "data": str(ip_list).split("\n"),
                    "exact": 1,
                    "flag": "bk_host_innerip"
                }
            result = self.__client.cc.search_host(param)
        except Exception, e:
            result = {'message': e}

        return result

    # 获取作业列表
    def get_job_list(self, bk_biz_id):
        try:
            param = self.__param
            param['bk_biz_id'] = bk_biz_id
            result = self.__client.job.get_job_list(param)
            return result
        except Exception, e:
            result = {'message': e}
            return result

    def search_business(self, start=0, limit=200, sort="bk_host_id"):
        try:
            param = self.__param
            param['start'] = start
            param['limit'] = limit
            param['sort'] = sort
            result = self.__client.cc.search_business(param)
            return result
        except Exception, e:
            result = {'message': e}
            return result


class ESBComponentApi(object):
    """
    不需要request参数的esb
    """

    def __init__(self):
        self.__param = {
            "app_code": APP_ID,
            "app_secret": APP_TOKEN,
            "bk_username": 'admin',
        }

        # common_args = {'bk_username': 'admin'}
        self.client = ComponentClient(
            # APP_ID 应用ID
            app_code=APP_ID,
            # APP_TOKEN 应用TOKEN
            app_secret=APP_TOKEN,
            # common_args=common_args
        )

    #  快速执行脚本
    def fast_execute_script(self, bk_biz_id=None, script_id=None, script_content=None, ip_list=None,
                            account=None, script_type=None, script_param='127.0.0.1', bk_username='admin'):
        if account is None:
            account = 'root'
        param = self.__param
        param["bk_username"] = bk_username
        param["bk_biz_id"] = bk_biz_id
        param["script_type"] = script_type
        if script_content is not None:
            param['script_content'] = script_content
        param["account"] = account
        _ip_list = [{"bk_cloud_id": "0", "ip": ip} for ip in ip_list]
        param["ip_list"] = _ip_list
        param['script_param'] = script_param
        result = self.client.job.fast_execute_script(param)

        return result

    # 获取脚本执行状态
    def get_job_instance_status(self, bk_biz_id, job_instance_id):
        """

        :param bk_biz_id:
        :param job_instance_id:
        :return:
                {
                  u'message': u'success',
                  u'code': 0,
                  u'data': [
                    {
                      u'status': 3,
                      u'step_results': [
                        {
                          u'tag': u'',
                          u'ip_logs': [
                            {
                              u'total_time': 0.276,
                              u'ip': u'192.168.51.77',
                              u'start_time': u'2019-04-09 12:49:24 +0800',
                              u'log_content': u'2019-04-09 12:49:24|7.23%|23%|0.00%\n',
                              u'exit_code': 0,
                              u'bk_cloud_id': 0,
                              u'retry_count': 0,
                              u'end_time': u'2019-04-09 12:49:24 +0800',
                              u'error_code': 0
                            }
                          ],
                          u'ip_status': 9
                        }
                      ],
                      u'is_finished': True,
                      u'step_instance_id': 80210,
                      u'name': u'API Quick execution script1554785364271'
                    }
                  ],
                  u'result': True,
                  u'request_id': u'2b1cf13890754dac80da111028db7327'
                }
        """

        param = {
            "bk_app_code": self.__param['app_code'],
            "bk_app_secret": self.__param['app_secret'],
            "bk_username": self.__param["bk_username"],
            "bk_biz_id": bk_biz_id,
            "job_instance_id": job_instance_id
        }

        resp = self.client.job.get_job_instance_log(param)

        return resp

    # 快速脚本执行结果
    def get_job_result(self, bk_biz_id, job_instance_id):
        """

        :param bk_biz_id:
        :param job_instance_id:
        :return:
        {
            "result": true,
            "code": 0,
            "message": "",
            "data": [
                {
                    "is_finished": true,
                    "step_instance_id": 90000,
                    "name": "test",
                    "status": 3,
                    "step_results": [
                        {
                            "ip_status": 9,
                            "tag": "xxx",
                            "ip_logs": [
                                {
                                    "retry_count": 0,
                                    "total_time": 60.599,
                                    "start_time": "2018-03-15 14:39:30 +0800",
                                    "end_time": "2018-03-15 14:40:31 +0800",
                                    "ip": "10.0.0.1",
                                    "bk_cloud_id": 0,
                                    "error_code": 0,
                                    "exit_code": 0,
                                    "log_content": "[2018-03-15 14:39:30][PID:56875] job_start\n"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        """
        param = {
            "bk_app_code": self.__param['app_code'],
            "bk_app_secret": self.__param['app_secret'],
            "bk_username": self.__param["bk_username"],
            "bk_biz_id": bk_biz_id,
            "job_instance_id": job_instance_id
        }
        resp = self.client.job.get_job_instance_log(param)
        return resp

    # 作业状态码: 1.未执行; 2.正在执行; 3.执行成功; 4.执行失败;
    # 5.跳过; 6.忽略错误; 7.等待用户; 8.手动结束; 9.状态异常;
    # 10.步骤强制终止中; 11.步骤强制终止成功; 12.步骤强制终止失败
