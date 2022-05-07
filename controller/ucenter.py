from flask import Blueprint, render_template

from module.article import Article
from module.favorite import Favorite

ucenter = Blueprint("ucenter", __name__)

@ucenter.route('/ucenter')
def user_center():
    result = Favorite().find_my_favorite()
    return render_template('user-center.html', result=result)


@ucenter.route('/user/favorite/<int:favoriteid>')
def user_favorite(favoriteid):
    canceled = Favorite().switch_favorite(favoriteid)
    return str(canceled)


@ucenter.route('/user/post')
def user_post():
    return render_template('user-post.html')


@ucenter.route('/user/article')
def user_article():
    result = Article().find_by_userid()
    return render_template('system-myarticle.html', result=result)


