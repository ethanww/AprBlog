#!/usr/bin/env python
#-*-coding:utf-8-*-
import os
from app import create_app,db
from app.models import Post
from flask_script import Manager,Shell,Server

app=create_app(os.getenv('FLASK_CONFIG') or 'default')
# app=create_app()
manager=Manager(app)

def make_shell_context():
    return dict(app=app,db=db,Post=Post)
manager.add_command('shell',Shell(make_context=make_shell_context))
manager.add_command('run',Server(use_debugger=True,host='127.0.0.1',port=5007))

if __name__ == '__main__':
    manager.run()
