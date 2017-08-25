# coding=utf-8
"""
A part of User modeling.
Author: Biao Chang, changb110@gmail.com, from University of Science and Technology of China
created at 2017/8/6.
"""
import re
import sys

temp = "想做/ 兼_职/学生_/ 的 、加,我Q：  1 5.  8 0. ！！？？  8 6 。0.  2。 3     有,惊,喜,哦"
temp = temp.decode("utf8")
string = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）]+".decode("utf8"), "".decode("utf8"), temp)
print string

import pynlpir  # 引入依赖包

print sys.getdefaultencoding()
reload(sys)
sys.setdefaultencoding('utf-8')

pynlpir.open()  # 打开分词器
s = """职位描述 岗位职责：  1、 根据公司要求完成JAVA语言复杂功能模块的前后台开发；  2、 独立完成中小型产品的系统级技术方案设计； 
    3、 负责对初中级程序员进行辅导，检查程序员代码的规范、质量；  任职要求：  1、3年以上Java开发经验； 2、 熟练的掌握 struts spring hibernate开源框架的开发；
    3、 掌握orcale/mysql等数据库相关技术；
    4、 了解如下技术以及专业技能：Ajax，Jquery，PostgreSQL，Linux，Android，Tomcat，Jboss，GlassFish，mongodb，redis，hadoop，webservice，lucene，nodejs，JBPM，Ngnix，MySQL集群
    5、 有大中型企业工作经验者优先。"""
print s.lower()
s = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）]+".decode("utf8"), "".decode("utf8"), s)
print s
r = pynlpir.segment(s, pos_english=False, pos_tagging=False)  # 默认打开分词和词性标注功能
print r[1].encode('utf-8')
print r

import MySQLdb

conn = MySQLdb.connect(
    host='172.16.46.10',
    port=3306,
    user='root',
    passwd='123456',
    db='weibo', charset='utf8'
)
cur = conn.cursor()
result = cur.execute("SELECT * FROM userprofile limit 5")
print result
for r in cur.fetchall():
    print r

cur.close()
conn.commit()
conn.close()