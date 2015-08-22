# coding: utf-8

from leancloud import Object
from leancloud import User
from leancloud import Query
from leancloud import LeanCloudError
from flask import Blueprint
from flask import request
from flask import redirect
from flask import url_for
from flask import render_template

from develop.models import Blog, Comments, Page, Err

from develop.markdown2 import markdown2


blogs_view = Blueprint('blogs', __name__)


@blogs_view.route('')
def list():
    page_index = 1
    page_size = 26
    try:
        page_index = int(request.args.get('page', '1'))
    except ValueError:
        pass
    try:
        total = Query(Blog).count();
        page = Page(total, page_index, page_size)
        blogs = Query(Blog).descending('createdAt').skip(page.offset).limit(page.page_size).find()
    except LeanCloudError, e:
        if e.code == 101:  # 服务端对应的 Class 还没创建
            blogs = []
        else:
            raise e
    return render_template('blogs.html', page=page, blogs=blogs, user=user)

@blogs_view.route('blog/<blog_id>')
def show(blog_id):
    try:
        blog = Query(Blog).equal_to("objectId", blog_id).first()
        if blog is None:
            raise Err('value:notfound', 'blog', 'blog not found.')
        comments = Query(Comments).equal_to("blog", blog).descending('createdAt').find()
    except LeanCloudError, e:
        if e.code == 101:  # 服务端对应的 Class 还没创建
            blog = []
        else:
            raise e
    blog.html_content = markdown2.markdown(blog.content)
    return render_template('blog.html', blog=blog, comments=comments, user=user)

@blogs_view.route('', methods=['POST'])
def add():
    name = request.form['name'].strip()
    summary = request.form['summary'].strip()
    content = request.form['content'].strip()
    if not name:
        raise Err('value:invalid', 'name', 'name cannot be empty.')
    if not summary:
        raise Err('value:invalid', 'summary', 'summary cannot be empty.')
    if not content:
        raise Err('value:invalid', 'content', 'content cannot be empty.')
    blog = Blog(name=name, summary=summary, content=content, user=user)
    blog.save()
    return redirect(url_for('blogs.list'))
