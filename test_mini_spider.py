# -*- coding: UTF-8 -*-

'''
Last modified time: 2015-02-25 17:53:01
Edit time: 2015-02-25 17:53:25
File name: test_mini_spider.py
Edit by caimaoy
'''

__author__ = 'caimaoy'


import unittest
import mini_spider_rebuild as mini
import os
from httpretty import HTTPretty, httprettified


FILE_DIR = os.path.dirname(os.path.abspath(__file__))
class FuncTest(unittest.TestCase):

    # 初始化工作
    def setUp(self):
        pass

    # 退出清理工作
    def tearDown(self):
        pass

    def test_trans_url(self):
        inpt = r'/\:?<>"\*'
        outpt = r'_________'
        self.assertEqual(mini.trans_url(inpt), outpt, 'failed')
        self.assertEqual(mini.trans_url('1.+'), '1.+', 'failed')

'''
class DownloadTest(unittest.TestCase):

    fm = ''.join(['file:///', os.path.join(FILE_DIR, 'test_download_file')])
    to = os.path.join(FILE_DIR, 'test_download_file_to')

    # 初始化工作
    def setUp(self):
        pass

    # 退出清理工作
    def tearDown(self):
        if os.path.exists(self.to):
            os.remove(self.to)

    def test_download_file(self):
        mini.download_file_to_local(self.fm, self.to)
        self.assertTrue(os.path.exists(self.to))

    def test_error_url_(self):
        mini.download_file_to_local('error_url', self.to)

class DownloadWorkerTest(unittest.TestCase):

    fm = ''.join(['file:///', os.path.join(FILE_DIR, 'test_download_file')])
    to = os.path.join(FILE_DIR, 'test_download_file_to')

    # 初始化工作
    def setUp(self):
        pass

    # 退出清理工作
    def tearDown(self):
        pass

    @httprettified
    def test_get_url_text(self):
        HTTPretty.register_uri(HTTPretty.GET, 'http://www.test.com',
                               body='xxx')
        dw = mini.DownloadWorker('http://www.test.com', '.', 'reg', 0, 3, 1, 1)
        self.assertEqual(dw.get_url_text(), 'xxx')

    def test_create_download_url(self):
        dw = mini.DownloadWorker('http://www.test.com', '.', 'reg', 0, 3, 1, 1)
        test_fuc = dw.create_download_url
        test_dic = {
            r'http://xxx': 'http://xxx',
            r'//xxx': 'http://xxx',
            r'xxx': 'http://www.test.com/xxx',
        }
        for k in test_dic:
            self.assertEqual(test_fuc(k), test_dic[k])

    @httprettified
    def test_get_url_text_404(self):
        HTTPretty.register_uri(HTTPretty.GET, 'http://www.test.com',
                               body='',
                               status=404
                              )
        dw = mini.DownloadWorker('http://www.test.com', '.', 'reg', 0, 3, 1, 1)
        dw.get_url_text()

    def test_get_url_text_wrong_url(self):
        dw = mini.DownloadWorker('http://wrong.url.me', '.', 'reg', 0, 3, 1, 1)
        dw.get_url_text()

    def test_download_file(self):
        dw = mini.DownloadWorker('http://no.url.me', '.', 'reg', 0, 3, 1, 1)
        to = dw.url_to_localfile(self.fm)
        def del_file(to):
            if os.path.exists(to):
                os.remove(to)
        del_file(to)
        dw.download_file(self.fm)
        self.assertTrue(os.path.exists(dw.url_to_localfile(self.fm)))
        dw.download_file(self.fm)
        self.assertTrue(os.path.exists(dw.url_to_localfile(self.fm)))
        del_file(to)
        dw.find_all_href()


class SpiderManagerTest(unittest.TestCase):

    # 初始化工作
    def setUp(self):
        self.config_file = os.path.join(FILE_DIR, 'spider.conf')
        self.wrong_url_config = os.path.join(FILE_DIR, 'wrong_url.conf')

    # 退出清理工作
    def tearDown(self):
        pass

    def test_spidermanage_ini(self):
        mini.SpiderManager(self.config_file)
        self.assertRaises(
            AttributeError,
            mini.SpiderManager,
            'wrong_file'
        )
        self.assertRaises(
            IOError,
            mini.SpiderManager,
            self.wrong_url_config
        )

'''

if __name__ == '__main__':
    unittest.main()
