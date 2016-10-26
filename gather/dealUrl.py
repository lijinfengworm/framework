#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from bs4 import BeautifulSoup
import os, time, urllib2,logging, sys, math
from multiprocessing import Pool
import redis

class RedisPool(object):
	"""docstring for RedisPool"""
	def __init__(self, host, port, user, passwd, db):
		self.host = host
		self.port = port
		self.db = db
		self.user = user
		self.passwd = passwd
	
	def pool(self):
		pool = redis.ConnectionPool(host=self.host, port=self.port,  password=self.passwd)
		return redis.StrictRedis(connection_pool= pool)


red = RedisPool('fb26689b3e7f4fc3.m.cnhza.kvstore.aliyuncs.com', 6379, '', 'fb26689b3e7f4fc3:YbeNI3ByazP3', 0)
pip = red.pool()


def deal_url_string(url):
	page = urllib2.urlopen(url).read()
	soup = BeautifulSoup(page, "html.parser")
	#sp = soup.prettify()
	pg = soup.find(class_="total")
	p = pg.get_text()
	_p = p.split('/', 1)
	if len(_p):
		return _p[1]

	return 0

def run_process(new_url, cate):
	page = urllib2.urlopen(new_url).read()
	soup = BeautifulSoup(page, "html.parser")
	item = soup.find_all(class_="goods-list-item")
	
	if len(item):
		for x in item:
			item_href = x.find(class_="goods-image")
			href = item_href.find('a').get('href')
			href = urllib2.quote(href)
			title = item_href.find('a').get('title')
			item_info = x.find(class_="goods-price-info")
			price = item_info.find(class_="price").get_text()
			old_price_tag = item_info.find(class_="goods-market-price")
			old_price_tag.span.decompose()
			old_price =  old_price_tag.get_text()
			discount =  format(float(price)/float(old_price), '0.2f')
			var_list = {"href":href, "title":title , "price":price, "old_price":old_price, "discount":discount}
			discount =  int(math.fsum([float(discount)] * 100))
			if discount < 50:
				pip.sadd('vip'+cate,var_list)
	#href = item_href.href
	#print href


class Vip(object):
	"""docstring for Vip"""
	def __init__(self, url, page):
		self.url = url
		self.page = page

	def do_url(self):
		str = self.url.split('|')
		if len(str):
			return str[1]
		return 0

	"""定义进程池"""
	def doprocess(self):
		p = Pool()
		cate = self.do_url()
		for i in xrange(1,self.page):
			new_url = 'http://category.vip.com/search-2-0-{0}.html?q=1|{1}|&rp={2}|0#catPerPos'.format(i, cate, cate)
			if not new_url is None:
				p.apply_async(run_process, args=(new_url, cate,  ))
						
		print '开始进程---采集程序开始'
		p.close()
		p.join()
		print '结束进程---采集程序结束'
			


'''
写一个进程池，处理分页后的页面
'''	

if __name__=='__main__':
	logging.basicConfig(level=logging.DEBUG)
	url = 'http://category.vip.com/search-2-0-1.html?q=1|30074|&rp=30074|0#catPerPos'
	page = deal_url_string(url)
	vip = Vip(url, int(page))
	vip.doprocess()
	
