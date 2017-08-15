# coding=utf-8
"""
A part of Source Detection.
Author: Biao Chang, changb110@gmail.com, from University of Science and Technology of China
created at 2017/8/10.
"""

import chardet

f = open('F:/changbiao/DATA/job.csv', 'r')
l = f.readline()
print l
l = f.readline()
print l
l = f.readline()
print l
l = f.readline()
print l
print chardet.detect(l)

i = 0
while l.__len__()>0:
    l = f.readline()
    i += 1
print i