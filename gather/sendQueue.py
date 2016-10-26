#!/usr/bin/env python
# -*- encoding:utf-8 -*-

from baseQueue import QueueManagerClient

client = QueueManagerClient()(address=('47.89.54.152', 5000), authkey=b'secret')
client.connect()
task = client.get_task_queue()
n = 10
print 123
'''
http://category.vip.com/search-2-0-1.html?q=1|30068|&rp=30068|0#catPerPos
http://category.vip.com/search-2-0-1.html?q=1|30069|&rp=30069|0#catPerPos
'''

dict = {"30073": "潮流男装", "30072": "时尚鞋包", "30071":"美妆个护", "30066": "运动户外", "30068":"家电数码", "30069": "居家用品" }
for k, i in dict.iteritems():
	print('Put task %s...' % k)
 	task.put('http://category.vip.com/search-2-0-1.html?q=1|{0}|&rp={1}|0#catPerPos'.format(k, k))
