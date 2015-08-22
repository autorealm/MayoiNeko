# coding: utf-8

import re, time, hashlib, logging

from leancloud import Object
from leancloud import User
from leancloud import Query
from leancloud import LeanCloudError
from flask import request
from flask import make_response
from flask import session

from develop.models import Blog, Comments, Page, Err

_COOKIE_NAME = 'mayoineko_skey'
_COOKIE_KEY = 'Nikora'

def _current_path():
    return os.path.abspath('.')

def _now():
    return datetime.now().strftime('%y-%m-%d_%H.%M.%S')

def make_signed_cookie(id, password, max_age):
    # build cookie string by: id-expires-md5
    expires = str(int(time.time() + (max_age or 86400)))
    L = [id, expires, hashlib.md5('%s-%s-%s-%s' % (id, password, expires, _COOKIE_KEY)).hexdigest()]
    return '-'.join(L)

def parse_signed_cookie(cookie_str):
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        id, expires, md5 = L
        if int(expires) < time.time():
            return None
        user = User().get(id)
        if user is None:
            return None
        if md5 != hashlib.md5('%s-%s-%s-%s' % (id, user.password, expires, _COOKIE_KEY)).hexdigest():
            return None
        return user
    except:
        return None

def check_login():
    cookie = request.cookies.get(_COOKIE_NAME)
    if cookie:
        user = parse_signed_cookie(cookie)
    if user is None:
        if _COOKIE_NAME in session:
            user = parse_signed_cookie(session[_COOKIE_NAME])
    request.user = user
    return user;

def sign_in(username, password):
    try:
        user = User().login(username, password)
    except LeanCloudError, e:
        raise e
    max_age = 604800 if remember=='true' else None
    cookie = make_signed_cookie(user.id, user.password, max_age)
    response = make_response();
    response.set_cookie(_COOKIE_NAME, cookie, max_age=max_age)
    session.permanent = False
    session[_COOKIE_NAME] = cookie
    user.password = '******'
    return user

_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_MD5 = re.compile(r'^[0-9a-f]{32}$')

def sign_up(username, password, email):
    email = email.strip().lower()
    if not email or not _RE_EMAIL.match(email):
        raise Err('value:invalid', 'email', 'email cannot be empty.')
    user = User()
    user.set("username", username)
    user.set("password", password)
    user.set("email", email)
    try:
        user.sign_up()
    except LeanCloudError, e:
        raise e
    return user

def sign_out():
    make_response().set_cookie(_COOKIE_NAME, None)
    session.pop(_COOKIE_NAME, None)


def update_blog(blog_id, name='', summary='', content=''):
    name = name.strip()
    summary = summary.strip()
    content = content.strip()
    if not name:
        raise Err('value:invalid', 'name', 'name cannot be empty.')
    if not summary:
        raise Err('value:invalid', 'summary', 'summary cannot be empty.')
    if not content:
        raise Err('value:invalid', 'content', 'content cannot be empty.')
    user = check_login()
    if user is None:
        raise Err('value:notfound', 'user', 'user not found.')
    try:
        blog = Query(Blog).get(blog_id)
        if blog is None:
            blog = Blog(name=name, summary=summary, content=content, user=user)
        else:
            blog.set('name', name)
            blog.set('summary', summary)
            blog.set('content', content)
        blog.save()
    except LeanCloudError, e:
        raise e
    return blog

def delete_blog(blog_id):
    blog = Query(Blog).get(blog_id)
    if blog is None:
        raise Err('value:notfound', 'blog', 'blog not found.')
    blog.destroy()
    return blog

def comment(blog_id, content=''):
    user = check_login()
    if user is None:
        raise Err('value:notfound', 'user', 'user not found.')
    content = content.strip()
    if not content:
        raise Err('value:invalid', 'content', 'content cannot be empty.')
    try:
        blog = Query(Blog).get(blog_id)
        comment = Comment(blog=blog, user=user, content=content)
        comment.save()
    except LeanCloudError, e:
        raise e
    
    return comment

def update_comment(comment_id, content=''):
    #if user is None:
        #raise Err('value:notfound', 'user', 'user not found.')
    content = content.strip()
    if not content:
         raise Err('value:invalid', 'content', 'content cannot be empty.')
    comment = Query(Comments).get(comment_id)
    if comment is None:
        raise Err('value:notfound', 'comment', 'comment not found.')
    comment.set('content', content)
    comment.save()
    return comment

def delete_comment(comment_id):
    comment = Query(Comments).get(comment_id)
    if comment is None:
        raise Err('value:notfound', 'comment', 'comment not found.')
    comment.destroy()
    return comment
