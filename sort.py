#!/usr/bin/env python
#-*- coding: utf-8 -*-
from urlparse import urlparse
import config
import hashlib,uuid
from framework.db import with_connection
from models import User,Blog,Tag,BlogTag, Gather, Gather_price
from models import *
from framework.web import get, post, ctx, view, interceptor, seeother, notfound,unauthorized, conRedis, Request
from framework.apis import api, Page, APIError, APIValueError, APIPermissionError, APIResourceNotFoundError
import os.path
import os, re, time, base64, hashlib, logging
from config import configs
#import sae.storage
import markdown2
from framework import db
import random, math, re
#import sae.kvdb
#from sae.taskqueue import Task,TaskQueue
import base64
import json
#kv = sae.kvdb.Client()
#counter_queue = TaskQueue(configs.taskqueue)
from gather.baseQueue import QueueManagerClient
from multiprocessing import Process


_COOKIE_NAME = 'jblog'
_COOKIE_KEY = configs.session.secret
CHUNKSIZE = 8192
UPLOAD_PATH='upload'

def base_sort():
	datas = Gather_price.find_by('where addtime=?', '20160927')
	logging.info(datas)

if __name__=='__main__':
    logging.basicConfig(level=logging.DEBUG)
    base_sort()

    