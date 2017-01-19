# coding:utf-8
__author__ = 'bchang'

from Dataset import *
from NAR import *


class ARMA:
    """
        AutoRegressive–Moving-Average model
    """
    max_order = 20
    lbd = 7
    nar = NAR()

    def crossValidation(self, views, n_Day, serials_episodes_records, n_fold, type=0):
        q_min = 0
        p_min = 0
        rmse_min = 1000
        w_min = 0
        for q in range(2, self.max_order):
            for p in range(2, self.max_order):
                # print p,q
                w, rmse = self.run(p, q, views, n_Day, serials_episodes_records, n_fold, type)
                # print rmse
                # print p,q,rmse
                if rmse < rmse_min:
                    q_min = q
                    p_min = p
                    rmse_min = rmse
                    w_min = w
        # print p_min,q_min,w_min,rmse_min
        return p_min, q_min, w_min, rmse_min

    def run(self, p, q, views, n_Day, serials_episodes_records, n_fold, type=0):
        # p,w, rmse = self.nar.crossValidation(views,n_Day,serials_episodes_records, n_fold)
        w, rmse = self.nar.run(p, views, n_Day, serials_episodes_records, n_fold, type)
        if type == 0:
            x, epsilon = self.getRegressionMatrix_s(p, q, w, views, n_Day, serials_episodes_records)
        else:
            x, epsilon = self.getRegressionMatrix_m(p, q, w, views, n_Day, serials_episodes_records)
        # print x.shape,epsilon.shape
        # for e in epsilon:
        #     print e
        rmse = 0
        w = 0
        for k in range(1, n_fold + 1):
            training_x, test_x = divideDataset(x, n_fold, k)
            training_epsilon, test_epsilon = divideDataset(epsilon, n_fold, k)
            temp_w = self.training(training_x, training_epsilon)

            t, temp_x = self.getKernelMatrix(test_x)
            phi = hstack([temp_x, test_epsilon])
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

    def training(self, x, epsilon):
        t, temp_x = self.getKernelMatrix(x)
        phi = hstack([temp_x, epsilon])
        A = dot(phi.T, phi)
        A += self.lbd * identity(A.shape[0])
        w = linalg.inv(A) * dot(phi.T, t)
        return w

    def getRegressionMatrix_s(self, p, q, w, views, n_Day, serials_episodes_records):
        """
        get the Regression Matrix when predicting in the single time interval
        :param p: order of AR
        :param q: order of MA
        :param w: coefficients(w0,w1,....,wp)
        :param views: raw popularity data(serial*episode*time)
        :param n_Day: # predict the popularity during the n-th time interval, range: 0,1,2,.....
        serials_episodes_records: the number of records of each episode of every serial
        """
        teleplay_num = len(serials_episodes_records)

        s1, s2, s3 = shape(views)
        temp_epsilon = array([zeros([s2, s3]) for i in range(s1)])
        # calculate residual errors
        for s in range(teleplay_num):
            episodes_num = len(serials_episodes_records[s])
            for nth in range(p, episodes_num):
                if serials_episodes_records[s][nth + 1] < n_Day:
                    break
                instance = views[s, nth - p:nth + 1, n_Day]  # t-p,...,t-2,t-1,t
                if instance.min() == 0:
                    continue
                row_max = instance.max()
                instance = instance * 1.0 / row_max
                temp_epsilon[s][nth][0] = instance[-1] - (w[0] + dot(instance[:-1], w[1:]))

        # generate matrix
        x = []
        epsilon = []
        for s in range(teleplay_num):
            episodes_num = len(serials_episodes_records[s])
            for nth in range(p + q, episodes_num):
                if serials_episodes_records[s][nth + 1] < n_Day:
                    break
                instance = views[s, nth - p:nth + 1, n_Day]  # t-p,...,t-2,t-1,t
                if instance.min() == 0:
                    continue
                row_max = instance.max()
                instance = instance * 1.0 / row_max
                x.append(instance)
                epsilon.append(temp_epsilon[s, nth - q:nth, 0])

        return mat(x), mat(epsilon)

    def getRegressionMatrix_m(self, p, q, w, views, n_Day, serials_episodes_records):
        """
        get the Regression Matrix when predicting in the multiple time interval
        :param p: order of AR
        :param q: order of MA
        :param w: coefficients(w0,w1,....,wp)
        :param views: raw popularity data(serial*episode*time)
        :param n_Day: # predict the popularity during the n-th time interval, range: 0,1,2,.....
        serials_episodes_records: the number of records of each episode of every serial
        """
        teleplay_num = len(serials_episodes_records)
        l = int(math.floor(sqrt(2 * max([p, q]) + 1.1)))
        s1, s2, s3 = shape(views)
        temp_epsilon = array([zeros([s2, s3]) for i in range(s1)])
        # calculate residual errors
        for s in range(teleplay_num):
            episodes_num = len(serials_episodes_records[s])
            for nth in range(l, episodes_num):
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
                row_max = instance.max()
                instance = instance * 1.0 / row_max
                temp_epsilon[s][nth][0] = instance[-1] - (w[0] + dot(instance[:-1], w[1:]))

        # generate matrix
        x = []
        epsilon = []
        for s in range(teleplay_num):
            episodes_num = len(serials_episodes_records[s])
            for nth in range(p + q, episodes_num):
                if serials_episodes_records[s][nth + 1] < n_Day:
                    break
                instance = zeros([1, p + 1])[0, :]  # t-p,...,t-2,t-1,t
                instance[p] = views[s, nth, n_Day]
                row_e = zeros([1, q])[0, :]
                k = 1
                for i in range(1, l + l):
                    for j in range(0, i):
                        if k < (p + 1):
                            instance[p - k] = views[s, nth - i, 0]
                        if k < (q + 1):
                            row_e[q - k] = temp_epsilon[s, nth - i, 0]
                        if (k >= (p + 1)) and (k >= (q + 1)):
                            break;
                        k += 1
                if (instance.min() == 0) or (row_e.max() == 0):
                    continue
                row_max = instance.max()
                instance = instance * 1.0 / row_max

                x.append(instance)
                epsilon.append(row_e)
        # print x,'abc'
        return mat(x), mat(epsilon)
