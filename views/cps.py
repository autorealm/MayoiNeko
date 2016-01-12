# coding: utf-8

import sys;
from leancloud import Object
from leancloud import Query
from leancloud import LeanCloudError
from flask import Blueprint
from flask import request
from flask import redirect
from flask import url_for
from flask import render_template

sys.path.append('..');
from develop.models import Blog, Comments, Page, Err

cps_view = Blueprint('cps', __name__)

def _get_page_index():
    page_index = 1
    try:
        page_index = int(request.args.get('page', '1'))
    except ValueError:
        pass
    return page_index


@cps_view.route('/', methods=['GET'])
def manage_index():
    list = []
    data = {}
    data.title = 'Ö÷Ò³±êÌâ'
    list.append(data)
    return render_template('cps/index.html', page_index=_get_page_index(), list=data, user=None)

@cps_view.route('/comments')
def manage_comments():
    return redirect(url_for('todos.show'))

@cps_view.route('/blog/<blog_id>')
def manage_blog_edit(blog_id):
    blog = Query(Blog).get(blog_id)
    if blog is None:
        raise notfound()
    return render_template('manage_blog_edit.html', id=blog.id, name=blog.get('name'), summary=blog.get('summary'), content=blog.get('content'), action='/blog/%s/update' % blog_id, redirect='/manage/blogs', user=None)

@cps_view.route('/users')
def manage_users():
    return str('bad request.')

