# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import threading
import MySQLdb
from scrapy import log

class SpiderNewsAllPipeline(object):
    
    SELECT_NEWS_BY_TITLE_AND_URL = "SELECT count(1) FROM news_all WHERE url='%s'"

    INSERT_NEWS_ALL = ("INSERT INTO news_all (title, day, type, url, keywords, article, site) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s)")

    lock = threading.RLock()
    conn=MySQLdb.connect(user='root', passwd='', db='news', host='127.0.0.1')
    conn.set_character_set('utf8')
    cursor = conn.cursor()
    cursor.execute('SET NAMES utf8;')
    cursor.execute('SET CHARACTER SET utf8;')
    cursor.execute('SET character_set_connection=utf8;')

    def insert(self, title, day, _type, url, keywords, article, site):
        def is_news_not_saved(title, url):         
            self.lock.acquire()
            self.cursor.execute(self.SELECT_NEWS_BY_TITLE_AND_URL % (url))            
            if 0 < self.cursor.fetchone()[0]:
                log.msg("News saved all finished.", level=log.INFO)
                return False
            else:
                return True
            self.lock.release()
            

        # if False == is_news_not_saved(title, url):
        #    return None                
        self.lock.acquire()
            
        news = (title, day, _type, url, keywords, article, site)
        try:
            self.cursor.execute(self.INSERT_NEWS_ALL, news)
            self.conn.commit()
            log.msg(title + " saved successfully", level=log.INFO)
        except:
            log.msg("MySQL exception !!!", level=log.ERROR)
        self.lock.release()

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