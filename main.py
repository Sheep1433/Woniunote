from flask import Flask, abort, render_template
import os
from flask_sqlalchemy import SQLAlchemy
import pymysql


pymysql.install_as_MySQLdb()  # ModuleNotFoundError: No module named 'MySQLdb'

app = Flask(__name__, template_folder='template', static_url_path='/', static_folder='resource')
app.config['SECRET_KEY'] = os.urandom(24)

# 使用集成方式处理SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:1107@localhost:3306/woniunote?charset=utf8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # True: 跟踪数据库的修改，及时发送信号
# 实例化db对象
db = SQLAlchemy(app)


# 定义404错误页面
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error-404.html')


# 定义500错误页面
@app.errorhandler(500)
def server_error(e):
    return render_template('error-500.html')


# 定义全局拦截器，实现自动登录
@app.before_request
def before():
    from flask import request, session
    from module.users import Users
    url = request.path

    pass_list = ['/user', '/login', '/logout']
    if url in pass_list or url.endswith('.js') or url.endswith('.jpg'):
        pass

    elif session.get('islogin') is None:
        username = request.cookies.get('username')
        password = request.cookies.get('password')
        if username != None and password != None:
            user = Users()
            result = user.find_by_username(username)
            if len(result) == 1 and result[0].password == password:
                session['islogin'] = 'true'
                session['userid'] = result[0].userid
                session['username'] = username
                session['nickname'] = result[0].nickname
                session['role'] = result[0].role


# 通过自定义过滤器来重构truncate原生过滤器
def mytruncate(s, length, end='...'):
    count = 0
    new = ''
    for c in s:
        if count > length:
            break
        new += c
        if ord(c) <= 128:
            count += 0.5
        else:
            count += 1
    return new + end
# 注册mytruncate过滤器
# 前面一个mytruncate是在html的jinja2模板中调用的函数，后一个是此处的函数
app.jinja_env.filters.update(truncate=mytruncate)


# 定义文章类型函数，供模板页面直接调用
@app.context_processor
def gettype():
    type = {
        '1': 'Python开发',
        '2': '操作系统',
        '3': '测试开发',
        '4': '数据结构',
        '5': '计算机网络',
        '6': '数据库',
        '7': '容器化',
        '8': 'git学习'
    }
    return dict(article_type=type)


if __name__ == '__main__':
    from controller.index import *
    app.register_blueprint(index)

    from controller.user import *
    app.register_blueprint(user)

    from controller.article import *
    app.register_blueprint(article)

    from controller.favorite import *
    app.register_blueprint(favorite)

    from controller.comment import *
    app.register_blueprint(comment)

    from controller.ueditor import *
    app.register_blueprint(ueditor)

    from controller.admin import *
    app.register_blueprint(admin)

    from controller.ucenter import *
    app.register_blueprint(ucenter)

    from controller.elasticsearchtry import *
    app.register_blueprint(elasticsearchtry)

    app.run(host="0.0.0.0", port=5000, debug=True)
