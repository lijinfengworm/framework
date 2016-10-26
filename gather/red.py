#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import redis, json, urllib2


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


#pip.delete('vip30073')
#pip.delete('vip30074')
#print pip.smembers('vip30074')
dict = {"30074": "品质女装"}
for k, i in dict.iteritems():
	vip = pip.smembers('vip'+k)
	l = []
	for v in vip:
	    nv = eval(v)
	    nv['href'] = urllib2.unquote(nv['href'])
	    l.append(nv)

	li = sorted(l, key=lambda s: s['discount'])

	for m in range(len(li)):
		num = bytes(m)
		pip.zadd('vip-'+k, float(m),  'vip'+k+'-'+num)
		pip.hset('vip-'+k+'-set', 'vip'+k+'-'+num, li[m])
		#del li[m]

	lix = []
	index = pip.zrange('vip-'+k,0,10)
	for ix in index:
		lix.append(pip.hget('vip-'+k+'-set', ix))

	print lix




# for i in range(len(li)):
# 	num = bytes(i)
# 	pip.zadd('vip-30074', float(i),  'vip30074-'+num)
# 	pip.hset('vip-30074-set', 'vip30074-'+num, li[i])
# 	del li[i]

# lix = []
# index = pip.zrange('vip-30074',0,10)
# for ix in index:
# 	tmp = pip.hget('vip-30074-set', ix)
# 	t = eval(tmp)
# 	lix.append(t)

# for t in lix:
# 	print type(t)
# 	break

# print lix
#print pip.hget('vip-30074-set', 'vip30074-0')
