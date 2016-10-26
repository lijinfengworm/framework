#!/usr/bin/env python
#-*- coding:utf-8 -*-

import time,uuid
from framework.db import next_id
from framework.orm import Model,StringField,BooleanField,FloatField,TextField,IntegerField
from framework import db
import logging

class User(Model):
    __table__ = "users"

    id = StringField(primary_key=True,default=next_id,ddl='varchar(50)')
    email = StringField(updatable=False,ddl='varchar(50)')
    password = StringField(ddl='varchar(50)')
    admin = BooleanField()
    created_at = FloatField(updatable=False,default=time.time)

class Blog(Model):
    __table__ = 'blogs'

    id = StringField(primary_key=True,default=next_id,ddl='varchar(50)')
    user_id = StringField(updatable=False,ddl='varchar(50)')
    title = StringField(ddl='varchar(50)')
    content = TextField()
    image = StringField(ddl='varchar(500)')
    created_at = FloatField(updatable=False,default=time.time)
    click = IntegerField()

class Tag(Model):
    __table__ = 'tags'
    id = StringField(primary_key=True,default=next_id,ddl='varchar(50)')
    name = StringField(ddl='varchar(50)')
    number = IntegerField(default=0)

class BlogTag(Model):
    __table__ = 'blogtag'
    id = StringField(primary_key=True,default=next_id,ddl='varchar(50)')
    blog_id = StringField(updatable=False,ddl='varchar(50)')
    tag_id = StringField(updatable=False,ddl='varchar(50)')

class Gather_price(Model):
    __table__ = 'gather_price'
    id = StringField(primary_key=True,default=next_id,ddl='varchar(50)')
    goods_id = StringField(updatable=False,ddl='varchar(50)')
    price = StringField(updatable=False,ddl='varchar(50)')
    sales = StringField(updatable=False,ddl='varchar(50)')
    rated = StringField(updatable=False,ddl='varchar(50)')
    addtime = StringField(updatable=False,ddl='varchar(50)')

class Gather_amazon(Model):
    __table__ = 'gather_amazon'
    id = StringField(primary_key=True,default=next_id,ddl='varchar(50)')
    g_id = StringField(updatable=False,ddl='varchar(50)')
    
    
class Gather(Model):
    __table__ = 'gather'
    id = StringField(primary_key=True,default=next_id,ddl='varchar(50)')
    title = StringField(updatable=False,ddl='varchar(255)')
    price = StringField(updatable=False,ddl='varchar(255)')
    cover = StringField(updatable=False,ddl='varchar(255)')
    info = StringField(updatable=False,ddl='varchar(255)')
    base = StringField(updatable=False,ddl='varchar(255)')
    addtime = StringField(updatable=False,ddl='varchar(255)')
    goods_id = StringField(updatable=False,ddl='varchar(255)')


def get_tags_from_blog(blog):
    tags = db.select('select tags.id,tags.name from tags,blogtag where tags.id=blogtag.tag_id and blogtag.blog_id="%s"' % blog.id)
    return tags

def get_blogs_from_tag(tag):
    blogs = db.select('select blogs.id,blogs.title,blogs.content,blogs.image,blogs.created_at from \
            blogs,blogtag where blogs.id=blogtag.blog_id and blogtag.tag_id="%s"' % tag.id)
    return blogs



def all_tags():
    tags = Tag.find_all()
    return tags
