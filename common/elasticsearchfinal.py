from elasticsearch import Elasticsearch

from module.article import Article

es = Elasticsearch()


# obj传入的对象是数据模型类，如Article
def add_to_index(index, obj):
    if not es:
        return

    # 由于博客主要是中文的，所以使用 ik 中文分词插件。先要配置 Index 的 mapping
    if not es.indices.exists(index=index):  # 如果是第一次插入，Index 还没创建
        # 创建 Index
        es.indices.create(index=index, ignore=400)
        # IK 模板，这里假设每个字段都用 text 类型，如果你要修改，也可以通过 __searchable__ 传递过来
        chinese_field_config = {
            "type": "text",
            "analyzer": "ik_max_word",
            "search_analyzer": "ik_max_word"
        }

        properties = {}
        for field, _ in obj.__searchable__:
            properties[field] = chinese_field_config

        mapping = {
            "properties": properties
        }
        es.indices.put_mapping(index=index, body=mapping)

    # 插入新文档 (不管是不是第一次都要执行此步骤)
    payload = {}
    for field, _ in obj.__searchable__:
        payload[field] = getattr(obj, field)
    es.index(index=index, id=obj.articleid, body=payload)


from elasticsearch.exceptions import NotFoundError


#  从Index中删除文档
def remove_from_index(index, obj):
    if not es:
        return

    try:
        es.delete(index=index, id=obj.id)
    except NotFoundError:
        pass


# 从Index中搜索文档
def query_index(index, query, page, per_page, ids=None):
    '''
    index: ES Index 的名称，比如 posts
    query: 查询关键字，比如 '中国'
    ids: 指定的文档 ID 集合，比如 [8, 9]
    page: 匹配到的搜索项分页后，返回指定页
    per_page: 匹配到的搜索项分页，每页 per_page 条记录
    '''
    if not es:
        return 0, [], ''

    # 中文分词器 ik 会将 query 拆分成哪些查找关键字，前端将通过正则表达式来高亮这些词
    analyze_body = {
        "analyzer": "ik_max_word",
        "text": query
    }
    tokens = es.indices.analyze(index=index, body=analyze_body)
    highlights = '+'.join([item['token'] for item in tokens['tokens']])

    if ids:  # 搜索指定的 ids 中是否匹配关键它
        body = {
            "query": {
                "bool": {
                    "must": {
                        "multi_match": {
                            "query": query,
                            "fields": ["*"]
                        }
                    },
                    "filter": {
                        "ids": {
                            "values": ids
                        }
                    }
                }
            },
            "from": (page - 1) * per_page,
            "size": per_page
        }
    else:
        body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["*"]
                }
            },
            "from": (page - 1) * per_page,
            "size": per_page
        }

    # 匹配的记录, 如果不指定 size 默认每页 10 条，且只返回第 1 页，即最多只返回 10 条匹配到的记录
    search = es.search(index=index, body=body)

    # hits 列表中每个元素是一个元组: (ID, 得分)
    hits = [(int(hit['_id']), hit['_score']) for hit in search['hits']['hits']]

    return search['hits']['total']['value'], hits, highlights
