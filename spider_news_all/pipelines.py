# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import threading
import MySQLdb
from scrapy import log
import DB
#
#todo 需要搞清楚threading的使用
#
class SpiderNewsAllPipeline(object):

    def insert(self, title, day, _type, url, keywords, article, site):
        DB.DB().insert(title, day, _type, url, keywords, article, site)

    def process_item(self, item, spider):
        title = item['title']
        day = item['day']
        _type = item['_type']
        url = item['url']
        keywords = item['keywords']
        article = item['article']
        site = item['site']
        self.insert(title, day, _type, url, keywords, article, site)
        return item