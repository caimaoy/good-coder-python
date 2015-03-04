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


class DownloadTest(unittest.TestCase):

    file_dir = os.path.dirname(os.path.abspath(__file__))
    fm = ''.join(['file:///', os.path.join(file_dir, 'test_download_file')])
    to = os.path.join(file_dir, 'test_download_file_to')

    # 初始化工作
    def setUp(self):
        pass

    # 退出清理工作
    def tearDown(self):
        os.remove(self.to)

    def test_download_file(self):
        mini.download_file_to_local(self.fm, self.to)
        self.assertTrue(os.path.exists(self.to))


if __name__ == '__main__':
    unittest.main()
