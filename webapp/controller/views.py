'''
@arthor: lihang
@time: 2017/12/26 11:31
@describe:
'''

from webapp import app
from flask import render_template
from webapp.model.models import User, Image


@app.route('/')
@app.route('/index/')
def index():
    images = Image.query.order_by(User.id.desc()).limit(10).all()
    return render_template('index.html', image=images)
