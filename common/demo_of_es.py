from elasticsearch import Elasticsearch

es = Elasticsearch()
es.indices.create(index='posts', ignore=400)  # 1. 创建名为 posts 的Index
mapping = {
    'properties': {
        'content': {
            'type': 'text',
            'analyzer': 'ik_max_word',
            'search_analyzer': 'ik_max_word'
        }
    }
}

es.indices.put_mapping(index='posts', body=mapping)  # 2. 设置Mapping，每个文档有个 content 字段，它的类型是 text，词法分析器是 ik
es.index(index='posts', id=1, body={'content': '美国留给伊拉克的是个烂摊子吗'})  # 3. 插入文档，每个文档必须使用唯一的 id
es.index(index='posts', id=2, body={'content': '公安部：各地校车将享最高路权'})
es.index(index='posts', id=3, body={'content': '中韩渔警冲突调查：韩警平均每天扣1艘中国渔船'})
es.index(index='posts', id=4, body={'content': '中国驻洛杉矶领事馆遭亚裔男子枪击 嫌犯已自首'})
es.search(index='posts', body={'query': {'match': {'content': '中国'}}})  # 4. 搜索 '中国'
body = {
    "query": {"match": {"content": "中国"}},
    "highlight": {
        "pre_tags": ["<tag1>", "<tag2>"],
        "post_tags": ["</tag1>", "</tag2>"],
        "fields": {
            "content": {}
        }
    }
}
es.search(index='posts',
          body=body)  # 5. 搜索 '中国'，同时高亮关键词，比如实际项目中可以替换 <tag1></tag1>
                        # 为 <span style='color: red; background: yellow;'></span>
es.indices.delete('posts')  # 6. 删除Index及里面的所有文档
