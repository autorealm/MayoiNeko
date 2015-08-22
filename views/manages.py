# coding: utf-8

from leancloud import Object
from leancloud import Query
from leancloud import LeanCloudError
from flask import Blueprint
from flask import request
from flask import redirect
from flask import url_for
from flask import render_template

from develop.models import Blog, Comments, Page, Err

manages_view = Blueprint('manages', __name__)

def _get_page_index():
    page_index = 1
    try:
        page_index = int(request.get('page', '1'))
    except ValueError:
        pass
    return page_index


@manages_view.route('/', methods=['GET'])
def manage_index():
    #return redirect(url_for('todos.show'))
    return str('bad request.')

@manages_view.route('/comments')
def manage_comments():
    return render_template('manage_comment_list.html', page_index=_get_page_index(), user=request.user)

@manages_view.route('/blogs')
def manage_blogs():
    return render_template('manage_blog_list.html', page_index=_get_page_index(), user=request.user)

@manages_view('/blog/create')
def manage_blog_create():
    return render_template('manage_blog_edit.html', id=None, action='/blog/0/update', redirect='/manage/blogs', user=request.user)

@app.route('/blog/edit/:blog_id')
def manage_blog_edit(blog_id):
    blog = Query(Blog).get(blog_id)
    if blog is None:
        raise notfound()
    return render_template('manage_blog_edit.html', id=blog.id, name=blog.name, summary=blog.summary, content=blog.content, action='/blog/%s/update' % blog_id, redirect='/manage/blogs', user=request.user)

@manages_view.route('/users')
def manage_users():
    return render_template('manage_user_list.html', page_index=_get_page_index(), user=request.user)

