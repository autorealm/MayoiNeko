# coding: utf-8

from datetime import datetime

from flask import Flask
from flask import request
from flask import redirect
from flask import render_template

from views.todos import todos_view
from views.blogs import blogs_view
from views.manages import manages_view

from develop.apis import *

app = Flask(__name__)
app.debug = True


# 动态路由
app.register_blueprint(todos_view, url_prefix='/todos')
app.register_blueprint(blogs_view, url_prefix='/blogs')
app.register_blueprint(manages_view, url_prefix='/manage')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/time')
def time():
    return str(datetime.now())

@app.route('/signin')
def signin():
    return render_template('signin.html', params=dict())

@app.route('/register')
def register():
    return render_template('register.html', params=dict())

@app.route('/blog/list', methods=['POST', 'GET'])
def blog_list():
    return list_blogs()

@app.route('/blog/<blog_id>/update', methods=['POST'])
def blog_update(blog_id):
    name = request.form['name'].strip()
    summary = request.form['summary'].strip()
    content = request.form['content'].strip()
    return update_blog(blog_id, name, summary, content)

@app.route('/blog/<blog_id>/delete', methods=['POST', 'GET'])
def blog_delete(blog_id):
    return delete_blog(blog_id)

@app.route('/blog/<blog_id>/comment', methods=['POST'])
def comment(blog_id):
    content = request.form['content'].strip()
    return comment(blog_id, content)

@app.route('/comment/<comment_id>/update', methods=['POST'])
def comment_update(comment_id):
    content = request.form['content'].strip()
    return update_comment(comment_id, content)

@app.route('/comment/<comment_id>/delete', methods=['DELETE'])
def comment_delete(comment_id):
    return delete_comment(comment_id)

