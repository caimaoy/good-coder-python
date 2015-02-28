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

class mytest(unittest.TestCase):

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

if __name__ == '__main__':
    unittest.main()
