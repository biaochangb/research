# coding=utf-8
"""
A part of Source Detection.
Author: Biao Chang, changb110@gmail.com, from University of Science and Technology of China
created at 2017/8/10.
"""

import chardet
import re

regex = re.compile(
        r'(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)', re.IGNORECASE)
regex = re.compile(
        r'(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(/\S+)?', re.IGNORECASE)
s ='职位描述 http://202.38.64.10 职位描述 1.负责蘑菇街广告的相关优化、算法改进及策略研发； 2.负责蘑菇街用户/商品数据挖掘的核心技术研究与开发； 3.负责蘑菇街用户行为分析与反作弊研究。 职位要求 1.具有较强分析问题和解决问题能力； 2.具有大规模数据处理经验； 3.熟练掌握数据挖掘、机器学习和广告计算学相关算法； 4.具有非常扎实的数据结构和算法基础，至少会写一门脚本语言； 5.有国际算法竞赛获奖经历者优先； 6.具有搜索引擎、推荐系统或广告计算学相关项目或研究经验者优先。 我们的福利(不限于)： 1、 国家规定的五险一金及补充医疗保险，季度奖，年度奖，每年2次的加薪升职机会哦； 2、 各种带薪假期，每年的免费体检，出国outing ； 3、 人手配备一个mac,2k+的人体工程系椅子，代码写起来刷刷的； 4、 每天品种丰富的免费早餐和加班晚餐；无限制拿的零食、饮料； 5、 大楼里各种免费的娱乐设施：台球，乒乓，桌上足球，xbox ，按摩椅等等；还有免费酒吧，每天调个伏特加神马的也不错； 6、 部门每月的活动经费，方圆10公里内好吃的一网打尽； 7、 妹子比例远超50% (好吧，这个算是宅男福利，来个去年年会的各种蘑菇女神照：http://weibo.com/p/1005051773761872/weibo?profile_ftype=1&key_word=%E8%98%91%E8%8F%87%E8%A1%97&is_search=1#_0)； 8、 优秀人才丰厚的期权奖励； [蘑菇街新一轮融资的新闻:http://ec.donews.com/201406/2806127.shtm] [蘑菇街新大楼的新闻:http://mp.weixin.qq.com/s?__biz=MjY0ODY5MTg0MA==&mid=201571040&idx=5&sn=9fccaead9a0e7489c57adad7d35cd244&scene=2&from=timeline&isappinstalled=0#rd]'
print s
match = regex.match(s)
if match:
    print match.group()
r, n = regex.subn('',s)
print r,n

punctuation = ur'[^\u4e00-\u9fa5]'

description = re.sub(punctuation, " ".decode("utf8"), s.decode("utf8"))
print description

import unicodedata
s = 'ＳＯＨＯ１５ＪＱｕｅｒｙＣＳＳ3'
s = unicodedata.normalize('NFKC', s.decode('utf-8'))
print s

f = open('../data/stopwords.txt', 'r')
line = f.readlines(-1)
print line.__len__()

import numpy as npy
from scipy.spatial.distance import pdist, squareform
x = npy.array([[1,2],[2,3],[1,2]])
print x, x.shape
print pdist(x)
print squareform(pdist(x))

a = npy.ones(4)
print a/4, npy.random.randint(0, 5)
print x[0,0], x[0][1]

import math
print math.gamma(3.1)
p = [1,3,4]
b = npy.asarray(p)
print b*1.0/npy.sum(b)
y = x[1].copy()
y[0] = 100
print x,y

import time
time_start=time.time()
for i in range(100000):
        x[0,1] = 10
time_end=time.time()
print time_end-time_start

time_start=time.time()
for i in range(100000):
        x[0][1] = 10
time_end=time.time()
print time_end-time_start

a = npy.asarray([1,3,5,7])
b = npy.tile(a, (3,1))
print b, npy.sum(b,axis=1)
c = npy.asarray([[1,3,5,7],[1,3,5,8],[1,3,5,9]])
d = npy.tile(npy.sum(c,axis=1),(4,1)).transpose()
print c*1.0/d

import scipy.special
print a
print scipy.special.gamma(a), scipy.special.gammaln(a)
print scipy.special.gamma(0.8)

e = [1,3]
a[e] = 10
print a
x = npy.random.multinomial(1,[0.4,0.1,0.1,0.4])
print x==1, x.shape, x
a[x==1] = 1100
print a
x =  npy.random.multinomial(100000,npy.asarray([0.4,0.1,0.1,0.4]))
for e in x:
        print e

a = npy.arange(50)
time_start=time.time()
j = 0
for i in range(10000):
    j=0
    for aa in a:
        if aa == 25:
            break
        j += 1
time_end=time.time()
print time_end-time_start,j

time_start=time.time()
for i in range(10000):
    j = npy.where(a==25)[0][0]
time_end=time.time()
print time_end-time_start,j

b = npy.asarray([0,1,3,0,7,3,5])
hkv = npy.zeros(10)
x = npy.asarray([0,1,2,0,1,0,0])
c = b[npy.where(x==0)]

print c, npy.bincount(c)
hkv[b[npy.where(x==0)]] += 1
print  hkv

from operator import mul
print npy.arange(0.1, 5.1)
print reduce(mul, npy.arange(0.1, 5.1))

a = npy.asarray([1,2])
b = npy.asarray([2,5])
print a*b
