#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys
import log
import time
import config
import simplejson as json

from image import Image
from bs4 import BeautifulSoup
from db import Mongo, Mysql

reload(sys)
sys.setdefaultencoding('utf8')

class Parse(object):

    def __init__(self, MyObj):
        self.myobj = MyObj
        self.image  = Image(config.img_path)
        

    def do(self, doc):

        try:
            if not doc["result"]:
                return False
        except:
            return False

        r = json.loads(doc['result'])
        if not r['content']:
            log.warning('content is None:%s, url:%s' % (r['content'], r['url']))
            return False
        
        #newctx = self.__parse(r['content']).encode('utf8')
        newctx = self.__parse(r['content'])
        #print len(str(newctx))
        #print type(newctx)
        #过短文章放弃
        if len(str(newctx)) < 140:
            log.warning('content is short; url:%s' % r['url'])
            return False

        ptime = self.__ptime(r['article_time'])
        mydict = {
            'task_id' : doc['taskid'],
            'site_label' : r.get('tags', ''),
            'title' : r.get('title', ''),
            'content' : newctx,
            'url' : r.get('url'),
            'source' : r.get('source', ''),
            'topic' : r.get('topic', ''),
            'pub_time' : ptime
        }
        return self.myobj.insert('re_articles', mydict)

    def __ptime(self, ptime):
        pt = ptime.replace('年', '-').replace('月', '-').replace('日', '')
        return pt

        
    def __download(self, url):
        """
        url下载图片
        """

        trytime = 3
        while trytime > 0:
            rs = self.image.download(url)
            if rs:
                return rs
            else:
                trytime -= 1

        return False 


    def __parse(self, content):
        """
        匹配图片，剔除script，a链接标签
        """
        soup=BeautifulSoup(content, "html.parser")  
        imgs=soup.find_all('img') 
        #print soup

        if not imgs:
            return soup.get_text() 

        for cimg in imgs:
            newImg = soup.new_tag('img')
            src = cimg.get('src')
            if not src:
                """
                src为空，删除当前img节点
                """
                cimg.extract()
                continue
            nsrc = self.__download(src)
            if not nsrc:
                """
                下载失败，删除当前img节点
                """
                cimg.extract()
                continue

            newImg['src'] = nsrc
            if cimg.get('alt'):
                newImg['alt'] = cimg.get('alt')

            if cimg.get('title'):
                newImg['title'] = cimg.get('title')

            #替换为新地址图片
            cimg.replace_with(newImg)

        #替换文章内a标签，文字用span wrap
        alinks  = soup.find_all('a')
        if not alinks:
            return soup
        for alink in alinks:
            spanTag = soup.new_tag('span')
            spanTag.string = alink.get_text()
            #print alink.get_text()
            alink.replace_with(spanTag)

        #直接删除script标签
        for x in soup.find_all('script'):
            x.extract()

        return soup


def main():
    fname = config.log_path + 'article_parse.' + time.strftime("%Y%m%d")
    log.set_logger(level = 'DEBUG', when="D", limit = 1, filename=fname)
    alist = Mongo().scan()
    if not alist:
        log.warn("no articles in mongodb")
        return False

    MyObj = Mysql()

    mobj = Mongo()
    for doc in alist:
        if Parse(MyObj).do(doc):
            mobj.update(doc.get("_id"), done=1)
            log.info("insert mysql success, url:%s" % doc.get('url'))
        else:
            mobj.update(doc.get("_id"), done=-1)
            log.warning("insert mysql failure, task_id:%s, url:%s" % (doc.get('taskid'), doc.get('url')))


if __name__ == "__main__":
    main() 
    
