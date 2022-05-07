import socket                 # 引入Python的socket类


# s = socket.socket()
# s.connect(('127.0.0.1', 6379))   # 与Redis建立连接，并基于协议规则发送数据包
#
# s.send('*3\r\n'.encode())               # *3 表示发送的命令包含3个字符串
# s.send(b'$3\r\n')               # $3 表示接下来的字符串有3个字符
# s.send(b'set\r\n')
# s.send(b'$5\r\n')
# s.send(b'phone\r\n')
# s.send(b'$11\r\n')              # $11 表示接下来发的字符串有11个字符
# s.send(b'18812345678\r\n')
# r = s.recv(1024)               # 一条完整的命令发送完后接收Redis服务器响应
# print(r.decode())               # 输出 +OK 表示命令成功执行
#
# s.send(b'*2\r\n')
# s.send(b'$3\r\n')
# s.send(b'get\r\n')
# s.send(b'$5\r\n')
# s.send(b'phone\r\n')
# r = s.recv(1024)
# print(r.decode())               # 通过get命令读取变量phone的值
#
# import redis
#
# # 指定Redis服务器的IP地址，端口号和数据库进行连接
# red = redis.Redis(host='127.0.0.1', port=6379, db=0)
#
# # 使用连接池进行连接，推荐使用此方式
# pool = redis.ConnectionPool(host='127.0.0.1', port=6379, decode_responses=True, db=0)
# red = redis.Redis(connection_pool=pool)
#
# print(red.get('phone'))
#
# red.hmset(name='mykey', mapping={'addr':'成都孵化园', 'tel':'028-12345678', 'employee':200})
# red.hset(name='mykey', key='name', value='蜗牛学院')    # 新增一条哈希值到mykey中
# red.hsetnx(name='mykey', key='name', value='蜗牛学院2') # 在mykey中不存在name时新增
# dict = red.hgetall('mykey')            # 获取mykey的所有值
# print(dict)


# elasticsearch使用示范
from common.database import dbconnect
from module.users import Users

dbsession, md, DBase = dbconnect()

from elasticsearch import Elasticsearch

def get_data():
    from module.article import Article
    result = dbsession.query(Article.articleid, Article.headline, Article.content, Users.nickname).join(Users, Users.userid == Article.userid) \
        .filter(Article.hidden == 0, Article.drafted == 0, Article.checked == 1,
                ) \
        .order_by(Article.articleid.desc()).all()
    return result


def create_es_data():
    es=Elasticsearch()
    try:
        results = get_data()
        for row in results:
            message={
                "id":row[0],
                "headline":row[1],
                "content":row[2],
                "nickname": row[3]
            }
            es.index(index="article", doc_type="test-type", document=message)

    except Exception as e:
        print("Error:"+str(e))


if __name__=="__main__":
    create_es_data()

