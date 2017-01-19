import scipy.spatial

from dataset import *

__author__ = 'ustc'


class Algorithm:
    step_size_gd = 0.1
    epsilon_delta = 0.01
    epsilon_y = 0.001
    epsilon_loss_function = 0.01
    max_iteration = 10
    map_class_index = {}
    map_index_class = {}
    data = Dataset()
    debug = True

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
        Y = copy(Y0)
        mu = 1 / alpha - 1
        change = 10
        # w = self.data.getAdjacentMatrix(x,delta)
        # w = self.data.loadAdjacentMatrix()
        # S = self.getNormalizedMatrixByRow(w,m)
        loss_function = -1
        loss_d = array([0 for i in range(dim)])
        i = 0
        while change > self.epsilon_loss_function and i < 200:
            if self.debug:
                print '\ti=%d' % i
            # fix delta
            w = self.data.getAdjacentMatrix(x, delta)
            # w = self.data.loadAdjacentMatrix()
            row_sum_w = w.sum(axis=1)  # sum of each row
            for j in range(m):
                row_sum_w[j] = math.pow(row_sum_w[j], -0.5)
            D = diag(row_sum_w)
            S = dot(dot(D, w), D)  # normalize by rows
            # S_array = S
            S = mat(S)
            Y = (identity(m) - alpha * S).getI() * Y0
            print self.result(train, labels, Y)
            # normal = 1
            # while normal > self.epsilon_y:
            #     normal = linalg.norm(Y)
            #     Y = alpha * S * Y + (1 - alpha) * Y0
            #     normal = math.fabs(normal - linalg.norm(Y))
            # fix Y
            Y_D = dot(D, Y).A
            normal = 1
            # row_sum_w = mat(w).sum(axis=1)
            while normal > self.epsilon_delta:
                if self.debug:
                    print '\t\tdelta'
                normal = linalg.norm(delta)
                for d in range(dim):
                    # if self.debug:
                    # print '\t\t\td=%d'%d
                    kernel = self.data.loadKernel(d)
                    wij_d = w * kernel / math.pow(delta[d], 3) * scipy.spatial.distance.cdist(Y_D, Y_D,
                                                                                              'sqeuclidean')  # multiply element-by-element
                    loss_d[d] = wij_d.sum()
                    # for j in range(m):
                    #     for k in range(m):
                    #         f_d_similarity = Y_D[j]-Y_D[k]
                    #         loss_d[d] += wij_d[j][k]* dot(f_d_similarity,f_d_similarity)
                    del kernel, wij_d
                delta -= self.step_size_gd * loss_d
                normal = math.fabs(normal - linalg.norm(delta))
            # update
            new_loss = mu * linalg.norm(Y - Y0) / 2 + (w * scipy.spatial.distance.cdist(Y_D, Y_D, 'sqeuclidean')).sum()
            # for j in range(m):
            #     for k in range(m):
            #         f_d_similarity = Y_D[j]-Y_D[k]
            #         new_loss += w[j][k]* dot(f_d_similarity,f_d_similarity)
            change = math.fabs(new_loss - loss_function)
            loss_function = new_loss
            i += 1

        return i, self.result(train, labels, Y), delta

    def randomWalk_GD(self, labeled=3, alpha=0.99):
        x, labels, m, dim, count, c = self.data.loadData()
        delta = array([1.25 for i in range(dim)])
        avg_steps = 0
        avg_accuracy = 0
        for i in range(0, self.max_iteration):
            if self.debug:
                print '\t%d-th iteration' % i
            train = self.data.divideDataSet(count, labeled, m)
            Y0 = self.initializeY0(c, count, labels, m, train)
            p, q, delta = self.LGC_GD(x, m, dim, Y0, alpha, labels, train, delta)
            avg_steps += p
            avg_accuracy += q
        avg_steps /= self.max_iteration
        avg_accuracy /= self.max_iteration
        return avg_steps, avg_accuracy, delta

    def randomWalk(self, labeled=3, alpha=0.99):
        x, labels, m, dim, count, c = self.data.loadData()
        delta = [1.25 for i in range(dim)]
        # w = self.data.loadAdjacentMatrix()
        # w = random.rand(m,m)
        w = self.data.getAdjacentMatrix(x, delta)
        S = self.getNormalizedMatrixByRow(w, m)
        avg_steps = 0
        avg_accuracy = 0
        for i in range(0, self.max_iteration):
            train = self.data.divideDataSet(count, labeled, m)
            Y0 = self.initializeY0(c, count, labels, m, train)
            # random walk
            p, q = self.LGC(S, Y0, alpha, labels, train)
            avg_steps += p
            avg_accuracy += q
        avg_steps /= self.max_iteration
        avg_accuracy /= self.max_iteration
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

    def experiment(self):
        write = open('../result/run.log', 'w')
        start_time = time.time()
        steps, accuracy = 0, 0
        for num in range(3, 100, 5):
            steps, accuracy, delta = self.randomWalk_GD(num)
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
