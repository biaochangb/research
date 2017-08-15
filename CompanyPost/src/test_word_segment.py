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
string = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）]+".decode("utf8"), "".decode("utf8"),temp)
print string


import pynlpir  # 引入依赖包

print sys.getdefaultencoding()
reload(sys)
sys.setdefaultencoding('utf-8')

pynlpir.open()  # 打开分词器
s = '职位描述 回家吃饭 全中国最大家庭厨房共享平台！ 如果你没有听说过分享经济，你的生活一定很单调； 如果你没有参与过分享经济，你的人生一定很枯燥； 如果你用过Airbnb/Uber/滴滴专车……你会发现，世界真精彩！ 好吧，废话了一大堆，只是想告诉你---- 我们正在做的是： 餐饮类的Airbnb！ 吃货们狂爱的“家庭厨房”共享！你要做的是： 线上线下结合，服务于商家端用户，为商家活跃度、商家订单数、复购率负责。 你需要： 有活动组织能力，同时能做做培训讲师^^提升商家活跃度以及自运营能力。 有棒棒哒文案功底，懂点摄影那是更好。咱们的自媒体还指着你来运营哪^^ 如果，你天生就是点子王^^亲和力超强^^热爱美食^^，那就别废话了，赶紧丢简历过来吧！ 厄厄对了~ 有O2O经验的优先哦^^棒棒哒！'  # 实验文本
print s
s = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）]+".decode("utf8"), "".decode("utf8"),s)
print s
r = pynlpir.segment(s, pos_english=False, pos_tagging=False)  # 默认打开分词和词性标注功能
print r[1].encode('utf-8')
print r

import MySQLdb
conn= MySQLdb.connect(
        host='172.16.46.10',
        port = 3306,
        user='root',
        passwd='123456',
        db ='weibo', charset='utf8'
        )
cur = conn.cursor()
result = cur.execute("SELECT * FROM userprofile limit 5")
print result
for r in cur.fetchall():
    print r

cur.close()
conn.commit()
conn.close()


