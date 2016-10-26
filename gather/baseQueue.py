#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
抽离队列
'''

from multiprocessing.managers import BaseManager

class _QueueManagerServer(BaseManager):
	"""docstring for _QueueManagerServer"""
	pass


def QueueManagerServer(task_queue, result_queue):
	_QueueManagerServer.register('get_task_queue', callable=lambda: task_queue)
	_QueueManagerServer.register('get_result_queue', callable=lambda: result_queue)
	return _QueueManagerServer

class _QueueManagerClient(BaseManager):
	"""docstring for _QueueManagerClient"""
	pass
	

def QueueManagerClient():
	_QueueManagerClient.register('get_task_queue')
	_QueueManagerClient.register('get_result_queue')
	return _QueueManagerClient
