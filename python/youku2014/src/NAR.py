# coding:utf-8
__author__ = 'bchang'

from numpy import *

from Dataset import *


class NAR:
    """
    naive vector autoregression
    """
    max_order = 5
    lbd = 7

    def crossValidation(self, views, n_Day, serials_episodes_records, n_fold, type=0):
        p_min = 0
        rmse_min = 1000
        w_min = 0
        for p in range(4, self.max_order):
            w, rmse = self.run(p, views, n_Day, serials_episodes_records, n_fold, type)
            # print p,rmse
            if rmse < rmse_min:
                p_min = p
                rmse_min = rmse
                w_min = w
        return p_min, w_min, rmse_min

    def run(self, p, views, n_Day, serials_episodes_records, n_fold, type=0):
        if type == 0:
            x = self.getRegressionMatrix(p, views, n_Day, serials_episodes_records)
        else:
            x = self.getRegressionMatrix_m(p, views, n_Day, serials_episodes_records)
        rmse = 0
        w = 0
        for k in range(1, n_fold + 1):
            training_matrix, test_matrix = divideDataset(x, n_fold, k)
            temp_w = self.training(training_matrix)
            t, phi = self.getKernelMatrix(test_matrix)
            predicted = dot(phi, temp_w)
            rmse += RMSE(predicted, t)
            w += temp_w
        rmse /= n_fold
        # print rmse
        w /= n_fold
        return w, rmse

    def getKernelMatrix(self, x):
        m, d = shape(x)
        t = x[:, d - 1]  # target vector
        phi = ones([m, d])
        phi[:, 1:] = x[:, 0:(d - 1)]
        return t, phi

    def training(self, x):
        t, phi = self.getKernelMatrix(x)
        A = dot(phi.T, phi)
        A += self.lbd * identity(A.shape[0])
        w = linalg.inv(A) * dot(phi.T, t)
        return w

    def getRegressionMatrix(self, p, views, n_Day, serials_episodes_records):
        """
        :param p: order of AR
        :param views: raw popularity data(serial*episode*time)
        :param n_Day: # predict the popularity during the n-th time interval, range: 0,1,2,.....
        serials_episodes_records: the number of records of each episode of every serial
        """
        temp_x = []
        teleplay_num = len(serials_episodes_records)
        for s in range(teleplay_num):
            episodes_num = len(serials_episodes_records[s])
            for nth in range(p, episodes_num):
                if serials_episodes_records[s][nth + 1] < n_Day:
                    break
                instance = views[s, nth - p:nth + 1, n_Day]  # t-p,...,t-2,t-1,t
                if instance.min() == 0:
                    continue
                temp_x.append(instance)  # t-p,...,t-2,t-1,t
        x = mat(temp_x)
        # print x.shape
        row_max = x.max(1)
        x = x.__truediv__(tile(row_max, (1, shape(x)[1])))  # normalize by rows
        return x

    def getRegressionMatrix_m(self, p, views, n_Day, serials_episodes_records):
        """
        :param p: order of AR
        :param views: raw popularity data(serial*episode*time)
        :param n_Day: # predict the popularity during the n-th time interval, range: 0,1,2,.....
        serials_episodes_records: the number of records of each episode of every serial
        """
        temp_x = []
        teleplay_num = len(serials_episodes_records)
        l = int(math.floor(sqrt(2 * p + 1.1)))
        for s in range(teleplay_num):
            episodes_num = len(serials_episodes_records[s])
            for nth in range(1, episodes_num):
                if serials_episodes_records[s][nth + 1] < n_Day:
                    break
                instance = zeros([1, p + 1])[0, :]  # t-p,...,t-2,t-1,t
                instance[p] = views[s, nth, n_Day]
                k = 1
                for i in range(1, l + l):
                    for j in range(0, i):
                        if k >= (p + 1):
                            break
                        instance[p - k] = views[s, nth - i, n_Day + j]
                        k += 1
                if instance.min() == 0:
                    continue
                temp_x.append(instance)
                #     print temp_x
                # break
        x = mat(temp_x)
        # print x.shape
        row_max = x.max(1)
        x = x.__truediv__(tile(row_max, (1, shape(x)[1])))  # normalize by rows
        return x
