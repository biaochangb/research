# coding:utf-8
__author__ = 'bchang'

import json
import re

import redis

import Event

listA = [0]
listB = listA
listB.append(1)
print listA


def is_ascii(s):
    return all(ord(c) < 128 for c in s)


def is_chinese(s):
    r = re.findall(ur'[\u4e00-\u9fff]+', s)
    return len(r) > 0


def isValid(keywords):
    """
    Keywords are not recognisable if they contain non-ASCII or non-chinese characters.
    """
    flag = True
    for w in keywords:
        if (not is_ascii(w)) and (not is_chinese(w)):
            flag = False
            break
    return flag


r = redis.Redis(host='10.0.109.33', port=8181, db=0)
e = Event.Event()
e.id = 123
print json.dumps(e.__dict__)
events_str = r.lrange("changbiao:event:evolution:twitter:sg:events", 0, -1)
print isValid(["abc", u"朋友", u"そして"])

m = 0
for e in events_str:
    event = eval(e)
    flag = 0
    for k in event['keywords']:
        if is_chinese(k):
            print k
            flag = 1
    if flag == 1:
        m += 1
        print "eeeeeeeeee"
print "m =", m

events_str = r.lrange("twitter:sg:event:python:detections2", 0, -1)

counts = {}
for event_str in events_str:
    event = eval(event_str)
    if len(event['keywords']) in counts:
        counts[len(event['keywords'])] += 1
    else:
        counts[len(event['keywords'])] = 1

print counts
# {3: 6562, 4: 4513, 5: 3559, 6: 2690, 7: 2323, 8: 1910, 9: 1560, 10: 26146}



sample = u'I am from 美国。We should be friends. 朋友。'
print re.findall(ur'[\u4e00-\u9fff]+', sample)
for n in re.findall(ur'[\u4e00-\u9fff]+', sample):
    print n
