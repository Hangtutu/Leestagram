'''
@arthor: lihang
@time: 2017/12/26 11:30
@describe:
'''
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)  # type:Flask
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.config.from_pyfile('app.conf')

# 由于Jinja不支持break,所以在Jinja官网找到的 break的扩展
# app.jinja_env.add_extension(' jinja2.ext.loopcontrols')

db = SQLAlchemy(app)

from webapp import controller
from webapp import model
