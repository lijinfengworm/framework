#!/usr/bin/env python
#-*- coding: utf-8 -*-
from urlparse import urlparse
import config
import hashlib,uuid
from framework.db import with_connection
from models import User,Blog,Tag,BlogTag, Gather, Gather_price, Gather_amazon
from models import *
from framework.web import get, post, ctx, view, interceptor, seeother, notfound,unauthorized, conRedis, Request
from framework.apis import api, Page, APIError, APIValueError, APIPermissionError, APIResourceNotFoundError
import os.path
import os, re, time, base64, hashlib, logging
from datetime import datetime
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
#SAE_BUCKET = configs.storage['bucket']

log = []
log.append({"start":datetime.now(), "log":'队列任务开始'})

def tag_count_add(tag):
    tag.number+=1
    tag.update()

def tag_count_min(tag):
    tag.number-=1
    if tag.number == 0:
        tag.delete()
    else:
        tag.update()

def get_blog_head(content):
    length = len(content)
    if length > 50:
        length = length / 5
        return content[:length]+'\n\n...\n\n'
    else:
        return content

def render_blogs(blogs):
    #length = len(blogs)
    #main_blogs = random.sample(blogs,length/2)
    for blog in blogs:
        #if blog in main_blogs:
            #blog.main = True
        if 'SERVER_SOFTWARE' not in os.environ:
            blog.image = '/'+blog.image
        blog.content = get_blog_head(blog.content) 
        blog.content = markdown2.markdown(blog.content,extras=["code-friendly"])
        tags = get_tags_from_blog(blog)
        if tags:
            blog.tag = tags[0]
        else:
            blog.tag = Tag(name=u"未分类")
    return blogs


@view('content.html')
@get('/')
def all_blogs():
    blogs = Gather.find_all()
    list_amazon = []
    amazon = Gather_amazon.find_by('order by id asc')
    logging.info(amazon)
    for x in amazon:
        price_id = Gather_price.find_by('where id=?',x.g_id)
        gather_id = Gather.find_by('where goods_id=?', price_id[0]['goods_id'])
        logging.info(gather_id)
        if not gather_id:
            price_id[0]['title'] = u'商品标题没采集到'
        else:
            price_id[0]['title'] = gather_id[0]['title']
        list_amazon.append(price_id[0])

    #cate = [{"id":"30074", "name":"品质女装".decode('utf-8')}, {"id":"30073", "name": "潮流男装".decode('utf-8')}, {"id": "30117", "name":"时尚鞋包".decode('utf-8')}, {"id":"30071", "name":"美妆个护".decode('utf-8')}, {"id":"30066", "name": "运动户外".decode('utf-8') }, {"id":"30068", "name" : "家电数码".decode('utf-8')} , {"id":"30069",  "name":"居家用品".decode('utf-8')}]
    #blogs = conRedis('30074', 1)
    return dict(blogs=list_amazon,tag_id='30074',page=1)


@api
@get('/queue')
def queue():
    
    logging.info('队列任务开始')
    
    ip = ctx.request.remote_addr;
    
    client = QueueManagerClient()(address=('47.89.54.152', 5000), authkey=b'secret')
    client.connect()
    task = client.get_task_queue()
    
    while True:
        if task.empty():
            print 'no task yet, wait 5s...'
            time.sleep(5)
            continue
        try:
            i = task.get(timeout=10)
            strs = '用户IP为：'+ip+'。的用户领取了url为'+i.encode('utf8')+'的任务'
            log.append({"start":datetime.now(), "log":strs})
            logging.info('用户IP为：%s。的用户领取了url为%s的任务', ip, i.encode('utf8'))
            return {'url':i.encode('utf8')}
            break
           
            
        except Exception, e:
            print 'Error: {0}'.format(e)
    user = ctx.request.user

    return dict(user=user)

