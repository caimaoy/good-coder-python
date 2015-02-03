# -*- coding: UTF-8 -*-

"""mini_spider

Usage:
    mini_spider.py (-h | --help)
    mini_spider.py (-v | --version)
    mini_spider.py [-c=<cf>]

Options:
    -h --help       Show this screen.
    -v --version    Show version.
    -c=<cf>         Config file[default: ./spider.conf]
"""

"""
Last modified time: 2014-09-12 17:15:07
Edit time: 2014-09-12 17:32:29
File name: mini_spider.py
Edit by caimaoy
"""

import ConfigParser
import os
import re
import string
import urlparse
import urllib2

from docopt2 import docopt
from bs4 import BeautifulSoup as bs
import log

logger = log.init_log(r'./log/mini_spider.log')

"""
config = ConfigParser.ConfigParser()
config.read('spider.conf')

print config.get('spider', 'url_list_file') # -> "Python is fun!"
print config.get('spider', 'thread_count') # -> "Python is fun!"
"""

def translator(frm='', to='', delete='', keep=None):
    """简化字符串translate方法使用，返回函数

    :frm: 要转化的字符
    :to: 目标字符
    :delete: 要删除的字符
    :keep: 要保留的字符
    :returns: 返回满足要求的函数

    """
    if len(to) == 1:
        to = to * len(frm)
    trans = string.maketrans(frm, to)
    if keep is not None:
        all_chars = string.maketrans('', '')
        delete = all_chars.translate(
            all_chars,
            keep.translate(all_chars, delete)
        )
    def translate(s):
        return s.translate(trans, delete)
    return translate


# 转义html特殊字符
trans_url = translator(frm=r'/\:?<>"|', to='_')


def donwload_file_to_local(url, filename):
    """download file from uri

    :uri: just uri download file from uri
    :filename: download fiile to filename
    :returns: TODO

    """
    print 'downloading with urllib2'
    f = urllib2.urlopen(url)
    try:
        data = f.read()
    except Exception as e:
        logger.error(e)

    with open(filename, 'wb') as code:
        code.write(data)


class SpiderManager(object):

    """爬虫管理管理器"""

    def __init__(self, config_file):
        """初始化

        :config_file: 配置文件

        """
        self._config_file = config_file
        self.url_list_file = r'./urls'
        self.output_directory = r'./output'
        self.max_depth = 1
        self.crawl_interval = 1
        self.crawl_timeout = 1
        self.target_url = r'.*\.(gif|png|jpg|bmp)$'
        self.thread_count = 8
        self._init()

    def _init(self):
        # import pdb; pdb.set_trace()
        config = ConfigParser.ConfigParser()
        config.read(self._config_file)

        v = [
            'url_list_file',
            'output_directory',
            'max_depth',
            'crawl_interval',
            'crawl_timeout',
            'target_url',
            'thread_count'
        ]
        try:
            for i in v:
                self.__setattr__(i, config.get('spider', i))
        except Exception as e:
            logger.error(e)


class DownlaodWorker(object):
    """下载类
    """
    # TODO 可能写成多线程

    import Queue
    task = Queue.Queue()
    task_done = []


    def __init__(self, url, out_put_dir, reg, depth, max_depth):
        self.out_put_dir = out_put_dir
        self.url = url
        self.reg = re.compile(reg)
        self.max_depth = max_depth
        self.depth = depth
        DownlaodWorker.task.put((url, depth))

    def download_file(self, url):
        """下载文件到制定目录

        :url: 需要下载的文件url
        :returns: TODO

        """
        if not os.path.exists(self.out_put_dir):
            os.mkdir(self.output_directory)
        local_file = os.path.join(self.out_put_dir, trans_url(url))
        if os.path.exists(local_file):
            logger.debug('%s exists' % local_file)
        else:
            donwload_file_to_local(url, local_file)

    def find_all_href(self):
        url, depth = DownlaodWorker.task.get()
        self.depth = depth
        DownlaodWorker.task_done.append(url)
        print 'now url is ', url
        req = urllib2.Request(url)
        try:
            ret = urllib2.urlopen(req)
        except urllib2.URLError as e:
            if hasattr(e, 'code'):
                logger.error('The server couldn\'t fulfill the request.')
                logger.error('Error code: %s' % e.code)
            elif hasattr(e, 'reason'):
                logger.error('We failed to reach a server.')
                logger.error('Reason: %s' % e.reason)
            else:
                logger.error('No exception was raised.')
            return None

        text = ret.read()
        soup = bs(text)
        hrefs = []
        for link in soup('a'):
            # print link
            href = link.get('href')
            # print href
            hrefs.append(href)
            '''
            if self.reg.match(href):
                print href, 'match'
            '''
        ret = []
        for i in hrefs:
            if i is not None:
                if re.match(r'http:', i):
                    ret.append(i)
                else:
                    ret.append(urlparse.urljoin(url, i))

        for i in ret:
            if (not i in DownlaodWorker.task_done and
                self.depth + 1 < self.max_depth):

                print 'depth is ', self.depth
                print 'max_depth is ', self.max_depth

                # import pdb; pdb.set_trace()
                DownlaodWorker.task.put((i, depth + 1))
                print 'put', i

    def run(self):
        while not DownlaodWorker.task.empty():
            self.find_all_href()


if __name__ == '__main__':
    arguments = docopt(__doc__, version='mini_spider 1.0')
    logger.debug(arguments)
    '''
    with open(arguments['-c'], 'r') as f:
        for i in f:
            logger.debug('url is %s' % i)
    '''
    config_file = r'D:\caimaoy\good-coder-python\spider.conf'
    s = SpiderManager(config_file)
    url = r'http://www.baidu.com/img/baidu_jgylogo3.gif?v=22596777.gif'
    # wrong_url = r'http://wwww.baidu.com/img/baidu_jgylogo3.gif?v=22596777.gif'
    # url = wrong_url
    # filename = 'test.gif'
    # donwload_file(url, filename)
    # s.download_file(url)
    url = r'http://pycm.baidu.com:8081/'
    reg = r'.*\.(gif|png|jpg|bmp|html)$'
    d = DownlaodWorker(url, './output', reg, 0, 8)
    # d.find_all_href()
    d.run()
