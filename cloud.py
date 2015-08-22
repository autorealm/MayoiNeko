# coding: utf-8

import os, sys, time
from datetime import datetime
from leancloud import Engine

from app import app

reload(sys)
sys.setdefaultencoding('utf8')

engine = Engine(app)

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

@engine.define
def hello(**params):
    if 'name' in params:
        return 'Hello, {}!'.format(params['name'])
    else:
        return 'Hello, LeanCloud!'

@app.template_filter('datetime')
def datetime_filter(t):
    if isinstance(t, datetime):
        t = time.mktime(t.timetuple())
    if not t:
        return '未知时间'
    delta = int(time.time() - t)
    if delta < 60:
        return '1分钟前'
    if delta < 3600:
        return '%s分钟前' % (delta // 60)
    if delta < 86400:
        return '%s小时前' % (delta // 3600)
    if delta < 604800:
        return '%s天前' % (delta // 86400)
    dt = datetime.fromtimestamp(t)
    return '%s年%s月%s日' % (dt.year, dt.month, dt.day)

#app.jinja_env.filters['datetime'] = datetime_filter

