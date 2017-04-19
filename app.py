from flask import Flask,render_template,url_for,session,redirect,request,flash,abort,Markup
from werkzeug.security import check_password_hash
from flask_moment import Moment
from flask_mongoengine import MongoEngine
from flask_admin import Admin
from flask_admin.contrib import sqla
from flask_wtf import Form
import os
import hashlib #计算md5
import functools #装饰器中用到
from datetime import datetime

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

'''错误界面'''
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'),500

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
    pass_hash='pbkdf2:sha1:1000$80Oc5MyH$74a5c46815e27f6282b744c6590b012cf9f23b56'
    if request.method=='POST' and request.form.get('password'):
        if check_password_hash(pass_hash,request.form.get('password')):
            session['logged_in']=True
            session.permanent=True #保持session
            flash('成功登录!','success')
            print(request.path)
            return redirect(next_url or url_for('index'))
        flash('密码错误，请重新输入','danger')
    return render_template('login.html',next=next_url)

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
    pagination=Post.objects.filter(published=True).order_by('-timestamp').paginate(page=1,per_page=10)
    posts=pagination.items
    return render_template('index.html',posts=posts,pagination=pagination,is_draft=False)


'''草稿箱视图函数'''
@app.route('/draft')
@login_required
def draft():
    page=request.args.get('page',1,type=int)
    pagination=Post.objects.filter(published=False).order_by('-timestamp').paginate(page=1,per_page=10)
    posts=pagination.items
    return render_template('index.html',posts=posts,pagination=pagination,is_draft=True)

'''博文创建视图'''
@app.route('/create',methods=['GET','POST'])
@login_required
def create():
    pass


'''数据库模型，采用MongoDB'''
class Post(db.Document):
    title=db.StringField(max_length=80)
    content=db.StringField()
    timestamp=db.DateTimeField(default=datetime.utcnow)
    published=db.BooleanField(default=False)
    # category_id=db.IntField()
    category=db.StringField(max_length=80,default='default')
    meta={
        'allow_inheritance': True,
        'ordering':['timestamp']
    }

    def __init__(self,title,content,category,published=False):
        self.title=title
        self.content=content
        self.category=category
        if published:
            self.published=True

    def __repr__(self):
        return '<Post %r>' %self.title



if __name__ == '__main__':
    app.run(host='127.0.0.1',port=5001)

