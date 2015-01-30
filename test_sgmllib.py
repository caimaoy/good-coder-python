# -*- coding: UTF-8 -*-

'''
Last modified time: 2014-09-29 16:48:00
Edit time: 2014-09-29 16:48:52
File name: test_sgmllib.py
Edit by caimaoy
'''

import re
import urllib
import urlparse
import PyV8
from sgmllib import SGMLParser
from bs4 import BeautifulSoup
class URLLister(SGMLParser):
    urls = []
    def start_a(self, attrs):
        href = [v for k, v in attrs if k=='href']
        if href:
            self.urls.extend(href)


def __test__():
    # url = r'http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000/'
    url = r'http://cq02-spi-ssd2p-bak10.cq02.baidu.com:8000'
    dic = urlparse.urlparse(url)
    '''
    ParseResult(scheme='http', netloc='cq02-spi-ssd2p-bak10.cq02.baidu.com:8000', pa
    th='/', params='', query='', fragment='')
    '''
    scheme, netloc, path, params, query, fragment = dic.scheme, dic.netloc, dic.path, dic.params, dic.query, dic.fragment

    # print type(dic)
    # print dic
    data = urllib.urlopen(url).read()

    ctxt = PyV8.JSContext()
    ctxt.enter()
    # data = ctxt.eval(data)


    # print data
    l = URLLister()
    l.feed(data)
    soup = BeautifulSoup(data)
    for link in soup.find_all('a'):
        # print 'from bs4'
        print link
        href = link.get('href')
        print href
        if re.match(re.compile(r'javascript:.*'), href):
            href = re.search(r'javascript:(.*)', href)
            print 'href is: '
            href = href.groups()[0]
            print href
            try:
                print ctxt.eval(href)
            except Exception as e:
                print e
    # print l.urls
    '''
    for i in l.urls:
        # print i
        print '-' * 80
        path = i
        new_url = urlparse.urlunparse((scheme, netloc, path, params, query, fragment))
        print new_url
        data = urllib.urlopen(new_url).read()
        print data
        print '-' * 80
    '''


if __name__ == '__main__':
    __test__()
