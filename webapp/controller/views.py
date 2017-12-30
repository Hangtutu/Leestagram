"""
@author: lihang
@time: 2017/12/26 11:31
@describe:
"""
from web import app, db
from flask import render_template, redirect, request, flash, get_flashed_messages, send_from_directory
from webapp.model.models import User, Image, Comment
import hashlib
import random
from flask_login import login_user, logout_user, current_user, login_required
import uuid, os, json
import smtplib
from email.mime.text import MIMEText


# index():首页遍历图片
@app.route('/')
def index():
    images = Image.query.order_by(db.desc(Image.id)).limit(10).all()
    return render_template('index.html', images=images)


# image():图片详情页,根据图片的id查询相应的图片
@app.route('/image/<int:image_id>')
@login_required  # 这里需要加权限,依旧使用Flask_Login的@login_required判断,如果未登录不允许访问image页面
def image(image_id):
    image = Image.query.get(image_id)
    if image is None:
        redirect('/')
    return render_template('pageDetail.html', image=image)


# reglogin():登录注册页
@app.route('/regloginpage/')
def reglogin():
    if current_user.is_authenticated:  # 如果当前用户已经登录,就转向首页
        return redirect('/')
    msg = ''
    for m in get_flashed_messages(with_categories=False, category_filter=['reglogin']):
        msg = msg + m  # 获取flash消息,显示消息内容(用户名或密码为空,用户已存在这类的内容)
    return render_template('login.html', msg=msg)


# redirect_with_msg():flash接口,所有想显示flash内容的地方都可以调用这个接口
def redirect_with_msg(target, msg, category):
    if msg is not None:
        flash(msg, category=category)
    return redirect(target)


# reg():注册入口
@app.route('/reg/', methods={'post', 'get'})
def reg():
    # request.args: GET 从地址栏获取参数
    # request.values: POST
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()
    if username == '' or password == '':
        return redirect_with_msg('/regloginpage/', u'用户名或密码为空', 'reglogin')
    user = User.query.filter_by(username=username).first()
    if user is not None:
        return redirect_with_msg('/regloginpage/', u'用户已存在', 'reglogin')
    # 加盐加密---随机生成的salt,在用户密码后加上11位随机数
    salt = '.'.join(random.sample('1234567890abcdefghigklmnopqrstvuwxyz', 10))
    m = hashlib.md5()  # 使用MD5进行加密
    m.update((password + salt).encode('utf-8'))
    # 这里需要加上encode,否则会报错:TypeError: Unicode-objects must be encoded before hashing
    user = User(username, m.hexdigest(), salt)
    db.session.add(user)
    db.session.commit()
    login_user(user)  # 使用的是Flask的Flask_Login的login_user()函数,自动登录user账户
    send_email(username)
    return redirect('/')


def send_email(useremail):
    msg_from = '3215758767@qq.com'  # 发送方邮箱
    passwd = 'fytuqdwnxufjdegj'  # 填入发送方邮箱的授权码
    msg_to = useremail  # 收件人邮箱

    subject = "LeeStagram"  # 主题
    content = "尊敬的LeeStagram用户:\n     您好,恭喜您注册成功!"  # 正文
    msg = MIMEText(content)
    msg['Subject'] = subject
    msg['From'] = msg_from
    msg['To'] = msg_to
    try:
        s = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 邮件服务器及端口号
        s.login(msg_from, passwd)
        s.sendmail(msg_from, msg_to, msg.as_string())
        print("发送成功")
    except s.SMTPException as e:
        print("发送失败")
    finally:
        s.quit()


# logout():退出当前用户
@app.route('/logout/')
def logout():
    logout_user()  # 使用Flask_Login 的logout_user()函数退出当前用户
    return redirect('/')


# login():登录入口
@app.route('/login/', methods={'get', 'post'})
def login():
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()
    user = User.query.filter_by(username=username).first()
    if username == '' or password == '':
        return redirect_with_msg('/regloginpage/', u'用户名或密码为空', 'reglogin')
    if user is None:
        return redirect_with_msg('/regloginpage/', u'用户名不存在', 'reglogin')
    m = hashlib.md5()
    m.update((password + user.salt).encode('utf-8'))
    if m.hexdigest() != user.password:
        return redirect_with_msg('/regloginpage/', u'用户密码错误', 'reglogin')
    login_user(user)
    # 这里在前端login.html页面中埋了一个隐藏字段,用于记录转入登录页前的页面,这样登录之后可以直接跳到该页面
    next = request.values.get('next')
    if next is not None and next.startswith('/'):  # 一般url都是以/开始
        return redirect(next)
    return redirect('/')


