# import json
# import math
#
# from flask import Blueprint, render_template
#
# from common.elasticsearch_query_class import elasticsearch
# from main import app
#
# elasticsearchtry = Blueprint('elasticsearchtry', __name__)
#
#
# @elasticsearchtry.route("/search/<int:page>-<content>")
# def get_es(page, content):
#     from module.article import Article
#     article = Article()
#     data = article.find_by_head_content(content)
#     # print(f"这里是{data}")
#     address_data=data["hits"]["hits"]
#     address_list=[]
#     start = (page - 1) * 10
#     for item in address_data:
#         address_list.append(item["_source"])
#     results=json.dumps(address_list,ensure_ascii=False)
#     total = math.ceil(len(address_list) / 10)
#     print(total)
#     print(results)
#     return render_template('search-es.html', results=results, total=total, start=start, page=page, content=content)
#     # return app.response_class(new_json, content_type="application/json", total=total, start=start)
#
#
import math

from flask import Blueprint, render_template

from common.elasticsearchfinal import add_to_index

elasticsearchtry = Blueprint('elasticsearchtry', __name__)


@elasticsearchtry.route("/search/<int:page>-<query>")
def get_es(page, query):
    from module.article import Article
    article = Article()
    start = (page - 1) * 10
    for post in article.find_all():  # 2. 为每篇文章添加对应的 ES 索引文档
        add_to_index("articles", post)
    total, results, highlights = article.find_by_head_content("articles", query, page, 10)
    total = math.ceil(total / 10)
    print(f"这里是{results}")
    return render_template('search-es.html', results=results, total=total, start=start, page=page, query=query)
    # return render_template('search-es.html', results=results, total=total, start=start, page=page, content=content)
    # return app.response_class(new_json, content_type="application/json", total=total, start=start)


