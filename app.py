# coding: utf-8

#import logging  

from datetime import datetime

from flask import Flask
from flask import request
from flask import redirect
from flask import render_template

from views.todos import todos_view
from views.blogs import blogs_view
from views.manages import manages_view
from views.bilis import bilis_view

from develop.apis import *
from develop.markdown2 import markdown
from develop.cloudmusic import NetEase

app = Flask(__name__)
app.debug = True


# 动态路由
app.register_blueprint(todos_view, url_prefix='/todos')
app.register_blueprint(blogs_view, url_prefix='/blogs')
app.register_blueprint(manages_view, url_prefix='/manage')
app.register_blueprint(bilis_view, url_prefix='/bili')

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/time')
def time():
    return str(datetime.now())

@app.route('/test')
def test():
    cloudmusic = NetEase()
    return str(cloudmusic.search('miku'))

@app.route('/search')
def search():
    return redirect('/', 401)

@app.route('/signin')
def signin():
    return render_template('signin.html', params=dict())

@app.route('/register')
def register():
    return render_template('register.html', params=dict())

@app.route('/blog/<blog_id>')
def show(blog_id):
    blog = None
    comments = None
    user = None
    try:
        blog = Query(Blog).equal_to("objectId", blog_id).first()
        if blog is None:
            raise Err('value:notfound', 'blog', 'blog not found.')
        try:
            comments = Query(Comments).equal_to("blog", blog).descending('createdAt').find()
        except LeanCloudError, e:
            pass
    except LeanCloudError, e:
        if e.code == 101:  # 服务端对应的 Class 还没创建
            blog = {}
        else:
            raise e
    blog.set('html_content', markdown(blog.get('content')))
    if comments is None:
        comments = []
    return render_template('blog.html', blog=blog, comments=comments, user=user)

@app.route('/blog/list', methods=['POST', 'GET'])
def blog_list():
    return list_blogs()

@app.route('/blog/<blog_id>/get', methods=['POST', 'GET'])
def blog(blog_id):
    return get_blog(blog_id)

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

@app.route('/user/signup', methods=['POST'])
def user_signup():
    username = request.form['username'].strip()
    password = request.form['password'].strip()
    email = request.form['email'].strip()
    return sign_up(username, password, email)

@app.route('/user/login', methods=['POST'])
def user_login():
    username = request.form['username'].strip()
    password = request.form['password'].strip()
    return sign_in(username, password)

@app.route('/users', methods=['POST', 'GET'])
def user_list():
    return list_users()

@app.route('/user/<user_id>', methods=['POST', 'GET'])
def user():
    return get_user(user_id)

@app.route('/comments', methods=['POST', 'GET'])
def comment_list():
    return list_comments()
