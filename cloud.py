# coding: utf-8

from leancloud import Engine

from app import app


engine = Engine(app)


@engine.define
def hello(**params):
    if 'name' in params:
        return 'Hello, {}!'.format(params['name'])
    else:
        return 'Hello, LeanCloud!'

@engine.define
def datetime_filter(t):
    delta = int(time.time() - t)
    if delta < 60:
        return u'1����ǰ'
    if delta < 3600:
        return u'%s����ǰ' % (delta // 60)
    if delta < 86400:
        return u'%sСʱǰ' % (delta // 3600)
    if delta < 604800:
        return u'%s��ǰ' % (delta // 86400)
    dt = datetime.fromtimestamp(t)
    return u'%s��%s��%s��' % (dt.year, dt.month, dt.day)

