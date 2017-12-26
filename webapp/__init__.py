'''
@arthor: lihang
@time: 2017/12/26 11:30
@describe:
'''
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_pyfile('app.conf')
db = SQLAlchemy(app)

from webapp.controller import views
from webapp.model import models
