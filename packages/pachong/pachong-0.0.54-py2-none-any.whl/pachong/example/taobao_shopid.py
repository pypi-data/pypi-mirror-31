#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Cheng Chen
# @Email : cchen224@uic.edu
# @Time  : 3/1/18
# @File  : [pachong] taobao_shopid.py


from __future__ import absolute_import
from __future__ import unicode_literals

from pachong.crawler.taobao import Taobao
from pachong.database.mongodb import MongoDB
from pachong.fetcher import Browser

project = 'yizhibo'
# project = 'test'
# fetcher = Requests(proxy='localhost:3128')
fetcher = Browser('firefox')
# crawler = Taobao(project, input_, fetcher=fetcher, Database=MongoDB)
crawler = Taobao(project, 'weibo_users', fetcher=fetcher, Database=MongoDB).login()
    # .import_input(input_list=['1866833821'], update=True)
    # .import_input(filepath='profile', update=True)\

crawler.crawl('shop')
