# -*- coding: utf-8 -*-

import random
import time
import functools
import multiprocessing

import requests
from requests.exceptions import ReadTimeout, ConnectionError

import gevent
from gevent.pool import Pool as GPool

from pyquery import PyQuery as pq

from gevent import monkey
monkey.patch_socket()

def run_worker(q):

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

            if title and date and db_score:
                print "<==title==>{}<==date==>{}<===score===>{}".format(
                        title.encode("utf8"),
                        date.encode("utf8"),
                        db_score.encode("utf8"))

    @_crawl_deco
    def _crawl_url(url):
        respon = requests.get(url, timeout=3)
        if respon.ok:
            _parse_html(respon.content)

    g_pool = GPool(20)
    while not q.empty():
        rst = q.get()
        g_pool.spawn(_crawl_url, rst).join()


if __name__ == '__main__':

    start_time = time.time()

    q = multiprocessing.Queue()
    map( q.put, ["http://www.bttiantang.com/?PageNo={}".format(i)
                 for i in range(1, 50)] )

    worker_count = 2 * multiprocessing.cpu_count() + 1
    workers = [multiprocessing.Process(target=run_worker, args=(q,))
               for i in range(worker_count) ]

    map( lambda worker: worker.start(), workers )
    map( lambda worker: worker.join(), workers )

    end_time = time.time()
    print "total cost {} sec.".format(end_time - start_time)

