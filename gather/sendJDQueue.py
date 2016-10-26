#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from baseQueue import QueueManagerClient
from multiprocessing import Process
import time, random, os
import requests
from bs4 import BeautifulSoup
import os, time, urllib2,logging, sys, math
client = QueueManagerClient()(address=('47.89.54.152', 5000), authkey=b'secret')
client.connect()
task = client.get_task_queue()
n = 10
L_list = ['https://www.amazon.cn/b/ref=sr_aj?node=1454115071&ajr=0'];
def deal_url(url):
    start = time.time()
    print 'Task begin'
    page = deal_url_string(url)
    end = time.time()
    print 'Task %s runs %0.2f seconds.' % ('task use time', (end - start))


def deal_url_string(new_url):
	page = urllib2.urlopen(new_url).read()
	soup = BeautifulSoup(page, "html.parser")
	item = soup.find_all(class_="s-result-item")
	for x in item:
		item_href = x.find(class_="a-section")
		href = item_href.find('a').get('href')
		print('Put task %s...' % href)
 		task.put(href)


while L_list[-1]:
	p = L_list[-1]
	page = urllib2.urlopen(p).read()
	soup = BeautifulSoup(page, "html.parser")
	item = soup.find(class_="pagnRA")
	href = item.find('a').get('href')
	p = Process(target=deal_url, args=(format(L_list[-1]),))
 	p.start()
 	p.join()
 	href = 'https://www.amazon.cn'+href
 	L_list.append(href)


# for i in range(1, 203):
# 	u = 'http://list.jd.com/list.html?cat=9192,9193,9201&page='+str(i)+'&trans=1&JL=6_0_0';
# 	p = Process(target=deal_url, args=(format(u),))
# 	p.start()
# 	p.join()
    #result.put({'i': i, 'o': o})
	




