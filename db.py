#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import log
import time
import config
import pymongo
import MySQLdb

from bson.objectid import ObjectId
class Mongo(object):
    """
    mongo
    """

    def __init__(self):
        self.conn = pymongo.MongoClient(config.mongodb, connect=False)
        self.rsdb = self.conn.resultdb

    def scan(self, lmt=50):
        """
        扫描抓取文章，进行下一步处理
        """

        llist = []
        ts = time.time() - 86400 * 10

        for doc in self.rsdb.articles.find({"done":{"$exists":False}, "updatetime":{"$gt":ts}}).limit(lmt):
            llist.append(doc)

        '''
        for doc in self.rsdb.articles.find({"_id": ObjectId('57fb1a5649e88f8bb2577d57')}):
            llist.append(doc)
        '''
        return llist
    

    def update(self, oid, **kwargs):
        """
        用于处理之后， 更新文章状态
        """
        if not oid or not kwargs:
            return False

        return self.rsdb.articles.update({"_id":ObjectId(oid)}, {"$set":kwargs})


class Mysql(object):
    """
    """

    def __init__(self):
        try:
            cfg = config.mysql
            self.conn = MySQLdb.connect(host=cfg['host'], user=cfg['user'], passwd=cfg['pwd'], db='collections',port=3306, charset='utf8')
            #print cur.execute('select * from re_articles')
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])

    def insert(self, table, ddict):
        if not ddict:
            return False
        qmarks = ', '.join(['%s'] * len(ddict)) 
        #用于替换记录值 
        cols = ', '.join(ddict.keys()) 
        sql = "INSERT INTO %s (%s) VALUES (%s)" % (table, cols, qmarks) 

        cur = self.conn.cursor()
        try:
            #cur.execute('SET NAMES UTF8')
            r = cur.execute(sql, ddict.values())
            self.conn.commit()
            return True
            
        except Execption, e:
            log.error("SQL error:%s, exceptin:%s" % (str(sys.exc_info()), str(e)))
            return False

        return True