@post('/queue/accept')
def accept_queue():
    i = ctx.request.input()
    ip = ctx.request.remote_addr;
    strs = '用户IP为:'+ip+'。的用户开始发送任务结果到taskmanager服务器'
    log.append({"start":datetime.now(), "log":strs})
    logging.info('用户IP为：%s。的用户开始发送任务结果到服务器', ip)
    title = i.title.strip()
    price = i.price.strip()
    goods_id = i.id.strip()
    sales = i.sales.strip()
    rated = i.rated.strip()
    sale = filter(str.isdigit, sales.encode("utf-8"))
    rate = filter(str.isdigit, rated.encode("utf-8"))
    pr = filter(str.isdigit, price.encode("utf-8"))
    pr = re.sub("\D", "", pr)
    if not pr:
        logging.info(pr)
        discount = int(math.ceil(int(pr)/100))
    else:
        discount = 0

    cover = i.cover.strip()
    info = i.info.strip()
    base = i.base.strip()
    num = Gather.count_all()
    gnum = Gather_price.count_all()
    gid = int(gnum)+1
    id = int(num)+1
    g = Gather_price(id=gid, goods_id=goods_id, price=discount, sales=sale, rated=rate, addtime=time.strftime("%Y%m%d", time.localtime()))
    g.insert()
    ga = Gather.find_by('where goods_id=?',goods_id)
    
    if not ga:
        bt = Gather(id=id,title=title, price=price, cover=cover, info=info, base=base, goods_id=goods_id, addtime=time.time())
        bt.insert()
    strss = '服务器接收了IP为:'+ip+'用户的请求,把商品存入数据库'

    log.append({"start":datetime.now(), "log":strss})


    logging.info('服务器接收了IP为:%s用户的请求输入', ip)
   




@view('content.html')
@get('/tag/:tag_id/page/:page')
def tag_blogs(tag_id, page):
    cate = [{"id":"30074", "name":"品质女装".decode('utf-8')}, {"id":"30073", "name": "潮流男装".decode('utf-8')}, {"id": "30117", "name":"时尚鞋包".decode('utf-8')}, {"id":"30071", "name":"美妆个护".decode('utf-8')}, {"id":"30066", "name": "运动户外".decode('utf-8') }, {"id":"30068", "name" : "家电数码".decode('utf-8')} , {"id":"30069",  "name":"居家用品".decode('utf-8')}]
    if not tag_id:
        raise notfound()
    blogs = conRedis(tag_id, int(page))
    return dict(blogs=blogs,cate=cate, tag_id=tag_id, page=int(page))


@view("blog.html")
@get('/blog/:id')
def blog(id):
    blog = Gather.find_first('where goods_id=? ', id)
    blog.cover = blog.cover.replace('40','400')
    logging.info(blog.cover)
    #.decode('gb2312').encode('utf-8') 
    datas = Gather_price.find_by('where goods_id= ? order by addtime ASC', id)
    logging.info(datas)
    return dict(blog=blog, datas=datas)



@view('signin.html')
@get('/signin')
def signin():
    logs = []
    for x in log:
        logging.info(x)
        dt = {"start": x["start"].strftime('%m/%d/%Y %H:%M:%S'), "log": x["log"].decode('utf-8')}
        logs.append(dt)
    
    return dict(log=logs)


def make_signed_cookie(id, password, max_age):
    # build cookie string by: id-expires-md5
    expires = str(int(time.time() + (max_age or 86400)))
    L = [id, expires, hashlib.md5('%s-%s-%s-%s' % (id, password, expires, _COOKIE_KEY)).hexdigest()]
    return '-'.join(L)
#@api
@post('/api/authenticate')
def authenticate():
    i = ctx.request.input(remember='')
    email = i.email.strip().lower()
    password = i.password
    remember = i.remember
    user = User.find_first('where email=?', email)
    if user is None:
        raise APIError('auth:failed', 'email', 'Invalid email.')
    elif user.password != password:
        raise APIError('auth:failed', 'password', 'Invalid password.')
    # make session cookie:
    max_age = 604800 if remember=='true' else None
    cookie = make_signed_cookie(user.id, user.password, max_age)
    ctx.response.set_cookie(_COOKIE_NAME, cookie, max_age=max_age)
    user.password = '******'
    back_last_page(2)



