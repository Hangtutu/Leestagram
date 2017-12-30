"""
@author: lihang
@time: 2017/12/26 11:30
@describe:
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)  # type:Flask

# 由于Jinja不支持break,所以在Jinja官网找到的 break的扩展,Jinja官网搜索Extensions
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

app.config.from_pyfile('app.conf')

app.secret_key = 'lihang'

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = '/regloginpage/'
# 如果游客访问有权限的页面可以直接跳转登陆页面
from webapp import controller
from webapp import model
