# coding=utf-8
"""
A part of User modeling.
Author: Biao Chang, changb110@gmail.com, from University of Science and Technology of China
created at 2017/8/6.
"""

import pynlpir  # 引入依赖包
pynlpir.open()  # 打开分词器
s = 'NLPIR分词系统前身为2000年发布的ICTCLAS词法分析系统，从2009年开始，为了和以前工作进行大的区隔，并推广NLPIR自然语言处理与信息检索共享平台，调整命名为NLPIR分词系统。'  # 实验文本
r = pynlpir.segment(s, pos_english=False, pos_tagging=False)  # 默认打开分词和词性标注功能
print r[1].encode('utf-8')
print r

import MySQLdb
conn= MySQLdb.connect(
        host='172.16.46.10',
        port = 3306,
        user='root',
        passwd='123456',
        db ='weibo',
        )
cur = conn.cursor()
result = cur.execute("SELECT * FROM userprofile limit 5")
print result
for r in cur.fetchall():
    print r

cur.close()
conn.commit()
conn.close()
