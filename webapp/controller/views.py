'''
@arthor: lihang
@time: 2017/12/26 11:31
@describe:
'''

from web import app, db
from flask import render_template, redirect
from webapp.model.models import User, Image, Comment


@app.route('/')
def index():
    images = Image.query.order_by(db.desc(Image.id)).limit(10).all()
    return render_template('index.html', images=images)


@app.route('/image/<int:image_id>')
def image(image_id):
    image = Image.query.get(image_id)
    if image == None:
        redirect('/')
    return render_template('pageDetail.html', image=image)


@app.route('/profile/<int:user_id>')
def profile(user_id):
    user = User.query.get(user_id)
    if user == None:
        redirect('/')
    return render_template('profile.html', user=user)
