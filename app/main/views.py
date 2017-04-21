from flask import render_template,url_for,session,redirect,request,flash,abort
from werkzeug.security import check_password_hash
import hashlib
import functools
from manage import app
from app.models import Post
from . import main



'''登录验证'''
def login_required(fn):
    @functools.wraps(fn)
    def inner(*args,**kwargs):
        if session.get('logged_in'):
            return fn(*args,**kwargs)
        return redirect(url_for('login',next=request.path))
    return inner

'''登录视图函数'''
# @app.route('/login',methods=['POST','GET'])
@main.route('/login',methods=['POST','GET'])
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
    return render_template('login.html', next=next_url)

'''登出视图函数'''
# @app.route('/logout',methods=['GET','POST'])
@main.route('/logout',methods=['GET','POST'])
@login_required
def logout():
    if request.method=='POST':
        session.clear()
        flash('你已经成功登出本站','success')
        print(request.path)
        return redirect(url_for('index'))
    return render_template('logout.html')

'''首页视图函数'''
# @app.route('/')
@main.route('/')
def index():
    page=request.args.get('page',1,type=int)
    pagination=Post.objects(published=True).order_by('-timestamp').paginate(page=page,per_page=10)
    posts=pagination.items
    return render_template('index.html', posts=posts, pagination=pagination, is_draft=False)
# @app.route('/')
# def index():
#     return 'hello'

'''草稿箱视图函数'''
# @app.route('/draft')
@main.route('/draft')
@login_required
def draft():
    page=request.args.get('page',1,type=int)
    pagination=Post.objects(published=False).order_by('-timestamp').paginate(page=page,per_page=10)
    posts=pagination.items
    return render_template('index.html', posts=posts, pagination=pagination, is_draft=True)

'''博文创建视图'''
# @app.route('/create',methods=['GET','POST'])
@main.route('/create',methods=['GET','POST'])
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

'''博文详细内容视图'''
# @app.route('/detail')
@main.route('/detail')
def detail():
    if not request.args.get('post_id'):
        abort(404)
    post=Post.objects(id=request.args.get('post_id')).first()
    if not post:
        abort(404)
    return render_template('detail.html', post=post)

'''博文编辑'''
# @app.route('/edit',methods=['GET','POST'])
@main.route('/edit',methods=['GET','POST'])
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


