# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from scrapy import log
import threading
import MySQLdb
from datetime import date, timedelta
import re
from spider_news_all.items import SpiderNewsAllItem


class CnblogsSpider(scrapy.Spider):
    name = "cnblogs"
    allowed_domains = ["cnblogs.com"]
    start_urls = (
        'http://www.cnblogs.com/news',
    )
    handle_httpstatus_list = [404]

    FLAG_INTERRUPT = False
    SELECT_NEWS_BY_TITLE_AND_URL = "SELECT * FROM news_all WHERE title='%s' AND url='%s'"

    lock = threading.RLock()
    conn=MySQLdb.connect(user='root', passwd='', db='news', host='127.0.0.1')
    conn.set_character_set('utf8')
    cursor = conn.cursor()
    cursor.execute('SET NAMES utf8;')
    cursor.execute('SET CHARACTER SET utf8;')
    cursor.execute('SET character_set_connection=utf8;')

    URL_TEMPLATE = 'http://news.cnblogs.com/n/%s'
    # URL_TEMPLATE = 'http://www.cs.com.cn/xwzx/cj/index_%s.html'
    # URL_TEMPLATE = 'http://www.cs.com.cn/ssgs/gsxw/index_%s.html'
    index = 0

    def is_news_not_saved(self, title, url):
        if self.FLAG_INTERRUPT:
            self.lock.acquire()
            rows = self.cursor.execute(self.SELECT_NEWS_BY_TITLE_AND_URL % (title, url))
            if rows > 0:
                log.msg("News saved all finished.", level=log.INFO)
                return False
            else:
                return True
            self.lock.release()
        else:
            return True

    def parse_news(self, response):
        log.msg("Start to parse news " + response.url, level=log.INFO)
        item = SpiderNewsAllItem()
        day = title = _type = keywords = url = article = ''
        #直接解析meta
        url = response.url
        day = response.meta['day']
        title = response.meta['title']
        _type = response.meta['_type']
        response = response.body
        soup = BeautifulSoup(response)

        #找到文章
        try:
            # article = soup.find(class_='postTitle').text.strip()
            article = soup.find(id='news_body').text.strip()
        except:
            log.msg("News " + title + " dont has article!", level=log.INFO)
        item['title'] = title
        item['day'] = day
        item['_type'] = _type
        item['url'] = url
        item['keywords'] = keywords
        item['article'] = article
        item['site'] = u'博客园'
        return item

    #根据url分类内容
    def get_type_from_url(self, url):
        # if 'hg' in url:
        #     return u'新闻.宏观'
        # elif 'cj' in url:
        #     return u'新闻.产经'
        # elif 'gongsi' in url:
        #     return u'上市公司'
        # elif 'gsxw' in url:
        #     return u'公司.公司新闻'
        # else:
            return ''

    #未实现
    #内容过滤很重要
    def parse(self, response):
        self.index = self.index + 1
        log.msg("Start to parse page " + response.url, level=log.INFO)
        url = response.url
        url_base = url.split('/n')[0]
        _type = self.get_type_from_url(url)
        items = []
        try:
            response = response.body
            soup = BeautifulSoup(response)
            lists = soup.find(class_='column-box')
            links = lists.find_all('li')
        except:
            items.append(self.make_requests_from_url(url))
            log.msg("Page " + url + " parse ERROR, try again !", level=log.ERROR)
            return items
        need_parse_next_page = True
        if len(links) > 0:
            for i in range(0, len(links)):
                try:
                    if links[i]['class'] == ['nobg']:
                        continue
                except:
                    log.msg("Start to parse page ", level=log.INFO)
                url_news = url_base + links[i].a['href'][1:]
                day = links[i].span.text.strip()
                title = links[i].a.text.strip()
                need_parse_next_page = self.is_news_not_saved(title, url_news)
                if not need_parse_next_page:
                    break
                items.append(self.make_requests_from_url(url_news).replace(callback=self.parse_news, meta={'_type': _type, 'day': day, 'title': title}))
            if (self.index != 10):
                page_next = self.URL_TEMPLATE % (self.index)
                if need_parse_next_page:
                    items.append(self.make_requests_from_url(page_next))
            return items
