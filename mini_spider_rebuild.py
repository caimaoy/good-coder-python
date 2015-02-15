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
import string
import threading
import time
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


def trans_url(s):
    # TODO rebuild
    reg = r'[/|\\|:|?|<|>|"|\|]'
    s = re.sub(reg, '_', s)
    return s


def donwload_file_to_local(url, filename, timeout=1):
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
        logger.error(e)

    if data:
        with open(filename, 'wb') as code:
            code.write(data)

class ThredPoolThread(threading.Thread):
    """线程池中的线程类"""

    def __init__(self, queue, pool, queue_lock, log_lock):
        super(ThredPoolThread, self).__init__()
        self.task_queue = queue
        self.isbusy = False
        self.pool = pool
        self.queue_lock = queue_lock
        self.log_lock = log_lock
        print 'ThredPoolThread is init'


    def task_status(self):
        """判断任务是否结束

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
        # XXX
        while True:
            if self.isbusy is True:
                logger.debug('I am busy')
                pass
            else:
                self.queue_lock.acquire()
                task_st = self.task_status()
                logger.debug('task_st is %s' % task_st)
                time.sleep(1)
                if task_st == 'finished':
                    self.queue_lock.release()
                    break
                elif task_st == 'continue':
                    self.queue_lock.release()
                    continue
                elif task_st == 'has_task':
                    logger.debug('has_task')
                    self.isbusy = True
                    # command, item = self.task_queue.get_nowait()
                    msg = self.task_queue.get_nowait()
                    self.queue_lock.release()

                    if isinstance(msg, DownloadWorker):
                        logger.debug('msg is DownloadWorker')
                        logger.debug('msg.url is %s' % msg.url)
                        msg.run()
                    '''
                    if command == 'stop':
                        break
                    try:
                        time.sleep(1)
                        if command == 'process':
                            # TODO dotask
                            pass
                        else:
                            raise ValueError, 'Unknown command %r' % command
                    except Exception as e:
                        logger.error(e)
                    else:
                        # TODO put the new task here
                        pass
                    '''
                    self.isbusy = False


class TaskMassage(object):

    """消息队列中的消息类"""

    def __init__(self, func, *arg):
        """初始化消息队列

        :func: 调用的函数签名
        :*arg: 函数的参数
        :returns: None

        """
        self.func = func
        self.arg = arg

    def run(self):
        """执行消息队列行为

        :returns: self.func的执行结果

        """
        return self.func(list(self.arg))


class ThreadPool(object):

    """线程池类"""

    def __init__(self, thread_class, number_of_thrads_in_pool=8):
        """TODO: to be defined1. """

        self.task_queue = Queue.Queue()
        self.number = number_of_thrads_in_pool
        self.thread_class = thread_class
        self._pool = []
        self.queue_lock = threading.Lock()
        self.log_lock = threading.Lock()

    def make_and_start_thread_pool(self):
        """创建并且启动线程池线程

        :returns: TODO

        """
        logger.debug('make_and_start_thread_pool')
        for i in range(self.number):
            logger.debug('starting the NO.%s thread.' % i)
            new_thread = self.thread_class(
                queue=self.task_queue,
                pool=self._pool,
                queue_lock=self.queue_lock,
                log_lock=self.log_lock
            )
            self._pool.append(new_thread)
            new_thread.start()

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


class DownloadWorker(object):
    """下载类
    """
    # TODO 可能写成多线程

    task = Queue.Queue()
    task_done = []
    mkdir_lock = threading.Lock()

    def __init__(self, url, out_put_dir, reg, depth, max_depth, timeout):

        self.out_put_dir = out_put_dir
        self.url = url
        self.reg = reg #XXX re.compile(reg)
        self.max_depth = max_depth
        self.depth = depth
        self.timeout = timeout
        self.__MAX_LENTH = 200
        self.dir_lenth = len(os.path.abspath(self.out_put_dir))
        self.__MAX_FILE_NAME_LENTH = self.__MAX_LENTH - self.dir_lenth -1

        # DownloadWorker.task.put((url, depth))

    def clone(self):
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
        :returns: TODO

        """
        print 'donwloading %s ...' % url
        logger.debug('self.out_put_dir is %s', self.out_put_dir)
        if not os.path.exists(self.out_put_dir):
            logger.debug('self.out_put_dir is %s', self.out_put_dir)
            os.mkdir(self.out_put_dir)
        trsurl = self.url_to_localfile(url)
        local_file = os.path.join(self.out_put_dir, trsurl)
        if os.path.exists(local_file):
            logger.debug('%s exists' % local_file)
        else:
            logger.debug('local_file is %s' % local_file)
            logger.debug('len(local_file) is %s' % str(len(local_file)))
            donwload_file_to_local(url, local_file, self.timeout)

    def find_all_href(self):
        '''
        url, depth = DownloadWorker.task.get()
        self.depth = depth
        DownloadWorker.task_done.append(url)
        '''

        # print 'now url is ', self.url
        '''
        self.url = msg.url
        self.depth = msg.depth
        '''
        req = urllib2.Request(url)
        try:
            ret = urllib2.urlopen(req, timeout=self.timeout)
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
        except Exception as e:
            logger.error('Error: %s', e)
            return None

        try:
            text = ret.read()
        except Exception as e:
            # TODO 可能或有timeout 异常
            logger.error('Error: %s', e)
            return None
        soup = bs(text)
        hrefs = []

        self.findall_reg(text)

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
            if (i not in DownloadWorker.task_done and
                self.depth + 1 < self.max_depth):

                # print 'depth is ', self.depth
                # print 'max_depth is ', self.max_depth
                '''
                logger.debug('depth is %s', self.depth)
                logger.debug('max_depth is %s', self.max_depth)
                logger.debug('self.out_put_dir is %s', self.out_put_dir)
                logger.debug('now url is %s', self.url)
                '''

                cl = self.clone()
                cl.depth = cl.depth + 1
                cl.url = i

                # DownloadWorker.task.put((i, depth + 1))
                logger.debug('cl is %s', cl)
                DownloadWorker.task.put(cl)
                logger.debug('put %s' % i.encode('utf-8', 'ignore'))

    def run(self):
        # while not DownloadWorker.task.empty():
        self.find_all_href()

    def findall_reg(self, text):
        # XXX ooo
        soup = bs(text)
        for img in soup('img'):
            print img
            src = img.get('src')
            print '-' * 80
            logger.debug('src is %s' % src)
            print 'self.url is ', self.url
            if src is None:
                continue
            # res = self.reg.match(src)
            res = re.match(self.reg, src)
            print 'self.reg is ', self.reg
            if res:
                src = res.group()
            if src.startswith('http:'):
                url = src
            elif src.startswith(r'//'):
                # TODO XXX BUG reg replace this
                url = src.replace(r'//', 'http://')
            else:
                url = urlparse.urljoin(self.url, src)
            self.download_file(url)
            print '-' * 80

    def __str__(self):
        return ('self.url is %s\n, self.depth is %s\n' % (self.url, self.depth))


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
    # url = r'http://pycm.baidu.com:8081/'
    url = r'http://www.baidu.com'
    reg = r'.*\.(gif|png|jpg|bmp|html)$'
    d = DownloadWorker(url, './output', reg, 0, 4, 1)
    pool = ThreadPool(ThredPoolThread, 4)
    DownloadWorker.task = pool.task_queue
    DownloadWorker.task.put(d)
    pool.make_and_start_thread_pool()
    # d.find_all_href()
    # d.run()
    # text = u'http:\\//tieba.baidu.com/tb/cms/game_test/混沌战域-280-180_1423019686.jpg'
    # print trans_url(text)
