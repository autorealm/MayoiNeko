# coding: utf-8

import re, time, hashlib, logging, json, functools

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


def _dump(obj):
    if isinstance(obj, list):
        objs = []
        for o in obj:
            objs.append(_dump(o))
        return objs
    if isinstance(obj, Page):
        return {
            'page_index': obj.page_index,
            'page_count': obj.page_count,
            'item_count': obj.item_count,
            'has_next': obj.has_next,
            'has_previous': obj.has_previous
        }
    if isinstance(obj, Blog):
        return {
            'id': obj.id,
            'name': obj.get('name'),
            'summary': obj.get('summary'),
            'content': obj.get('content'),
            #'user_name': obj.get('user').get('username'),
            'created_at': str(obj.created_at)
        }
    if isinstance(obj, Comments):
        return {
            'id': obj.id,
            #'user_name': obj.get('user').get('username'),
            'content': obj.get('content'),
            'created_at': str(obj.created_at)
        }
    if isinstance(obj, User):
        return {
            'id': obj.id,
            'username': obj.get('username'),
            'password': obj.get('password'),
            'email': obj.get('email')
        }
    raise TypeError('%s is not JSON serializable' % obj)

def dumps(obj):
    return json.dumps(obj, default=_dump)

def api(func):
    @functools.wraps(func)
    def _wrapper(*args, **kw):
        try:
            r = dumps(func(*args, **kw))
        except Err, e:
            r = json.dumps(dict(error=e.error, data=e.data, message=e.message))
        except Exception, e:
            logging.exception(e)
            r = json.dumps(dict(error='internalerror', data=e.__class__.__name__, message=e.message))
        make_response().headers['content-type'] = 'application/json'
        return r
    return _wrapper

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
    else:
        user = None;
    if user is None:
        if _COOKIE_NAME in session:
            user = parse_signed_cookie(session[_COOKIE_NAME])
    return user;

@api
def sign_in(username, password, remember='false'):
    try:
        User().login(username, password)
        user = Query(User).equal_to("username", username).first()
    except LeanCloudError, e:
        raise e
    max_age = 604800 if remember=='true' else None
    cookie = make_signed_cookie(user.id, user.get('password'), max_age)
    response = make_response();
    response.set_cookie(_COOKIE_NAME, cookie, max_age=max_age)
    session.permanent = False
    session[_COOKIE_NAME] = cookie
    return user

_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_MD5 = re.compile(r'^[0-9a-f]{32}$')

@api
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

@api
def list_users():
    page_index = 1
    page_size = 26
    page = None
    users = []
    try:
        page_index = int(request.args.get('page', '1'))
    except ValueError:
        pass
    try:
        total = Query(User).count();
        page = Page(total, page_index, page_size)
        users = Query(User).descending('createdAt').skip(page.offset).limit(page.page_size).find()
    except LeanCloudError, e:
        if e.code == 101:  # 服务端对应的 Class 还没创建
            users = []
        else:
            raise e
    return dict(users=users, page=page)

@api
def get_user(user_id):
    user = Query(User).get(user_id)
    if user:
        return user
    raise Err('value:notfound', 'user', 'user not found.')

@api
def list_blogs():
    format = request.args.get('format', '')
    page_index = 1
    page_size = 26
    page = None
    blogs = []
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
    #logging.debug(blogs)
    if format=='html':
        for blog in blogs:
            blog.content = markdown2.markdown(blog.content)
    return dict(blogs=blogs, page=page)

@api
def get_blog(blog_id):
    blog = Query(Blog).get(blog_id)
    if blog:
        return blog
    raise Err('value:notfound', 'blog', 'blog not found.')

@api
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
    #if user is None:
        #raise Err('value:notfound', 'user', 'user not found.')
    blog = None
    try:
        blog = Query(Blog).get(blog_id)
    except LeanCloudError, e:
        pass
    try:
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

@api
def delete_blog(blog_id):
    blog = Query(Blog).get(blog_id)
    if blog is None:
        raise Err('value:notfound', 'blog', 'blog not found.')
    blog.destroy()
    return blog

@api
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

@api
def get_comments(blog_id):
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
    return comments

@api
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

@api
def delete_comment(comment_id):
    comment = Query(Comments).get(comment_id)
    if comment is None:
        raise Err('value:notfound', 'comment', 'comment not found.')
    comment.destroy()
    return comment

@api
def list_comments():
    page_index = 1
    page_size = 26
    page = None
    comments = []
    try:
        page_index = int(request.args.get('page', '1'))
    except ValueError:
        pass
    try:
        total = Query(Comments).count();
        page = Page(total, page_index, page_size)
        comments = Query(Comments).descending('createdAt').skip(page.offset).limit(page.page_size).find()
    except LeanCloudError, e:
        if e.code == 101:  # 服务端对应的 Class 还没创建
            comments = []
        else:
            raise e
    return dict(comments=comments, page=page)