def parse_signed_cookie(cookie_str):
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        id, expires, md5 = L
        if int(expires) < time.time():
            return None
        user = User.get(id)
        if user is None:
            return None
        if md5 != hashlib.md5('%s-%s-%s-%s' % (id, user.password, expires, _COOKIE_KEY)).hexdigest():
            return None
        return user
    except:
        return None

@interceptor('/')
def user_interceptor(next):
    logging.info('try to bind user from session cookie...')
    user = None
    cookie = ctx.request.cookies.get(_COOKIE_NAME)
    if cookie:
        logging.info('parse session cookie...')
        user = parse_signed_cookie(cookie)
        if user:
            logging.info('bind user <%s> to session...' % user.email)
    ctx.request.user = user
    return next()


@get('/signout')
def signout():
    ctx.response.delete_cookie(_COOKIE_NAME)
    raise seeother('/')


def check_admin():
    user = ctx.request.user
    if user and user.admin:
        return
    raise APIPermissionError('No permission.')

'''def upload(image):
    filename = os.path.join(UPLOAD_PATH,hashlib.md5(image.filename.encode('utf-8')).hexdigest()+uuid.uuid4().hex)
    if 'SERVER_SOFTWARE' in os.environ:
       conn = sae.storage.Connection() 
       bucket = conn.get_bucket(SAE_BUCKET)
       bucket.put_object(filename,image.file)
       filename = bucket.generate_url(filename)
       logging.info(filename)
    else:
        with open(filename,'w') as f:
            chunk = image.file.read(CHUNKSIZE)
            while chunk:
                f.write(chunk)
                chunk = image.file.read(CHUNKSIZE)
    return filename

def delete_upload(filename):
    if 'SERVER_SOFTWARE' in os.environ:
       conn = sae.storage.Connection() 
       bucket = conn.get_bucket(SAE_BUCKET)
       filename = urlparse(filename).path[1:]
       bucket.delete_object(filename)
    else:
        if os.path.isfile(filename):
            os.remove(filename)
    logging.info("remove file %s." % filename)
'''
def add_tags(blog_id,tags):
    if not tags:
        return
    if not tags[0]:
        return
    for tag in tags:
        t=Tag.find_by('where name=?',tag)
        if t:
            t = t[0]
        if not t:
            t = Tag(name=tag)
            t.insert()
        bt = BlogTag(blog_id=blog_id,tag_id=t.id)
        tag_count_add(t)
        bt.insert()
        logging.info("######add tag %s----%s" % (blog_id,tag))



@post('/api/blogs')
def api_create_blog():
    check_admin()
    i = ctx.request.input(title='', content='')
    logging.info(i)
    title = i.title.strip()
    content = i.content.strip()
    image = i.image
    tags = i.tags.strip()
    if image:
        logging.info("upload image name:%s,type:%s" % (image.filename,type(image.filename)))
    if not title:
        raise APIValueError('name', 'name cannot be empty.')
    #if not summary:
        #raise APIValueError('summary', 'summary cannot be empty.')
    if not content:
        raise APIValueError('content', 'content cannot be empty.')
    if not image:
        raise APIValueError('image', 'image cannot be empty.')
    filename = upload(image)
    user = ctx.request.user
    blog = Blog(user_id=user.id,  title=title,  content=content,image=filename)
    blog.insert()
    add_tags(blog.id,tags.split(' '))
    raise seeother('/blog/%s' % blog.id)

@view("add_blog.html")
@get('/manage/add_blog')
def add_blog():
    user = ctx.request.user
    return dict(user=user)

