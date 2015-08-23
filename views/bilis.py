# coding: utf-8

import sys, re, json
from leancloud import Object
from leancloud import User
from leancloud import Query
from leancloud import LeanCloudError
from flask import Blueprint
from flask import request
from flask import redirect
from flask import url_for
from flask import render_template

reload(sys)
sys.setdefaultencoding('utf8')

sys.path.append("..")
from develop.models import Page
from develop.biclass import *
from develop.bilibili import *


bilis_view = Blueprint('bilis', __name__)

APPKEY = '85eb6835b0a1034e'
APPSEC = '2ad42749773c441109bdc0191257a664'

@bilis_view.route('')
def list():
    page_index = 1
    page_size = 30
    tid = 0
    days = 15
    order='hot'
    page = None
    try:
        page_index = int(request.args.get('page', '1'))
        tid = int(request.args.get('tid', '0'))
        days = int(request.args.get('days', '15'))
        order = str(request.args.get('order', 'hot'))
    except ValueError:
        pass
    try:
        bilis = GetRank(APPKEY, tid, days=days, page=page_index, pagesize=page_size, order=order, AppSecret=APPSEC)
        total = len(bilis)
        #return str(total);
        page = Page(total, page_index, page_size)
    except:
        raise
    return render_template('bili_list.html', list=bilis, page=page)

@bilis_view.route('/search')
def search():
    page_index = 1
    page_size = 20
    keyword = ''
    order='default'
    page = None
    try:
        page_index = int(request.args.get('page', '1'))
        keyword = str(request.args.get('keyword', ''))
        order = str(request.args.get('order', 'default'))
    except ValueError:
        pass
    regex_match = re.findall('av(\\d+)', keyword)
    if regex_match:
        return redirect(url_for('.view', video_id=regex_match[0]))
    try:
        bilis = biliVideoSearch(APPKEY, APPSEC, keyword, order=order, page=page_index, pagesize=page_size)
        total = len(bilis)
        page = Page(total, page_index, page_size)
    except:
        raise
    return render_template('bili_list.html', list=bilis, page=page)

@bilis_view.route('/view/<video_id>')
def view(video_id):
    fav = ''
    try:
        video = GetBilibiliVideo(video_id, APPKEY, AppSecret=APPSEC)
    except:
        raise
    return render_template('bili_view.html', item=video)

@bilis_view.route('', methods=['POST'])
def save():
    name = request.form['name'].strip()
    
    #blog = Blog(name=name, summary=summary, content=content, user=user)
    #blog.save()
    return redirect(url_for('bilis_view.list'))
