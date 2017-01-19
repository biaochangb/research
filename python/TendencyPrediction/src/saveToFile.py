# coding:utf-8
import time

import data_preprocess as dp

if __name__ == '__main__':
    start_time = time.time()

    preprocess = dp.DataPreprocess()
    preprocess.saveDTWtoFile(1)
    # preprocess.saveDTWtoFile(3)
    # preprocess.saveDTWtoFile(5)
    # preprocess.saveDTWtoFile(7)
    # preprocess.saveDTWtoFile(10)
    # print preprocess.readDTWfromFile()
    # preprocess.k_mediods('../result/normalized-teleplay-series-clustering.txt',3)
    # print preprocess.DTW([1,1,2,3,4,3,2,1],[2,2,1,1,3,1])
    # print preprocess.DTW([2,2,1,1,3,1],[1,1,2,3,4,3,2,1])
    end_time = time.time()
    print 'running time: %f \r\n' % ((end_time - start_time) / 3600)