@interceptor('/')
def remember_last_page_interceptor(next):
    if ctx.request.path_info.startswith('/static') or ctx.request.path_info.startswith('/upload'):
        return next()
    referer_url = ctx.request.path_info
    remembered = ctx.request.cookie('referer_url')
    if remembered:
        array = remembered.split(',')
        if len(array) > 15:
            array = array[:15]
        remembered = ','.join(array)
    logging.info("#############@@@@@@@2")
    logging.info('remembered=%s, referer_url=%s ' % (remembered,referer_url))
    if referer_url:
        if remembered:
            ctx.response.set_cookie('referer_url',','.join([referer_url,remembered]))
        else:
            ctx.response.set_cookie('referer_url',referer_url)
    return next()

def back_last_page(back_index):
    referer_url = ctx.request.cookie('referer_url')
    logging.info('##############%s ' % referer_url)
    ctx.response.delete_cookie('referer_url')
    if referer_url:
        try:
            url=referer_url.split(',')[back_index-1]
        except IndexError:
            raise seeother('/')
        logging.info('##############%s ' % url)
        raise seeother(url)
    else:
        raise seeother('/')

@interceptor('/manage/')
def manage_interceptor(next):
    user = ctx.request.user
    if user and user.admin:
        return next()
    raise seeother('/signin')


@post('/tasks/counter')
def counter():
    i = ctx.request.input()
    key = i.blog_id.encode('utf-8')
    count = kv.get(key)
    logging.info("blog %s count is %d.\n" % (i.blog_id,count))
    kv.set(key,count+1)
    dirty = kv.get('dirty')
    if not dirty:
        kv.set('dirty','')
        dirty = ''
    kv.set('dirty',(dirty+' '+key).strip())

@post('/tasks/sync-click')
def tasks_sync_click():
    keys = kv.get('dirty').split(' ')
    keys = [k  for k in keys if k]
    dirty = kv.get_multi(keys)
    for k,v in dirty.iteritems():
        print "key: %s,value: %d\n" % (k,v)
        blog = Blog.get(k)
        blog.click = v
        blog.update()
    kv.replace('dirty','')

@get('/cron/sync-click')
def cron_sync_click():
    authorization = ctx.request.header('Authorization').split(' ')[1]
    print "@@@@@@get basic: %s \n" % authorization
    answer = base64.b64encode('jblog:jblog').decode('utf-8')
    if authorization != answer:
        raise unauthorized()


    counter_queue.add(Task('/tasks/sync-click',"time=1min"))


@view("edit_blog.html")
@get('/manage/edit/:id')
def edit_blog(id):
    blog = Blog.get(id)
    if not blog:
        raise notfound()
    tags = get_tags_from_blog(blog)
    return dict(blog=blog,user=ctx.request.user,tags=tags)

#delete one blog's some blogtag relationship.
def remove_blogtag(blog,remove):
    if not remove:
        return
    remove_string = "','".join(remove)
    s='delete from blogtag where blogtag.blog_id="%s" and blogtag.tag_id in (\'%s\')' % (blog.id,remove_string)
    logging.info('#########')
    logging.info(s)
    db.update(s)
    for tag_id in remove:
        tag = Tag.get(tag_id)
        tag_count_min(tag)

    
def update_tags(blog,tag_checkbox,tags):
    origin = get_tags_from_blog(blog)
    origin_ids = [tag.id for tag in origin]
    origin_names = [tag.name for tag in origin]

    #remove用的id
    remove = list(set(origin_ids).difference(set(tag_checkbox)))
    remove_blogtag(blog,remove)
    #add用的name
    if tags and tags[0]:
        add = list(set(tags).difference(set(origin_names)))
        add_tags(blog.id,add)

    

@post('/manage/edit/:id')
def api_edit_blog(id):
    check_admin()
    i = ctx.request.input()
    logging.info(i)
    title = i.title.strip()
    content = i.content.strip()
    image = i.image
    tags = i.tags
    try:
        tag_checkbox = ctx.request.gets('tag_checkbox')
    except KeyError:
        tag_checkbox = []
    logging.info("##################")
    logging.info(tag_checkbox)
    if not title:
        raise APIValueError('name', 'name cannot be empty.')
    if not content:
        raise APIValueError('content', 'content cannot be empty.')
    blog = Blog.get(id)
    if not blog:
        raise notfound()
    blog.title = title
    blog.content = content
    if image:
        delete_upload(blog.image)
        filename = upload(image)
        blog.image = filename
    blog.update()
    update_tags(blog,tag_checkbox,tags.split(' '))
    raise seeother('/blog/%s' % blog.id)

