#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import gzip
import json
import hashlib
import re
#import urllib.parse
import urllib2
import xml.dom.minidom
import zlib
import StringIO

USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
APPKEY = '85eb6835b0a1034e'
APPSEC = '2ad42749773c441109bdc0191257a664'

def GetBilibiliUrl(url, aid=0):
    overseas=False
    pid=1
    url_get_media = 'http://interface.bilibili.com/playurl?' if not overseas else 'http://interface.bilibili.com/v_cdn_play?'
    if url:
        regex_match = re.findall('http:/*[^/]+/video/av(\\d+)(/|/index.html|/index_(\\d+).html)?(\\?|#|$)',url)
        if not regex_match:
            raise ValueError('Invalid URL: %s' % url)
        aid = regex_match[0][0]
        pid = regex_match[0][2] or '1'
    
    cid_args = {'type': 'json',  'id': str(aid), 'page': str(pid)}
    
    resp_cid = urlfetch('http://api.bilibili.com/view?'+GetSign(cid_args,APPKEY,APPSEC))
    resp_cid = dict(json.loads(resp_cid.decode('utf-8', 'replace')))
    cid = resp_cid.get('cid')
    media_args = {'cid': cid,'quality':4}
    resp_media = urlfetch(url_get_media+GetSign(media_args,APPKEY,APPSEC))
    media_urls = [str(k.wholeText).strip() for i in xml.dom.minidom.parseString(resp_media.decode('utf-8', 'replace')).getElementsByTagName('durl') for j in i.getElementsByTagName('url')[:1] for k in j.childNodes if k.nodeType == 4]
    return media_urls
    
def GetSign(params,appkey,AppSecret=None):
    """
    获取新版API的签名，不然会返回-3错误
待添加：【重要！】
    需要做URL编码并保证字母都是大写，如 %2F
    """
    params['appkey']=appkey;
    data = "";
    paras = sorted(params)
    paras.sort();
    for para in paras:
        if data != "":
            data += "&";
        data += para + "=" + str(params[para]);
    if AppSecret == None:
        return data
    m = hashlib.md5()
    m.update((data+AppSecret).encode('utf-8'))
    return data+'&sign='+m.hexdigest()
    
def urlfetch(url):
    req_headers = {'Accept-Encoding': 'gzip, deflate'}
    req = urllib2.Request(url=url, headers=req_headers)
    response = urllib2.urlopen(req, timeout=120)
    content_encoding = response.info().get('Content-Encoding')
    compressedstream = StringIO.StringIO(response.read())
    if content_encoding == 'gzip':
        gzipper = gzip.GzipFile(fileobj=compressedstream)
        data = gzipper.read()
    elif content_encoding == 'deflate':
        decompressobj = zlib.decompressobj(-zlib.MAX_WBITS)
        data = decompressobj.decompress(response.read())+decompressobj.flush()
    else:
        data = response.read()
    return data

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('输入视频播放地址')
    else:
        media_urls = GetBilibiliUrl(sys.argv[1])
        for i in media_urls:
            print(i)
