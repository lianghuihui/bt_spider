# -*- coding: utf-8 -*-

import random
import time
import functools

import requests
from requests.exceptions import ReadTimeout, ConnectionError

import gevent
from gevent.pool import Pool as GPool

from pyquery import PyQuery as pq

from gevent import monkey
monkey.patch_socket()

def run_worker(url):

    def _crawl_deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            url = args[0]
            while True:
                try:
                    print "start._crawl_url.{}".format(url)
                    func(*args, **kw)
                    print "_crawl_url.success.{}".format(url)
                    return
                except (ReadTimeout, ConnectionError) as e:
                    print "_crawl_url.{}.timeout".format(url)
                    gevent.sleep(random.randint(1, 3))
        return wrapper

    def _parse_html(content):
        item_list = pq(content)(".item.cl")
        for item in item_list:
            item_q = pq(item)
            title = item_q("img:first").attr("alt")
            date = item_q("span:first").text()
            db_score = "".join([
                item_q(".rt:first strong").text(),
                ".",
                item_q(".rt:first em:last").text()])
            url = "www.bttiantang.com{}".format(item_q("a:first").attr("href"))

            if title and date and db_score:
                print "<===>{}<===>{}<===>{}<===>{}".format(
                        title.encode("utf8"),
                        date.encode("utf8"),
                        db_score.encode("utf8"),
                        url.encode("utf8"))

    @_crawl_deco
    def _crawl_url(url):
        respon = requests.get(url, timeout=3)
        if respon.ok:
            _parse_html(respon.content)

    _crawl_url(url)


if __name__ == '__main__':

    start_time = time.time()

    crawl_list = ( "http://www.bttiantang.com/?PageNo={}".format(i)
                 for i in range(1, 500) )

    g_pool = GPool(50)
    g_pool.map( run_worker, crawl_list )

    end_time = time.time()
    print "total cost {} sec.".format(end_time - start_time)

