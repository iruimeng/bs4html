#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys
import log
import tld
import time
import requests
import urlparse

class Image(object):
    
    """
    下载文章内图片
    """

    def __init__(self, imgPath=None):
        if imgPath is None:
            self.path = "/tmp"
        else:
            self.path = imgPath

    def download(self, url):
         
        imgname = self._imgname + self._getExt(url)
        midpath = self._imgpath(url)
        ipath = os.path.join(self.path, midpath)

        self._mkdir(ipath)

        iimg = os.path.join(ipath, imgname)

        try:
            headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36"}
            rsp = requests.get(url, headers=headers, timeout=5, stream=True)
        except Exception, e:
            log.error( "read image from %s, error: %s", url, str(e))
            return False

        if rsp.status_code == 200:
            try:
                with open(iimg, 'wb') as fd:
                    for chunk in rsp.iter_content():
                        fd.write(chunk)

                return os.path.join('/', midpath, imgname)
            except Exception, e:
                log.error( "read image from %s, error: %s", url, str(e))
                return False
            
        log.error("read image status not 200")
        return False

    def _getExt(self, url):

        r = urlparse.urlparse(url)
        if r.path:
            fname, ext = os.path.splitext(r.path)
            if ext:
                return ext.lower()
        return '.jpg'


    def _mkdir(self, path):
        """
        #创建日志日期目录
        """
        if os.path.exists(path):
            return True
        os.makedirs(path)

    def _imgpath(self, url):
        """
        产生hash路径，存储图片
        """
        pfmt = "%s/%s"
        ddate = time.strftime("%Y%m%d")
        try:
            r = tld.get_tld(url, as_object=True)
            return pfmt % (r.domain, ddate)
        except Exception,e:
            log.error("tld get host error: %s" % str(e))
            return 'all/%s' % ddate

    @property
    def _imgname(self):
        """
        产生img随机名称
        """
        return ''.join(map(lambda xx:(hex(ord(xx))[2:]),os.urandom(12)))


if __name__ == "__main__":
    Obj = Image()
    Obj.download('http://p6.sinaimg.cn/3010048525/180/07871392439527')
    #Obj.download('http://com/wp-content/uploads/2016/09/qiniu_08_03.png')
