#!/usr/bin/env python
# -*- coding: utf-8 -*-

from agent.api.qualityplatform import QualityPlatform
from agent.api.grand import GrandClient

if __name__ == '__main__':
    qualityplatform_client = QualityPlatform('alta')
    grand_client = GrandClient()
    app = grand_client.get_latest_app('me.ele', 'Android', 'Release')
    # server_api.send_mail(
    #     ["waimai.qa.platform@ele.me", "waimai.mobile.platform@ele.me", "waimai.qa@ele.me", "hongbo.tang@ele.me"],
    #     'testin报告', '饿了么android_兼容性测试_testin', app,
    #     'https://www.testin.cn/s/32e18167',
    #     'test_report.html')
    qualityplatform_client.send_mail(["waimai.qa.platform@ele.me", "waimai.mobile.platform@ele.me", "waimai.qa@ele.me", "hongbo.tang@ele.me"],
                         '阿里云测报告_Top10机型', 'Android_兼容性测试_Top10机型', app,
                         'https://mqc.aliyun.com/report.htm?executionId=422374&shareCode=BARKybjw4DrI',
                         'test_report.html')

    # qualityplatform_client.send_mail(["weiyu.li@ele.me", "waimai.qa.platform@ele.me", "waimai.qa@ele.me"],
    #                                  'UI自动化测试报告', 'Android_UI自动化_BVT', app,
    #                                  'http://10.12.38.246:7070/view/UI%E8%87%AA%E5%8A%A8%E5%8C%96/job/hulk_WTK0217124000280/114/allure/',
    #                                  'test_report.html')
    # mail_content = 'No crash happened'
    # test_results = {
    #     'results': [
    #         {
    #             "case_id": 1138945,
    #             "comment": mail_content
    #         }
    #     ]
    # }
    # server_api.add_results_for_cases(636070, test_results)
    # mail_content = 'No crash happened'
    # comment = {
    #     "app_name": 'me.ele',
    #     "app_version": '7.24',
    #     "commit_id": 'asdasdas',
    #     "download_url": 'asdasdasd',
    #     "log": mail_content,
    #     "package_type": 'Release',
    #     "platform": 'Android',
    # }
    # test_results = {
    #     'results': [
    #         {
    #             "case_id": 1138945,
    #             "comment": json.dumps(comment)
    #         }
    #     ]
    # }
    # server_api.add_results_for_cases(636489, test_results)
    # oneday = timedelta(days=1)
    # day = datetime.now() - oneday
    # date_from = datetime(day.year, day.month, day.day, 0, 0, 0)
    # query_date = int(time.mktime(time.strptime(str(date_from), '%Y-%m-%d %H:%M:%S')))
    # # print(int(time.time()))
    # print query_date
