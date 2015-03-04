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
import copy
import os
import Queue
import re
import threading
import urlparse
import urllib2

from time import sleep
from docopt2 import docopt
from bs4 import BeautifulSoup as bs

import log

logger = log.init_log(r'./log/mini_spider.log')


def trans_url(s):
    # TODO rebuild
    reg = r'[/|\\|:|?|<|>|"|\*|\|]'
    s = re.sub(reg, '_', s)
    return s


def download_file_to_local(url, filename, timeout=1):
    """download file from url

    :url: just url download file from url
    :filename: download fiile to filename
    :returns: TODO

    """
    data = None
    try:
        f = urllib2.urlopen(url, timeout=timeout)
        data = f.read()
    except Exception as e:
        logger.error('%s error', url)
        logger.error(e)

    if data:
        with open(filename, 'wb') as code:
            code.write(data)


class ThredPoolThread(threading.Thread):
    """线程池中的线程类"""

    def __init__(self, queue, pool, queue_lock):
        """初始化线程池

        :queue 消息队列
        :pool 线程池
        :queue_lock 消息队列锁

        """
        super(ThredPoolThread, self).__init__()
        self.task_queue = queue
        self.isbusy = False
        self.pool = pool
        self.queue_lock = queue_lock

    def task_status(self):
        """判断任务是否结束

        结束条件为队列为空，而且线程都处于非工作状态

        :return 任务是否结束

        """
        ret = ''
        if self.task_queue.empty():
            set_isbusy = set([i.isbusy for i in self.pool])
            if True in set_isbusy:
                ret = 'continue'
            else:
                ret = 'finished'
        else:
            ret = 'has_task'
        return ret

    def run(self):
        """多线程调用函数"""

        while True:
            self.queue_lock.acquire()
            task_st = self.task_status()
            if task_st == 'finished':
                self.queue_lock.release()
                break
            elif task_st == 'continue':
                self.queue_lock.release()
                continue
            elif task_st == 'has_task':
                self.isbusy = True
                msg = self.task_queue.get_nowait()
                self.queue_lock.release()

                try:
                    msg.run()
                except Exception as e:
                    logger.error(e)
                    '''
                    logger.debug('msg is DownloadWorker')
                    logger.debug('msg.url is %s' % msg.url)
                    logger.debug('the id of msg is %s' % id(msg))
                    '''
                self.isbusy = False


class ThreadPool(object):

    """线程池类"""

    def __init__(self, thread_class, number_of_thrads_in_pool=8):
        """线程池初始化

        :thread_class: 线程池中的线程类
        :number_of_thrads_in_pool: 线程个数
        """

        self.task_queue = Queue.Queue()
        self.number = number_of_thrads_in_pool
        self.thread_class = thread_class
        self._pool = []
        self.queue_lock = threading.Lock()

    def make_and_start_thread_pool(self):
        """创建并且启动线程池线程

        :returns: TODO

        """
        for i in range(self.number):
            logger.debug('starting the NO.%s thread.' % i)
            new_thread = self.thread_class(
                queue=self.task_queue,
                pool=self._pool,
                queue_lock=self.queue_lock
            )
            self._pool.append(new_thread)
            new_thread.start()

    '''
    def stop_and_free_thread_pool(self):
        """暂停并释放所有线程池中线程

        :returns: TODO

        """
        for i in range(len(self._pool)):
            self.request_work(None, 'stop')

        for existring_thread in self._pool:
            existring_thread.join()

        del self._pool[:]

    def request_work(self, data, command='process'):
        self.task_queue.put(command, data)

    def get_task_queue(self):
        return self.task_queue

    def is_task_queue_empty(self):
        return self.empty()
    '''

    def wait_all(self):
        for i in self._pool:
            i.join()


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
        self.pool = ThreadPool(ThredPoolThread, 8)
        DownloadWorker.task = self.pool.task_queue
        self._init()

    def _init(self):
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
            raise AttributeError('sth error with config_file')

        self.read_url_file()

    def read_url_file(self):
        try:
            url_f = open(self.url_list_file)
            for u in url_f:
                worker = DownloadWorker(
                    u,
                    self.output_directory,
                    self.target_url,
                    0,
                    int(self.max_depth),
                    int(self.crawl_timeout),
                    int(self.crawl_interval)
                )
                DownloadWorker.add_queue(worker)
        except Exception as e:
            logger.error(e)
            raise IOError('sth error with url_list_file')

    def run(self):
        self.pool.make_and_start_thread_pool()
        self.pool.wait_all()
        logger.debug(u'任务完成，优雅的退出了...')


