# coding:utf-8

import math
import pickle
import time
from collections import Counter

from numpy import *

__author__ = 'ustc'


class Dataset:
    adjacent_matrix = '../result/adjacent-matrix150.pickle'
    # dataset_file = '../dataset/usps1-3-150.txt'
    dataset_file = '../dataset/usps1-3-all.txt'

    def saveDatasetToFile(self):
        read = open('../dataset/usps_train.jf')
        write = open('../dataset/usps1-3.txt')

    def loadData(self):
        print 'read data from %s' % (self.dataset_file)
        read = open(self.dataset_file)
        lines = read.readlines()
        feature_num = 256
        x = zeros((shape(lines)[0], feature_num))
        labels = []
        i = 0
        for line_str in lines:
            line = line_str.strip().split('\t')
            x[i, :] = line[1:]
            labels.append(int(line[0]))
            i += 1
        m = shape(x)[0]
        dim = shape(x)[1]
        print m, dim
        count = Counter(labels)
        c = len(count)
        print count, c
        return x, labels, m, dim, count, c

    def GaussianDistance(self, x, y, delta):
        distance = 0
        i = 0
        for z in (x - y):
            distance += z * z / delta[i] / delta[i]
            i += 1
        distance = math.exp(-distance / 2)
        return distance

    def distance(self, x, y, delta):
        return self.GaussianDistance(x, y, delta)

    def getKernel(self, x, m, d):
        kernel = zeros((m, m))
        for i in range(0, m):
            for j in range(i + 1, m):
                kernel[i][j] = kernel[j][i] = (x[i][d] - x[j][d]) * (x[i][d] - x[j][d])
                # kernel[i][j] = kernel[j][i] = (x[i][d]-x[j][d])**2/math.pow(delta[d], 3)
        return kernel

    def saveKernel(self):
        x, labels, m, dim, count, c = self.loadData()
        for d in range(dim):
            print 'd=%d' % d
            write = open('../result/kernel/150/dim%d' % d, 'wb')
            kernel = self.getKernel(x, m, d)
            pickle.dump(kernel, write)
            write.close()

    def loadKernel(self, d):
        read = open('../result/kernel/150/dim%d' % d, 'rb')
        kernel = pickle.load(read)
        read.close()
        return kernel

    def getAdjacentMatrix(self, x, delta):
        # m = shape(x)[0]
        # x_normalized = x/delta
        # start_time = time.time()
        # print '\t getAdjacentMatrix'
        # w = scipy.spatial.distance.cdist(x_normalized, x_normalized, lambda u, v: exp(-((u-v)**2).sum()/2))
        # end_time = time.time()
        # print '\t w running time:',(end_time-start_time)/3600
        #
        # start_time = time.time()
        # w2 = exp(scipy.spatial.distance.cdist(x_normalized, x_normalized, lambda u, v: -((u-v)**2).sum()/2))
        # end_time = time.time()
        # print '\tw2 running time:',(end_time-start_time)/3600,linalg.norm(w-w2)
        # for i in range(m):
        #     w[i][i] = 0

        start_time = time.time()
        m = shape(x)[0]
        w2 = w = zeros((m, m))  # initialize the adjacent matrix
        for i in range(0, m):
            for j in range(i + 1, m):
                w[i][j] = w[j][i] = math.exp(-dot((x[i] - x[j]) / delta, (x[i] - x[j]) / delta) / 2)
                # w[i][j] = w[j][i] = self.distance(x[i], x[j],delta)
        end_time = time.time()
        print '\tw2 running time:', (end_time - start_time) / 3600, linalg.norm(w - w2)
        #
        # m = shape(x)[0]
        # w = zeros((m,m))    # initialize the adjacent matrix
        # for i in range(0,m):
        #     for j in range(i+1, m):
        #         w[i][j] = w[j][i] = math.exp(-dot((x[i]-x[j])/delta, (x[i]-x[j])/delta)/2)
        #         #w[i][j] = w[j][i] = self.distance(x[i], x[j],delta)
        return w

    def saveAdjacentMatrix(self):
        write = open(self.adjacent_matrix, 'wb')
        x, labels, m, dim, count, c = self.loadData()
        delta = [1.25 for i in range(dim)]
        w = self.getAdjacentMatrix(x, delta)
        pickle.dump(w, write)
        write.close()

    def loadAdjacentMatrix(self):
        print 'reading the adjacent matrix from a file'
        read = open(self.adjacent_matrix, 'rb')
        w = pickle.load(read)
        read.close()
        return w

    def divideDataSet(self, count, labeled, m):
        """generate the training and test_category set"""
        training = []
        c = len(count)
        index = []
        for i in range(m):
            index.append(i)

        size = 0  # 记录每个类别数据的大小
        for i in count:
            t = random.randint(size, size + count[i] - 1)
            index.remove(t)
            training.append(t)
            size += count[i]
        for i in range(0, labeled - c):
            t = random.randint(0, len(index) - 1)
            training.append(index[t])
            del index[t]
        return training


if __name__ == '__main__':
    dataset = Dataset()
    dataset.saveAdjacentMatrix()
    # dataset.LGC()
