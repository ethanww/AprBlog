#!/usr/bin/env python
#-*-coding:utf-8-*-

from flask import Flask,render_template,url_for,session,redirect,request,flash,abort,Markup
from werkzeug.security import check_password_hash
from flask_moment import Moment
from flask_mongoengine import MongoEngine
from flask_admin import Admin
from flask_admin.contrib.mongoengine import ModelView
from flask_wtf import Form
import os
import hashlib
import functools
from datetime import datetime
'''导入支持markdown文本内容的相关库'''
from markdown import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.extra import ExtraExtension
from micawber import bootstrap_basic, parse_html
from micawber.cache import Cache as OEmbedCache


basedir=os.path.abspath(os.path.dirname(__file__))

'''配置和注册'''
app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': 'AprBlog',
    'host': '127.0.0.1',
    'port': 27017
}
app.secret_key='it is my first blog'
app.debug=True
db=MongoEngine(app)
moment=Moment(app)
admin=Admin(app,name='后台管理')
oembed_providers = bootstrap_basic(OEmbedCache())

'''错误界面'''
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

'''登录验证'''
def login_required(fn):
    @functools.wraps(fn)
    def inner(*args,**kwargs):
        if session.get('logged_in'):
            return fn(*args,**kwargs)
        return redirect(url_for('login',next=request.path))
    return inner

'''登录视图函数'''
@app.route('/login',methods=['POST','GET'])
def login():
    next_url=request.args.get('next') or request.form.get('next')
    if request.method=='POST' and request.form.get('password') and request.form.get('email'):
        try:
            user=User.objects(email=request.form.get('email')).first()
            if user.password == request.form.get('password'):
                session['logged_in'] = True
                session.permanent = True
                flash('成功登录!', 'success')
                return redirect(next_url or url_for('index'))
            flash('密码错误，请重新输入', 'danger')
        except:
            flash('不存在该用户名！','danger')

    return render_template('login.html', next=next_url)

'''登出视图函数'''
@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():
    if request.method=='POST':
        session.clear()
        flash('你已经成功登出本站','success')
        print(request.path)
        return redirect(url_for('index'))
    return render_template('logout.html')

'''首页视图函数'''
@app.route('/')
def index():
    page=request.args.get('page',1,type=int)
    pagination=Post.objects(published=True).order_by('-timestamp').paginate(page=page,per_page=10)
    posts=pagination.items
    return render_template('index.html', posts=posts, pagination=pagination, is_draft=False)
# @app.route('/')
# def index():
#     return 'hello'

'''草稿箱视图函数'''
@app.route('/draft')
@login_required
def draft():
    page=request.args.get('page',1,type=int)
    pagination=Post.objects(published=False).order_by('-timestamp').paginate(page=page,per_page=10)
    posts=pagination.items
    return render_template('index.html', posts=posts, pagination=pagination, is_draft=True)

'''博文创建视图'''
@app.route('/create',methods=['GET','POST'])
@login_required
def create():
    if request.method=='POST':
        if request.form.get('title') and request.form.get('content'):
            post=Post(title=request.form.get('title'),content=request.form.get('content'),published=request.form.get('published',None))
            try:
                post.save()
            except:
                flash('博文添加错误，请重新编辑.','danger')
                return render_template('create.html')
            if request.form.get('published'):
                flash('博文添加成功，已发布.','success')
                return redirect(url_for('index'))
            else:
                flash('博文添加成功，已存入草稿箱.','success')
                return redirect(url_for('draft'))
    return render_template('create.html')

'''创建使用者视图'''
@app.route('/adduser',methods=['GET','POST'])
def add_user():
    if request.method=='POST':
        if request.form.get('email') and request.form.get('password'):
            user_find = User.objects(email=request.form.get('email')).first()
            if user_find is None:
                user=User(email=request.form.get('email'),password=request.form.get('password'))
                try:
                    user.save()
                except:
                    flash('出了点小问题，请再输入一遍.','danger')
                    return render_template('adduser.html')
                flash('创建成功！','success')
            else:
                flash('该用户已存在.', 'danger')
    return render_template('adduser.html')



'''博文详细内容视图'''
@app.route('/detail')
def detail():
    if not request.args.get('post_id'):
        abort(404)
    post=Post.objects(id=request.args.get('post_id')).first()
    if not post:
        abort(404)
    return render_template('detail.html', post=post)

'''博文编辑'''
@app.route('/edit',methods=['GET','POST'])
@login_required
def edit():
    if not request.args.get('post_id'):
        abort(404)
    post=Post.objects(id=request.args.get('post_id')).first()
    if not post:
        abort(404)
    if request.method=='POST':
        post.title=request.form.get('title')
        post.content=request.form.get('content')
        if request.form.get('published',None):
            post.published=True
        else:
            post.published=False
        try:
            post.save()
            flash('博文更新成功.','success')
            return redirect(url_for('detail',post_id=post.id))
        except:
            flash('博文更新失败.','danger')
    return render_template('edit.html', post=post)


'''限制游客访问后台'''
@app.before_request
def before_request():
    if '/admin' in request.path and not session.get('logged_in',None):
        return redirect(url_for('login',request.path))

'''博文分类视图'''
# @app.route('/post')
# def posts():
#     posts=Post.objects(category=request.args.get('category_name'),published=True)
#     if posts:
#         return render_template('posts.html',posts=posts)
#     return redirect(url_for('index'))

'''添加CSRF Protection'''
@app.before_request
def csrf_protect():
    if request.method =='POST' and '/admin' not in request.path:
        token=session.pop('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            abort(404)

def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = hashlib.sha1(os.urandom(24)).hexdigest()
    return session['_csrf_token']
app.jinja_env.globals['csrf_token']=generate_csrf_token

'''创作者模型'''
class User(db.Document):
    email=db.StringField(required=True)
    password=db.StringField(required=True,max_length=30)
    meta={
        'allow_inheritance': True,
    }

    def __unicode__(self):
        return self.email


'''数据库模型，采用MongoDB'''
class Post(db.Document):
    title=db.StringField(max_length=80,required=True)
    content=db.StringField()
    timestamp=db.DateTimeField(default=datetime.utcnow)
    published=db.BooleanField(default=False)
    author=db.ReferenceField(User)
    # category_id=db.
    # category=db.ReferenceField('Category')
    # category=db.ListField(db.ReferenceField('Category'))
    meta={
        'allow_inheritance': True,
        'ordering':['-timestamp']
    }

    @property
    def html_content(self):
        hilite=CodeHiliteExtension(linenums=False,css_class='highlight')
        extras=ExtraExtension()
        markdowm_content=markdown(self.content,extensions=[hilite,extras])
        oembed_content=parse_html(
            markdowm_content,
            oembed_providers,
            urlize_all=True,
            maxwidth=800)
        return Markup(oembed_content)

    def __repr__(self):
        return '<Post %r>' %self.title

    def __unicode__(self):
        return self.title



'''后台管理'''
class PostAdmin(ModelView):
    form_base_class = Form
    column_display_pk = True
    can_create = False
    column_list = ('title','timestamp','published')


admin.add_view(PostAdmin(Post))


if __name__ == '__main__':
    app.run(host='127.0.0.1',port=5000)

