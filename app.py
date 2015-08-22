# coding: utf-8

from datetime import datetime

from flask import Flask
from flask import request
from flask import redirect
from flask import render_template

from views.todos import todos_view

import develop.apis

app = Flask(__name__)
app.debug = True


# 动态路由
app.register_blueprint(todos_view, url_prefix='/todos')
#app.register_blueprint(blogs_view, url_prefix='/blogs')
#app.register_blueprint(manages_view, url_prefix='/manages')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/time')
def time():
    return str(datetime.now())
