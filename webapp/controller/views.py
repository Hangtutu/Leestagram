'''
@arthor: lihang
@time: 2017/12/26 11:31
@describe:
'''

from web import app
from flask import render_template


@app.route('/')
@app.route('/index/')
def index():
    msg = '123456'
    return render_template('index.html', msg=msg)