@api
@post('/manage/delete/:id')
def delete_blog(id):
    check_admin()
    blog = Blog.get(id)
    if not blog:
        raise notfound()
    tags = get_tags_from_blog(blog)
    remove = [tag.id for tag in tags]
    remove_blogtag(blog,remove)
    delete_upload(blog.image)
    blog.delete()
    return {'data':'/'}

@view('tag_cloud.html')
@get('/tagcloud')
def tag_cloud():
    tags = all_tags()
    user = ctx.request.user
    return dict(user=user,tags=tags)
    

@view('about.html')
@get('/about')
def about():
    user = ctx.request.user
    return dict(user=user)
    

@view('about.html')
@get('/sort')
def sort():
    user = ctx.request.user
    price = sales = rated = {}
    datas = Gather_price.find_by('where addtime=?', '20160927')
    for v in datas:
        price[int(v.id)] = int(v.price)
    price = sorted(price.items(), lambda x, y: cmp(x[1], y[1]))
    for v in datas:
        sales[int(v.id)] = int(v.sales)
    sales = sorted(sales.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
    for v in datas:
        rated[int(v.id)] = int(v.rated)
    rated = sorted(rated.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
    # 设置商品单价 、销量、 评价的权重分别是1，2，3
    # 设置前5位的集合为A1，A2，A3
    L = set()
    for l in price:
        L.add(l[0])

    A = set()
    # A1设置的是 10 ＊ 1％ , 其中1%是单价在商品属性中的权重
    A1 = set()
    tmp = price[0:1]
    for p in tmp:
        A1.add(p[0])

    # A2设置的是10 * 2% ,其中2%是销量在商品属性中的权重
    A2 = set()
    tmp2 = sales[0:2]
    for p2 in tmp2:
        A2.add(p2[0])
    # A2设置的是10 * 3% ,其中3%是评价在商品属性中的权重
    A3 = set()
    tmp3 = rated[0:3]
    for p3 in tmp3:
        A3.add(p3[0])
    
    # 设置集合A
    # 其中集合A就是集合A1、A2、A3的交集，
    A = A1 & A2 & A3
    logging.info(A)
    # 同理，我可以拿到集合B
    B = set()
    # A1设置的是 20 ＊ 1％ , 其中1%是单价在商品属性中的权重
    B1 = set()
    tmpb = price[0:2]
    for pb in tmpb:
        B1.add(pb[0])
    # A2设置的是20 * 2% ,其中2%是销量在商品属性中的权重
    B2 = set()
    tmpb2 = sales[0:4]
    for pb2 in tmpb2:
        B2.add(pb2[0])
    # A2设置的是20 * 3% ,其中3%是评价在商品属性中的权重
    B3 = set()
    tmpb3 = rated[0:6]
    for pb3 in tmpb3:
        B3.add(pb3[0])
    # 设置集合A
    # 其中集合A就是集合A1、A2、A3的交集，
    B = B1 & B2 & B3
    logging.info(B)
    B = B - A
    G = set()
    G = L - B - A

    for x in A:
        gnum = Gather_amazon.count_all()
        gid = int(gnum)+1
        g = Gather_amazon(id=gid, g_id=x)
        g.insert()

    for x in B:
        gnum = Gather_amazon.count_all()
        gid = int(gnum)+1
        g = Gather_amazon(id=gid, g_id=x)
        g.insert()

    for x in G:
        gnum = Gather_amazon.count_all()
        gid = int(gnum)+1
        g = Gather_amazon(id=gid, g_id=x)
        g.insert()

    return dict(user=user)


    
    

            


