# -*- coding: utf-8 -*-

import os

import leancloud
from wsgiref import simple_server

from app import app
from cloud import engine

APP_ID = os.environ['LC_APP_ID']
MASTER_KEY = os.environ['LC_APP_MASTER_KEY']
PORT = int(os.environ['LC_APP_PORT'])

#APP_ID = 'm6i9vkd1ia02nngqmf00q7h8'
#MASTER_KEY = 'm9p1z9fvh0cmld8y09vwozel'
#PORT = 3000

#if os.environ.get('LC_APP_PROD') == '1':
    # 当前为生产环境
#elif os.environ.get('LC_APP_PROD') == '0':
    # 当前为测试环境
#else:
    # 当前为开发环境

leancloud.init(APP_ID, master_key=MASTER_KEY)

application = engine


if __name__ == '__main__':
    # 只在本地开发环境执行的代码
    app.debug = True
    server = simple_server.make_server('localhost', PORT, application)
    server.serve_forever()
