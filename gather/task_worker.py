#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from baseQueue import QueueManagerClient
from multiprocessing import Process
import time, random, os
import requests

from dealUrl import deal_url_string, Vip

client = QueueManagerClient()(address=('47.89.54.152', 5000), authkey=b'secret')

print 'connect to queue...'
client.connect()


task = client.get_task_queue()
result = client.get_result_queue()

def deal_url(url):
    start = time.time()
    print 'Task begin'
    page = deal_url_string(url)
    vip = Vip(url, int(page))
    vip.doprocess()
    end = time.time()
    print 'Task %s runs %0.2f seconds.' % ('task use time', (end - start))

def get(url):
    start = time.time()
    try:
        requests.get(url)
    except:
        ok = 0
    else:
        ok = 1
    finally:
        rt = time.time() - start
        return {'ok': ok, 'rt': rt}

while True:
    if task.empty():
        print 'no task yet, wait 5s...'
        time.sleep(5)
        continue
    try:
        i = task.get(timeout=10)
        '''
        这里操作解析url, 查找商品，放入redis
        '''
        p = Process(target=deal_url, args=(format(i),))
        p.start()
        p.join()        
        o = get(i)
        #向resultQueue输出结果
        result.put({'i': i, 'o': o})
    except Exception, e:
        print 'Error: {0}'.format(e)