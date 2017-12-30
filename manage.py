"""
@author: lihang
@time: 2017/12/26 11:30
@describe:
"""
from web import db, app
from flask_script import Manager
from webapp.model.models import User, Image, Comment
from sqlalchemy import or_, and_
import random

print('manage')
manager = Manager(app)


def get_image_url():
    return 'http://images.nowcoder.com/head/' + str(random.randint(0, 1000)) + 'm.png'


@manager.command
def init_database():
    db.drop_all()
    db.create_all()
    for i in range(0, 100):
        db.session.add(User('tutu' + str(i + 1), 'pw' + str(i)))
        for j in range(0, 10):
            db.session.add(Image(get_image_url(), i + 1))

            for k in range(0, 3):
                db.session.add(Comment('这是一条评论' + str(k), 1 + 3 * i + j, i + 1))
    db.session.commit()

    print(1, User.query.all())
    print(2, User.query.get(1))
    print(3, User.query.filter_by(id=5).first())
    print(4, User.query.order_by(User.id.desc()).offset(1).limit(2).all())
    print(5, User.query.filter(User.username.endswith('0')).limit(3).all())
    print(6, User.query.filter(or_(User.id == 99, User.id == 88)).all())
    print(7, User.query.filter(and_(User.id > 88, User.id < 99)).all())
    print(8, User.query.filter(and_(User.id > 88, User.id < 90)).first_or_404())  # 如果结果存在的话打印第一个,如果不存在的话,抛出异常
    print(9, User.query.order_by(User.id.desc()).paginate(page=2, per_page=10).items)  # 分页--显示第二页的10个数据
    user = User.query.get(1)
    print(10, user)
    image = Image.query.get(1)
    print(11, image, image.user)


if __name__ == '__main__':
    # init_database()
    manager.run()