class DownloadWorker(object):
    """下载类
    """

    task = Queue.Queue()
    task_done = set()
    mkdir_lock = threading.Lock()

    @staticmethod
    def add_queue(t):
        """add msg to DownloadWorker.task which is a queue

        :t: DownloadWorker inistance
        :returns: None

        """
        DownloadWorker.task.put(t)

    def __init__(
        self,
        url,
        out_put_dir,
        reg,
        depth,
        max_depth,
        timeout,
        interval
    ):
        """下载类初始化

        :url: 现在正在爬取的url
        :out_put_dir: 爬取文件输出文件夹
        :reg: 爬取的正则表达式
        :depth: 现在所处的爬取深度
        :max_depth: 需要爬取的最大深度
        :timeout: 超时时间
        :interval: 间隔时间

        """

        self.out_put_dir = out_put_dir
        self.url = url
        self.reg = reg  # 使用re.compile对象不能clone
        self.max_depth = max_depth
        self.depth = depth
        self.timeout = timeout
        self.__MAX_LENTH = 200
        self.dir_lenth = len(os.path.abspath(self.out_put_dir))
        self.__MAX_FILE_NAME_LENTH = self.__MAX_LENTH - self.dir_lenth - 1
        self.interval = interval

    def clone(self):
        """克隆方法实现prototype

        :returns: 实例的深拷贝

        """
        return copy.deepcopy(self)

    def url_to_localfile(self, url):
        """url 转换为 本地文件名

        :url: url地址
        :returns: 返回转换后的地址

        """
        trsurl = trans_url(url)
        trsurl = trsurl[-self.__MAX_FILE_NAME_LENTH:]
        return trsurl

    def download_file(self, url):
        """下载文件到制定目录

        :url: 需要下载的文件url
        :returns: None

        """
        logger.debug('donwloading %s ...' % url)
        # logger.debug('self.out_put_dir is %s', self.out_put_dir)
        if not os.path.exists(self.out_put_dir):
            logger.debug('self.out_put_dir is %s', self.out_put_dir)
            os.mkdir(self.out_put_dir)
        trsurl = self.url_to_localfile(url)
        local_file = os.path.join(self.out_put_dir, trsurl)
        if os.path.exists(local_file):
            logger.debug('%s exists' % local_file)
        else:
            # logger.debug('local_file is %s' % local_file)
            # logger.debug('len(local_file) is %s' % str(len(local_file)))
            download_file_to_local(url, local_file, self.timeout)

    def get_url_text(self):
        """获取url的内容
        函数内捕捉异常

        :returns: url的内容，错误返回None

        """
        req = urllib2.Request(self.url)
        try:
            ret = urllib2.urlopen(req, timeout=self.timeout)
        except urllib2.URLError as e:
            logger.error('%s has error' % self.url)
            if hasattr(e, 'code'):
                logger.error('The server couldn\'t fulfill the request.')
                logger.error('Error code: %s' % e.code)
            elif hasattr(e, 'reason'):
                logger.error('We failed to reach a server.')
                logger.error('Reason: %s' % e.reason)
            else:
                logger.error('No exception was raised.')
            return None
        except Exception as e:
            logger.error('%s has error' % self.url)
            logger.error('Error: %s', e)
            return None

        text = ''
        try:
            text = ret.read()
        except Exception as e:
            logger.error('Error: %s', e)
            return None
        return text

    def find_all_href(self):
        """查询所有的超链接，下载或者加入队列继续爬

        :returns: None

        """

        DownloadWorker.task_done.add(self.url)
        logger.debug('%s is being crawled now...' % self.url)

        text = self.get_url_text()
        if text is None:
            return

        soup = bs(text)
        hrefs = []

        self.findall_reg(text)

        for link in soup('a'):
            href = link.get('href')
            hrefs.append(href)
        ret = []

        # html_reg = re.compile(r'http.*html')
        html_reg = re.compile(r'http')

        for i in hrefs:
            if i is not None and i.endswith('html'):
                if re.match(html_reg, i):
                    ret.append(i)
                else:
                    urljoined = urlparse.urljoin(self.url, i)
                    ret.append(urljoined)
                    # logger.debug('url is %s' % self.url)
                    # logger.debug('i is %s' % i)
                    # logger.debug('urljoined is %s' % urljoined)

        for i in ret:
            if (i not in DownloadWorker.task_done and
                    self.depth + 1 < self.max_depth):
                '''
                logger.debug('depth is %s', self.depth)
                logger.debug('max_depth is %s', self.max_depth)
                logger.debug('self.out_put_dir is %s', self.out_put_dir)
                logger.debug('now url is %s', self.url)
                logger.debug('task_done is %s' % DownloadWorker.task_done)
                '''
                # 克隆下载配置，修改depth 和 url
                cl = self.clone()
                cl.depth = cl.depth + 1
                cl.url = i
                DownloadWorker.task.put(cl)

                # logger.debug('clone is %s', cl)
                # logger.debug('id of self is %s', id(self))
                # logger.debug('id of clone is %s', id(cl))
                # DownloadWorker.task.put((i, depth + 1))
                # logger.debug('size is: %s' % DownloadWorker.task.qsize())
                # logger.debug('put %s' % i.encode('utf-8', 'ignore'))

    def run(self):
        # interval
        self.find_all_href()
        sleep(self.interval)

    def findall_reg(self, text):
        """下载html中的reg文件

        :text: html 内容，考虑传bs对象，为了复用传递text
        :returns: None

        """
        soup = bs(text)
        for img in soup('img'):
            src = img.get('src')

            if src is None:
                continue

            # replace \r\n
            src = src.replace('\r\n', '')
            res = re.match(self.reg, src)
            if res:
                src = res.group()
                url = self.create_download_url(src)
                self.download_file(url)

    def create_download_url(self, src):
        """生成现在的url地址

        :src: 原文URL中提取出的链接
        :returns: 根据判断绝对地址和相对地址给出最后的下载地址

        """
        url = ''
        if src.startswith('http:'):
            url = src
        elif src.startswith(r'//'):
            # TODO XXX BUG reg replace this
            url = src.replace(r'//', 'http://')
        else:
            url = urlparse.urljoin(self.url, src)
        return url

    def __str__(self):
        return ('self.url is %s\n, self.depth is %s\n' %
                (self.url, self.depth))


if __name__ == '__main__':
    arguments = docopt(__doc__, version='mini_spider 1.0')
    logger.debug(arguments)
    config_file = r'D:\caimaoy\good-coder-python\spider.conf'
    s = SpiderManager(config_file)
    s.run()
    '''
    # url = r'http://www.baidu.com/img/baidu_jgylogo3.gif?v=22596777.gif'
    # wrong_url = r'http://wwww.baidu.com/img/baidu_jgylogo3.gi=22596777.gif'
    # url = wrong_url
    # filename = 'test.gif'
    # donwload_file(url, filename)
    # s.download_file(url)
    # url = r'http://pycm.baidu.com:8081/'
    # url = r'http://www.baidu.com'
    # url = r'http://caixin.com'
    reg = r'.*\.(gif|png|jpg|bmp|html)$'
    d = DownloadWorker(url, './output', reg, 0, 4, 1)
    pool = ThreadPool(ThredPoolThread, 8)
    DownloadWorker.task = pool.task_queue
    DownloadWorker.task.put(d)
    pool.make_and_start_thread_pool()
    # d.find_all_href()
    # d.run()
    # text = u'http:\\//tiu.com/te_test/混沌战域-280-180_1423019686.jpg'
    # print trans_url(text)
    '''
