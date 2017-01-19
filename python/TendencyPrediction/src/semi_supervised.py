from multiprocessing.dummy import Pool

import scipy.spatial

import tool
from dataset import *

__author__ = 'ustc'


class Algorithm:
    step_size_gd = 0.2
    epsilon_delta = 0.05
    epsilon_y = 0.001
    epsilon_loss_function = 0.01
    trials = 10
    max_iteration = 200
    map_class_index = {}
    map_index_class = {}
    data = Dataset()
    debug = True
    pool = Pool(3)

    def __init__(self):
        i = 0

    def getNormalizedMatrixByRow222(self, w, m):
        """normalize w by row"""
        w = mat(w)
        row_sum_w = w.sum(axis=1)  # sum of each row
        D = tile(row_sum_w, (1, m))
        S = w.__truediv__(D)  # normalize by rows
        return S

    def getNormalizedMatrixByRow(self, w, m):
        """normalize w by row"""
        row_sum_w = w.sum(axis=1)  # sum of each row
        for i in range(m):
            row_sum_w[i] = math.pow(row_sum_w[i], -0.5)
        D = diag(row_sum_w)
        S = dot(dot(D, w), D)  # normalize by rows
        return mat(S)

    def initializeY0(self, c, count, labels, m, train):
        j = 0
        for i in count:
            self.map_class_index[i] = j
            self.map_index_class[j] = i
            j += 1
        Y0 = zeros((m, c))
        for i in train:
            Y0[i][self.map_class_index[labels[i]]] = 1
        Y0 = mat(Y0)
        return Y0

    def LGC(self, S, Y0, alpha, labels, train):
        """NIPS2004_Learning with local and global consistency"""
        Y = copy(Y0)
        i = 0
        Y = (identity(shape(Y0)[0]) - alpha * S).getI() * Y0
        # normal = 1
        # while normal > self.epsilon_y:
        #     normal = linalg.norm(Y)
        #     Y = alpha * S * Y + (1 - alpha) * Y0
        #     normal = math.fabs(normal - linalg.norm(Y))
        #     i += 1
        # print 'i=%d' % i
        return i, self.result(train, labels, Y)

    def LGC_GD(self, x, m, dim, Y0, alpha, labels, train, delta):
        """LGC learning hype-parameters with gradient descent"""
        c = shape(Y0)[1]
        mu = 1 / alpha - 1
        change = 10
        loss_function = -1
        loss_d = zeros((1, dim))[0]
        steps = 0
        tool.gc = c
        tool.gm = m
        tool.gx = x

        while change > self.epsilon_loss_function and steps < self.max_iteration:
            if self.debug:
                print '\tsteps=%d' % steps, loss_function, change
            # fix delta
            print '\tdelta_sum = ', delta.sum()
            w = self.data.getAdjacentMatrix(x, delta)
            # w = self.data.loadAdjacentMatrix()
            start_time = time.time()
            row_sum_w = w.sum(axis=1)  # sum of each row
            row_sum_w_inverse = power(row_sum_w, -0.5)
            D = diag(row_sum_w_inverse)
            S = dot(dot(D, w), D)  # normalize by rows
            S = mat(S)
            end_time = time.time()
            print '\tD running time:', (end_time - start_time) / 3600

            start_time = time.time()
            Y = copy(Y0)
            normal = 1
            while normal > self.epsilon_y:
                normal = linalg.norm(Y)
                Y = alpha * S * Y + (1 - alpha) * Y0
                normal = math.fabs(normal - linalg.norm(Y))
            end_time = time.time()
            print '\tY running time:', (end_time - start_time) / 3600

            # start_time = time.time()
            # Y2 = (identity(shape(Y0)[0])-alpha*S).getI()*Y0
            # end_time = time.time()
            # print '\tY running time:',(end_time-start_time)/3600, linalg.norm(Y2-Y)
            # print self.result(train, labels, Y2)

            # fix Y
            normal = -1
            term_change = 10
            while term_change > self.epsilon_delta:
                if self.debug:
                    print '\t\tdelta'
                start_time = time.time()
                w = self.data.getAdjacentMatrix(x, delta)
                row_sum_w = w.sum(axis=1)  # sum of each row
                row_sum_w_inverse = power(row_sum_w, -0.5)
                D = diag(row_sum_w_inverse)
                Y_D = dot(D, Y).A
                similarty_y_d = scipy.spatial.distance.cdist(Y_D, Y_D, 'sqeuclidean')

                tool.grow_sum_w = row_sum_w
                tool.gw = w
                tool.gdelta = delta
                tool.gsimilarty_y_d = similarty_y_d
                tool.gY_D = Y_D

                start_time = time.time()
                # result = array(self.pool.map(tool.calculateGradient, range(dim)))
                result = loss_d
                end_time = time.time()
                print '\t\t\trunning time:', (end_time - start_time) / 3600

                start_time = time.time()
                for d in range(dim):
                    loss_d[d] = tool.calculateGradient4(Y_D, similarty_y_d, c, delta, m, row_sum_w, w, x, d)
                end_time = time.time()
                print '\t\t\trunning time:', (end_time - start_time) / 3600, linalg.norm(result - loss_d)

                start_time = time.time()
                for d in range(dim):
                    loss_d[d] = tool.calculateGradient5(Y_D, similarty_y_d, c, delta, m, row_sum_w, w, x, d)
                end_time = time.time()
                print '\t\t\trunning time:', (end_time - start_time) / 3600, linalg.norm(result - loss_d)

                start_time = time.time()
                for d in range(dim):
                    loss_d[d] = tool.calculateGradient2(Y_D, similarty_y_d, c, delta, m, row_sum_w, w, x, d)
                end_time = time.time()
                print '\t\t\trunning time:', (end_time - start_time) / 3600, linalg.norm(result - loss_d)

                delta -= self.step_size_gd * loss_d
                term = (w * similarty_y_d).sum()
                term_change = math.fabs(normal - term)
                normal = term
                end_time = time.time()
                print '\t\t\trunning time:', (end_time - start_time) / 3600, normal, term_change

            # update
            new_loss = mu * ((linalg.norm(Y - Y0)) ** 2) / 2 + normal
            change = math.fabs(new_loss - loss_function)
            loss_function = new_loss
            steps += 1

        return steps, self.result(train, labels, Y), delta

    def randomWalk_GD(self, labeled=3, alpha=0.99, sigma=1.25):
        x, labels, m, dim, count, c = self.data.loadData()
        delta = array([sigma for i in range(dim)])
        avg_steps = 0
        avg_accuracy = 0
        for i in range(0, self.trials):
            if self.debug:
                print '\t%d-th trial' % i
            train = self.data.divideDataSet(count, labeled, m)
            Y0 = self.initializeY0(c, count, labels, m, train)
            p, q, delta = self.LGC_GD(x, m, dim, Y0, alpha, labels, train, delta)
            avg_steps += p
            avg_accuracy += q
        avg_steps /= self.trials
        avg_accuracy /= self.trials
        return avg_steps, avg_accuracy, delta

    def randomWalk(self, labeled=3, alpha=0.99, sigma=1.25):
        x, labels, m, dim, count, c = self.data.loadData()
        delta = [sigma for i in range(dim)]
        # w = self.data.loadAdjacentMatrix()
        # w = random.rand(m,m)
        w = self.data.getAdjacentMatrix(x, delta)
        S = self.getNormalizedMatrixByRow(w, m)
        avg_steps = 0
        avg_accuracy = 0
        for i in range(0, self.trials):
            train = self.data.divideDataSet(count, labeled, m)
            Y0 = self.initializeY0(c, count, labels, m, train)
            # random walk
            p, q = self.LGC(S, Y0, alpha, labels, train)
            avg_steps += p
            avg_accuracy += q
        avg_steps /= self.trials
        avg_accuracy /= self.trials
        return avg_steps, avg_accuracy, delta

    def result(self, train, labels, y):
        m = len(y)
        accuracy = 0
        for i in range(0, m):
            if i not in train:
                classified = array(argsort(-y[i][:]))[0][0]
                if self.map_index_class[classified] == labels[i]:
                    accuracy += 1
        accuracy = accuracy * 1.0 / (m - len(train))
        # print 'accuracy = %f'%accuracy
        return accuracy

    def sigma(self, num=10):
        write = open('../result/run-sigma-labeled-%d.log' % (num), 'w')
        print 'igma\taccuracy\n'
        self.trials = 100
        start_time = time.time()
        for sigma in range(4, 50, 1):
            steps, accuracy, delta = self.randomWalk(num, 0.99, sigma / 10.0)
            print '%f\t%f\n' % (sigma / 10.0, accuracy)
            write.write('%f\t%f\n' % (sigma / 10.0, accuracy))
        end_time = time.time()
        print 'running time: %f' % ((end_time - start_time) / 3600)
        write.close()

    def experiment(self):
        write = open('../result/run.log', 'w')
        start_time = time.time()
        steps, accuracy = 0, 0
        sigma = 3.25
        for num in range(3, 100, 5):
            steps, accuracy, delta = self.randomWalk_GD(num, 0.99, sigma)
            print 'labeled=%d, iteration steps=%d, accuracy=%f\n' % (num, steps, accuracy)
            write.write('labeled=%d, iteration steps=%d, accuracy=%f\n' % (num, steps, accuracy))
            for d in delta:
                write.write('%f\t' % d)
            write.write('\n')
        end_time = time.time()
        print 'running time: %f' % ((end_time - start_time) / 3600)
        write.close()


if __name__ == '__main__':
    model = Algorithm()
    model.experiment()
    # print model.randomWalk()
