# coding:utf-8
import time

from numpy import *

import data_preprocess as dp

x = array([[1, 2], [2, 3]])
y = array([[2.0, 2], [2, 3]])
print x * y

if __name__ == '__main__':
    start_time = time.time()

    preprocess = dp.DataPreprocess()
    # preprocess.k_mediods('../result/normalized-teleplay-series-clustering2.txt',3)
    # print preprocess.DTW([1,1,2,3,4,3,2,1],[2,2,1,1,3,1])
    # print preprocess.DTW([2,2,1,1,3,1],[1,1,2,3,4,3,2,1])
    x = array([([random.random()] * (3022)) for i in range(3022)])
    y = array([([random.random()] * (3022)) for i in range(3022)])
    print shape(x)
    m = 3
    x = array([[1, 2, 3], [2, 3, 4], [1, 2, 1]])
    w = mat([[1, 2, 3], [2, 3, 4], [1, 2, 1]])
    row_sum_w = w.sum(axis=1)  # sum of each row
    D = tile(row_sum_w, (1, m))
    S = w.__truediv__(D)  # normalize by rows
    print D
    print x.__truediv__(D)

    end_time = time.time()
    print 'running time: %f \r\n' % ((end_time - start_time) / 3600)