# profile():个人详情页
@app.route('/profile/<int:user_id>')
@login_required  # 这里也需要限制用户的权限
def profile(user_id):
    user = User.query.get(user_id)
    if user is None:
        redirect('/')
    # 个人详情页中的"更多"应该做成分页形式,
    paginate = Image.query.filter_by(user_id=user_id).order_by(db.desc(Image.id)).paginate(page=1, per_page=3,
                                                                                           error_out=False)
    return render_template('profile.html', user=user, has_next=paginate.has_next, images=paginate.items)


# user_images():(更多)按钮的后端接口,前端在profile.html中引用的profile.js和jquery.js是前端的接口
@app.route('/profile/images/<int:user_id>/<int:page>/<int:per_page>/')
def user_images(user_id, page, per_page):
    # 将所需要的字段以json形式返回
    paginate = Image.query.filter_by(user_id=user_id).order_by(db.desc(Image.id)).paginate(page=page, per_page=per_page)
    map = {'has_next': paginate.has_next}
    images = []
    for image in paginate.items:
        imgvo = {'id': image.id, 'url': image.url, 'comment_count': len(image.comments)}
        images.append(imgvo)
    map['images'] = images
    return json.dumps(map)


# upload():上传图片
@app.route('/upload/', methods={'post'})
def upload():
    file = request.files['file']  # 使用postman上传key为file的图片
    file_ext = ''  # 定义存储图片后缀的变量
    if file.filename.find('.') > 0:  # 如果filename中找到'.'的位置大于0,说明filename中存在'.'
        file_ext = file.filename.rsplit('.', 1)[1].strip().lower()  # 将文件后缀中'.'以后的部分切割并且去除左右空格和换行 变为小写
    if file_ext in app.config['ALLOWED_EXT']:  # 如果文件类型满足我们在配置文件app.conf中定义的类型
        file_name = str(uuid.uuid1()).replace('-', '') + '.' + file_ext  # 则将文件名修改为随机定义的uuid+'.'+文件后缀
        url = save_to_local(file, file_name)  # 调用函数将图片保存在本地,并且返回能够查询图片的url
        if url is not None:  # 如果url不是空的,则可以将图片保存到数据库中
            db.session.add(Image(url, current_user.id))
            db.session.commit()
    return redirect('/profile/' + str(current_user.id))


# save_to_local():将图片保存在本地磁盘中
def save_to_local(file, filename):
    save_dir = app.config['UPLOAD_DIR']
    file.save(os.path.join(save_dir, filename))
    return '/image/' + filename


# view_image():显示图片
@app.route('/image/<image_name>/')
def view_image(image_name):
    return send_from_directory(app.config['UPLOAD_DIR'], image_name)


# addcomment():添加评论
@app.route('/addcomment/', methods={'post'})
def addcomment():
    image_id = str(request.values['image_id'])  # 获取key为image_id的值
    content = request.values['content']  # 获取key为content的值
    comment = Comment(content, image_id, current_user.id)
    db.session.add(comment)
    db.session.commit()
    return json.dumps({"code": 0,  # 返回json,pageDetail.html触发引用detail.js文件
                       "id": comment.id,
                       "content": comment.content,
                       "username": comment.user.username,
                       "user_id": comment.user_id})


# index_images:评论的后端入口
@app.route('/index/images/<int:page>/<int:per_page>/')
def index_images(page, per_page):
    paginate = Image.query.order_by(db.desc(Image.id)).paginate(page=page, per_page=per_page, error_out=False)
    map = {'has_next': paginate.has_next}
    images = []
    for image in paginate.items:
        comments = []
        for i in range(0, min(2, len(image.comments))):
            comment = image.comments[i]
            comments.append({'username': comment.user.username,
                             'user_id': comment.user_id,
                             'content': comment.content})
        imgvo = {'id': image.id,
                 'url': image.url,
                 'comment_count': len(image.comments),
                 'user_id': image.user_id,
                 'head_url': image.user.head_url,
                 'created_date': str(image.created_date),
                 'comments': comments}
        images.append(imgvo)

    map['images'] = images
    return json.dumps(map)
