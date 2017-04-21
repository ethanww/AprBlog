from flask import render_template
# from manage import app
from . import main

'''错误界面'''
# @app.errorhandler(404)
@main.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# @app.errorhandler(500)
@main.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500