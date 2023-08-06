#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    agent.worker.appcrawler
    ~~~~~~~~~~~~

    This module provide the appcrawler.

    :copyright: (c) 2017 by Ma Fei.
"""
import logging
import os
import subprocess

from bs4 import BeautifulSoup

import agent.util.file as file_tool
from agent.consts import TestRunStatus
from agent.qualityplatform import server_api
from agent.worker.base import BaseWorker

logger = logging.getLogger(__name__)

appcrawler_dir = file_tool.make_worker_dir(os.getcwd() + '/agent/')


class Appcrawler(BaseWorker):
    def __init__(self, data):
        super(Appcrawler, self).__init__(data)
        self.notice_account = self.data.get('notice_account')
        self.conf_url = self.data.get('fuss_hash')
        self.device_id = self.data.get('device_id')
        self.grand_id = self.data.get('grand_id')
        self.platform = self.data.get('platform')
        self.packtype = self.data.get('packtype')
        self.app_version = self.data.get('app_version')
        self.run_id = self.data.get('run_id')
        self.case_id = self.data.get('case_id')
        self.app = server_api.get_latest_app(self.grand_id, self.platform, self.packtype, self.app_version)

        os.chdir(appcrawler_dir)
        subprocess.call('git clone git@git.elenet.me:waimaiqa/appcrawler.git', shell=True)
        os.chdir(os.path.join(appcrawler_dir, 'appcrawler'))
        subprocess.call('git pull origin master', shell=True)

    def start_worker(self):
        if self.conf_url:
            file_tool.save_file(self.conf_url.encode('utf-8'), 'conf/', 'eleme.yaml')
        os.chdir(os.path.join(appcrawler_dir, 'appcrawler'))
        subprocess.call(
            'java -jar appcrawler-2.1.2.jar -c conf/eleme.yaml --capability udid=' + self.device_id + ' -a ' + self.app[
                'downloadURL'] + '-o' + os.path.join('/Users/mobile.test/eleme.qa/report/', str(self.task_id)),
            shell=True)
        fp = open(appcrawler_dir + "appcrawler/reports/index.html")
        soup = BeautifulSoup(fp, 'html.parser')
        fail_count = soup.select('#summary_view_row_1_legend_failed_count')[0].string
        if fail_count != '0':
            test_run_status = TestRunStatus.failed.value
        else:
            test_run_status = TestRunStatus.passed.value

        mail_content = 'http://10.12.38.246:8000/report/' + str(self.task_id) + '/index.html'

        if self.run_id:
            server_api.add_results_for_cases(self.run_id, self.case_id, mail_content, test_run_status, self.app)
        server_api.send_mail(self.notice_account, 'appcrawlerUI遍历报告', '饿了么android_稳定性测试_UI遍历', self.app,
                             mail_content, 'test_report.html')

        self.complete()
