# -*- coding: utf-8 -*-
import MySQLdb
import threading
import pymysql
from DBUtils.PooledDB import PooledDB
from scrapy.utils.project import get_project_settings
from scrapy import log
import __future__

class DbPool(object):
    _instance_lock = threading.Lock()

    def __init__(self):
        if not hasattr(DbPool, "pool"):
            DbPool.mysql_pool()
        else:
            pass

    def __new__(cls, *args, **kwargs):
        if not hasattr(DbPool, "_instance"):
            with DbPool._instance_lock:
                if not hasattr(DbPool, "_instance"):
                    DbPool._instance = object.__new__(cls, *args, **kwargs)
        return DbPool._instance

    @staticmethod
    def mysql_pool():
        settings = get_project_settings()

        host = settings['MYSQL_HOST']
        port = int(settings['MYSQL_PORT'])
        user = settings['MYSQL_USER']
        passwd = settings['MYSQL_PASSWD']
        db = settings['MYSQL_DBNAME']
        DbPool.pool = PooledDB(
            creator=pymysql,  # 使用链接数据库的模块
            mincached=2,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
            maxcached=6,  # 链接池中最多闲置的链接，0和None不限制
            maxshared=3,
            # 链接池中最多共享的链接数量，0和None表示全部共享。PS: 无用，因为pymysql和MySQLdb等模块的 threadsafety都为1，所有值无论设置为多少，_maxcached永远为0，所以永远是所有链接都共享。
            maxconnections=8,  # 连接池允许的最大连接数，0和None表示不限制连接数
            blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
            maxusage=None,  # 一个链接最多被重复使用的次数，None表示无限制
            setsession=None,  # 开始会话前执行的命令列表。如：["set datestyle to ...", "set time zone ..."]
            # ping MySQL服务端，检查是否服务可用。# 如：0 = None = never, 1 = default = whenever it is requested, 2 = when a cursor is created, 4 = when a query is executed, 7 = always
            host=host,
            port=port,
            user=user,
            passwd=passwd,
            db=db,
            use_unicode=False,
            charset='utf8'
        )



class DB:
    con = DbPool().pool.connection()
    SELECT_NEWS_BY_URL = "SELECT count(1) FROM news_all WHERE url='%s'"
    SELECT_NEWS_BY_TITLE_AND_URL = "SELECT count(1) FROM news_all WHERE url='%s' or title ='%s'"
    INSERT_NEWS_ALL = ("INSERT INTO news_all (title, day, type, url, keywords, article, site) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s)")

    #判断给定的url或者title是否存在
    def isExists(self, url, title = None):
        cursor = self.con.cursor()
        if None == title:
            log.msg('SQL:' + self.SELECT_NEWS_BY_URL % url)
            cursor.execute(self.SELECT_NEWS_BY_URL % (url))
        else:
            log.msg('SQL:' + self.SELECT_NEWS_BY_TITLE_AND_URL % (url, title))
            cursor.execute(self.SELECT_NEWS_BY_TITLE_AND_URL % (url, title))

        # print(cursor.fetchone())
        # exit()
        if 0 < cursor.fetchone()[0]:
            log.msg("News saved all finished.", level=log.INFO)
            return True
        else:
            return False

    #写入数据
    def insert(self, title, day, _type, url, keywords, article, site):
        cursor = self.con.cursor()
        if False == self.isExists(url):
            news = (title, day, _type, url, keywords, article, site)
            try:
                cursor.execute(self.INSERT_NEWS_ALL, news)
                self.con.commit()
                log.msg('SQL:' + self.INSERT_NEWS_ALL % news)
                log.msg("%s saved successfully" % url, level=log.INFO)
            except Exception, e:
                log.msg("MySQL exception, msg => %s" % str(e), level=log.ERROR)
        else:
            log.msg('%s is exists, dont write!' % url)


#测试
# a = DB()
# a.insert('1211231', '212', '1123132311', '1112313123123123', '1', '1', '1')
# print a.isExists('http://news.cnblogs.com/n/594133/')

