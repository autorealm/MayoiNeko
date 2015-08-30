# -*- coding: utf-8 -*-
"""
Created on Fri Jul 25 01:10:44 2014

@author: Vespa
"""

import urllib
import shutil
import urllib2
import re
import time
import os
import cookielib
#根据正则表达式获取内容
def GetRE(content,regexp):
    return re.findall(regexp, content)

#获取网页源代码
def getURLContent(url):
    #如果失败，会不断重新获取
    while True:    	
        flag = 1;
        try:
            headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
            req = urllib2.Request(url = url,headers = headers);   
            #单次连接最长时间10s
            content = urllib2.urlopen(req,timeout = 10).read();
        except:
            print "get content Error:",url
            flag = 0;
            ###如果失败，等待5s
            time.sleep(5)
        if flag == 1:
        	break;
    #连接成功后等待1秒作为爬虫间隔，可以删除
    time.sleep(1)
    return content;

#下载资源时进度显示函数
def cbk(a, b, c):  
    '''回调函数 
    @a: 已经下载的数据块 
    @b: 数据块的大小 
    @c: 远程文件的大小 
    '''  
    per = 100.0 * a * b / c  
    if per > 100:  
        per = 100  
    print '#%.2f%%#' % per

#下载资源
def Download(url,dest,ShowProc=0):
    if ShowProc:
        print "##########begin############"
    while True:    	
        flag = 1;
        try:
            if ShowProc:
                urllib.urlretrieve(url, dest,cbk)
            else:
                urllib.urlretrieve(url, dest)
        except:
            print "SAVE FILE ERROR "
            print "URL:",url
            print "FILE",dest
            flag = 0;
            time.sleep(5)
        if flag == 1:
            if ShowProc:
                print "##########finished############"
            break;
    time.sleep(1)

#按行读取文件
def ReadFile(path):
    dirlist = [];
    for line in open(path,'r'):
        if line.find('\n') >= 0:
            line = line.replace('\n','');
        if line.find('\r') >= 0:
            line = line.replace('\r','');
        dirlist.append(line)
    return dirlist

#读取目录下一级目录
def GetDir(path):
    return  os.listdir(path)

#删除文件
def RemoveFile(path,fileName):
    shutil.rmtree(os.path.join(path,fileName))

#根据返回来Json信息构建Json类
#Getvalue可以保证再找不到指定key的时候程序不会崩溃
class JsonInfo():
    def __init__(self,url):
        self.info = json.loads(getURLContent(url));
    def Getvalue(self,*keys):
        if len(keys) == 0:
            return None
        if self.info.has_key(keys[0]):
            temp = self.info[keys[0]];
        else:
            return None;
        if len(keys) > 1:
            for key in keys[1:]:
                if temp.has_key(key):
                    temp = temp[key]
                else:
                    return None;
        return temp
    info = None;

#字符串或者数字全部转成字符串，拼接URL用
def GetString(t):
    if type(t) == int:
        return str(t)
    return t

#统一转码至UTF8
def ToUTF8(item):
    try:
        item.decode('utf8','ignore')
        k=item
    except:
        k = item.decode('gbk','ignore').encode('utf8','ignore');
    return k

#统一转码至UTF8
def ToGBK(item):
    try:
        item.decode('gbk','ignore')
        k=item
    except:
        k = item.decode('utf8','ignore').encode('gbk','ignore');
    return k

#统计文件行数
def linecount(filename):
    count = -1
    for count,line in enumerate(open(filename,'r')):
        pass
    return count+1
    
#demo
def UrlLogin():
    loginurl = 'https://www.douban.com/accounts/login'
    cookie = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
    
    params = {
    "form_email":"xxx@xxx.org",
    "form_password":"xxxxxxx",
    "source":"index_nav" 
    }
    
    response=opener.open(loginurl, urllib.urlencode(params))
    
    html = ''
    if response.geturl() == "https://www.douban.com/accounts/login":
        html=response.read()
        pass
    return opener
    #opener.open(url).read()
        
