import os

from flask import Blueprint, render_template, abort, jsonify, session, request

from module.article import Article
import math

from module.users import Users

index = Blueprint("index", __name__)

# 此处被重构做了静态化，在本模块底部
# @index.route('/')
# def home():
#     article = Article()
#     result = article.find_limit_with_users(0, 10)
#     total = math.ceil(article.get_total_count() / 10)  # 总页数
#
#     last, most, recommended = article.find_last_most_recommended()
#
#     return render_template('index.html', result=result, page=1, total=total,
#                            last=last, most=most, recommended=recommended)


# @index.route('/page/<int:page>')
# def paginate(page):
#     start = (page - 1) * 10
#     article = Article()
#     result = article.find_limit_with_users(start, 10)
#     total = math.ceil(article.get_total_count() / 10)  # 总页数
#     return render_template('index.html', result=result, page=page, total=total)


@index.route('/type/<int:type>-<int:page>')
def classify(type, page):
    article = Article()
    start = (page - 1) * 10
    result = article.find_by_type(type, start, 10)
    total = math.ceil(article.get_count_by_type(type) / 10)
    return render_template('type.html', result=result, page=page, total=total, type=type)


# @index.route('/search/<int:page>-<keyword>')
# def search(page, keyword):
#     keyword = keyword.strip()
#     if keyword is None or keyword == '' or '%' in keyword or len(keyword) > 10:
#         abort(404)
#
#     article = Article()
#     start = (page - 1) * 10
#     result = article.find_by_headline(keyword, start, 10)
#     total = math.ceil(article.get_count_by_headline(keyword) / 10)
#     return render_template('search.html', result=result, total=total, page=page, keyword=keyword)

# @index.route('/search/<int:page>-<keyword>')
# def search(page, keyword):
#     keyword = keyword.strip()
#     if keyword is None or keyword == '' or '%' in keyword or len(keyword) > 10:
#         abort(404)
#
#     article = Article()
#     start = (page - 1) * 10
#     result = article.find_by_headline(keyword, start, 10)
#     total = math.ceil(article.get_count_by_headline(keyword) / 10)
#     return render_template('search.html', result=result, total=total, page=page, keyword=keyword)


@index.route('/recommend')
def recommend():
    article = Article()
    # 返回的last等是一个列表，列表元素的类型为<class 'sqlalchemy.engine.row.Row'>，不可直接序列化，可能是SQLAlechemy更新导致的
    last, most, recommended = article.find_last_most_recommended()
    res = []
    last_list = []
    for i, headline in last:
        step = (i, headline)
        last_list.append(step)
    res.append(last_list)
    most_list = []
    for i, headline in most:
        step = (i, headline)
        most_list.append(step)
    res.append(most_list)
    recommended_list = []
    for i, headline in recommended:
        step = (i, headline)
        recommended_list.append(step)
    res.append(recommended_list)
    return jsonify(res)


# ============== Redis ================== #
# 重构index控制器中的代码，新增以下两个方法
from common.redisdb import redis_connect


@index.route('/redis')
def home_redis():
    red = redis_connect()
    # 获取有序集合article的总数量
    count = red.zcard('article')
    total = math.ceil(count / 10)
    # 利用zrevrange从有序集合中倒序取0-9共10条数据，即最新文章
    result = red.zrevrange('article', 0, 9)
    # 由于加载进来的每一条数据是一个字符串，需要使用eval函数将其转换为字典
    article_list = []
    for row in result:
        article_list.append(eval(row))

    return render_template('index-redis.html', article_list=article_list, page=1, total=total)


@index.route('/redis/page/<int:page>')
def paginate_redis(page):
    pagesize = 10
    start = (page - 1) * pagesize   # 根据当前页码定义数据的起始位置

    red = redis_connect()
    count = red.zcard('article')
    total = math.ceil(count / 10)
    result = red.zrevrange('article', start, start+pagesize-1)
    article_list = []
    for row in result:
        article_list.append(eval(row))
    # 将相关数据传递给模板页面，从模板引擎调用
    return render_template('index-redis.html', article_list=article_list, page=page, total=total)


#================== 静态化处理 ======================#
@index.route('/static')
def all_static():
    pagesize = 10
    article = Article()
    # 先计算一共有多少页，处理逻辑与分页接口一致
    total = math.ceil(article.get_total_count() / pagesize)
    # 遍历每一页的内容，从数据库中查询出来，渲染到对应页面中
    for page in range(1, total + 1):
        start = (page - 1) * pagesize
        result = article.find_limit_with_users(start, pagesize)

        # 将当前页面正常渲染，但不响应给前端，而是将渲染后的内容写入静态文件
        content = render_template('index.html', result=result, page=page, total=total)

        # 将渲染后的内容写入静态文件,其实content本身就是标准的HTML页面
        with open(f'./template/index-static/index-{page}.html', mode='w', encoding='utf-8') as file:
            file.write(content)

    return '文章列表页面分页静态化处理完成'  # 最后简单响应给前面一个提示信息


@index.route('/')
def home():
    # 判断是否存在该页面，如果存在则直接响应，否则正常查询数据库
    if os.path.exists('./template/index-static/index-1.html'):
        return render_template('index-static/index-1.html')

    # 下述代码跟之前版本保持不变，正常查询数据库
    article = Article()
    result = article.find_limit_with_users(0, 10)
    total = math.ceil(article.get_total_count() / 10)
    content = render_template('index.html', result=result, page=1, total=total)

    # 如果是第一个用户访问，而静态文件不存在，则生成一个
    with open('./template/index-static/index-1.html', mode='w', encoding='utf-8') as file:
        file.write(content)

    return content


@index.route('/page/<int:page>')
def paginate(page):
    # 判断是否存在该页面，如果存在则直接响应，否则正常查询数据库
    if os.path.exists(f'./template/index-static/index-{page}.html'):
        return render_template(f'index-static/index-{page}.html')

    # 下述代码跟之前版本保持不变，正常查询数据库
    article = Article()
    start = (page - 1) * 10
    result = article.find_limit_with_users(start, 10)
    total = math.ceil(article.get_total_count() / 10)
    content = render_template('index.html', result=result, page=page, total=total)

    # 如果是第一个用户访问，而静态文件不存在，则生成一个
    with open(f'./template/index-static/index-{page}.html', mode='w', encoding='utf-8') as file:
        file.write(content)

    return content
