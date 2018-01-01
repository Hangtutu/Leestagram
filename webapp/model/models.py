"""
@author: lihang
@time: 2017/12/26 11:31
@describe:
"""
from web import db, login_manager
import random
from datetime import datetime


class User(db.Model):
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(32))
    salt = db.Column(db.String(100))
    head_url = db.Column(db.String(256))
    images = db.relationship('Image', backref='user', lazy='dynamic')

    # backref 参数代表:User类内声明image对象的同时,Image类内也可以访问user对象
    # lazy:代表加载机制是懒加载

    def __init__(self, username, password, salt=''):
        self.username = username
        self.password = password
        self.salt = salt
        self.head_url = 'http://images.nowcoder.com/head/' + str(random.randint(0, 1000)) + 't.png'

    def __repr__(self):
        return ('<User %d %s> ' % (self.id, self.username))

    # Flask_Login接口
    def is_authenticated(self):  # 用户是否通过验证,即提供有效证明时返回True
        print('is_authenticated')
        return True

    def is_active(self):
        # 如果这是一个活动用户且通过验证，账户也已激活，未被停用，也不符合任何你 的应用拒绝一个账号的条件，返回 True 。
        print('is_active')
        return True

    def is_anonymous(self):  # 判断当前用户是否是匿名用户
        print('is_anonymous')
        return False

    def get_id(self):  # 返回一个唯一识别的用户
        print('get_id')
        return self.id


class Image(db.Model):
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url = db.Column(db.String(512))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_date = db.Column(db.DateTime)
    comments = db.relationship('Comment')

    def __init__(self, url, user_id):
        self.url = url
        self.user_id = user_id
        self.created_date = datetime.now()

    def __repr__(self):
        return ('<Image %d %s>' % (self.id, self.url))


class Comment(db.Model):
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.Integer, default=0)  # 0 正常 1删除
    user = db.relationship('User')

    def __init__(self, content, image_id, user_id):
        self.content = content
        self.image_id = image_id
        self.user_id = user_id

    def __repr__(self):
        return ('<Comment %d %s>' % (self.id, self.content)).encode('gbk')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
