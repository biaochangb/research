# coding=utf-8
"""
A part of online Recruitment Market Analysis.
Author: Biao Chang, changb110@gmail.com, from University of Science and Technology of China
created at 2017/8/21.
"""

import cPickle
import time

import numpy as npy

import tools


class RMA:
    """The basic Recruitment Market Analysis model using collapsed Gibbs sampling"""

    def __init__(self, vocabulary, topic_num, alpha, beta, gamma, delta, _lambda):
        self.vocabulary = vocabulary
        self.vocabulary_size = len(vocabulary)
        self.topic_num = topic_num
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.delta = delta
        self._lambda = _lambda
        self.factor_num = 3

    def fit(self, data, iter_num):
        """fit the model to the data.
        Args:
            data: list-like, every element is a dict {pid:[tid]}
            iter_num: the number of Gibbs sampling iterations

        Returns:

        """
        self._initialize(data)
        # sample z and x by collapsed Gibbs sampling
        print 'topic_num:%s, alpha:%s, beta:%s, delta:%s' % (self.topic_num, self.alpha[0], self.beta[0], self.delta[0])
        print time.strftime('Current time: %Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        print '-- start the Gibbs sampling with iter_num = %s' % iter_num
        time0 = time.time()
        for i in range(0, iter_num):
            time1 = time.time()
            for cid in range(0, self.company_num):
                for pid in data[cid]:
                    p_terms = data[cid][pid]
                    self.draw_z(cid, pid, p_terms)
                    for t_index in range(0, len(p_terms)):
                        self.draw_x(cid, pid, t_index, p_terms[t_index])
            ll = self.log_complete_likelihood()
            time2 = time.time()
            print '%s-iteration: log_complete_likelihood = %s, running time: %ss' % (i, ll, time2 - time1)
        print 'Total running time: %ss' % (time2 - time0)
        self.estimate()

    def _initialize(self, data):
        """
        initialize x, z, and the counters.
        Args:
            data: list-like, every element is a dict {pid:[tid]}

        Returns:

        """
        company_num = len(data)  # the number of companies
        self.company_num = company_num
        self.tuk = npy.zeros((company_num, self.topic_num))
        self.gui = npy.zeros((company_num, self.factor_num))
        self.hkv = npy.zeros((self.topic_num, self.vocabulary_size))
        self.euv = npy.zeros((company_num, self.vocabulary_size))
        self.suv = npy.zeros((company_num, self.vocabulary_size))

        self.Z = []  # [{pid:z}]
        self.X = []  # [cid:{pid:[x]}]
        for cid in range(0, company_num):
            self.Z.append({})
            self.X.append({})
            for pid in data[cid]:
                z_p = npy.random.randint(0, self.topic_num)
                self.Z[cid][pid] = z_p
                self.tuk[cid, z_p] += 1
                self.X[cid][pid] = []
                for tid in data[cid][pid]:
                    x_t = npy.random.randint(0, self.factor_num)
                    self.X[cid][pid].append(x_t)
                    self.gui[cid, x_t] += 1
                    if x_t == 0:
                        self.hkv[z_p, tid] += 1
                    elif x_t == 1:
                        self.euv[cid, tid] += 1
                    else:
                        self.suv[cid, tid] += 1
                self.X[cid][pid] = npy.asarray(self.X[cid][pid])

        self.beta_sum = npy.sum(self.beta)
        self.gamma_row_sum = npy.sum(self.gamma, axis=1)
        self._lambda_row_sum = npy.sum(self._lambda, axis=1)

        self.hkv_row_sums = npy.sum(self.hkv, axis=1)
        self.euv_row_sums = npy.sum(self.euv, axis=1)
        self.suv_row_sums = npy.sum(self.suv, axis=1)

    def draw_z(self, cid, pid, terms):
        z_prev = self.Z[cid][pid]
        # exclude the pid-post
        self.tuk[cid, z_prev] -= 1
        tx0 = terms[npy.where(self.X[cid][pid] == 0)]
        tx0_counts = {}  # the number of times each term appearing in tx0
        for t in tx0:
            self.hkv[z_prev, t] -= 1
            self.hkv_row_sums[z_prev] -= 1
            if tx0_counts.has_key(t):
                tx0_counts[t] += 1
            else:
                tx0_counts[t] = 1

        # get the full conditional distribution according to the sampling equation.
        p_z = self.alpha + self.tuk[cid]
        # p_z /= npy.sum(p_z)
        sum_beta_hk = self.beta_sum + self.hkv_row_sums[z_prev]
        log_sum = -npy.sum(npy.log(npy.arange(sum_beta_hk, sum_beta_hk + len(tx0))))  # avoid OverflowError
        for t in tx0_counts:
            y = self.beta[t] + self.hkv[z_prev][t]
            log_sum += npy.sum(npy.log(npy.arange(y, y + tx0_counts[t])))
        p_z[z_prev] = npy.exp(log_sum)

        # sample the new topic of current post
        # z_new = tools.multinomial_sampling(p_z, self.topic_num)
        z_new = tools.random_sampling_for_multinomial(p_z, self.topic_num)
        self.Z[cid][pid] = z_new
        self.tuk[cid, z_new] += 1
        for t in tx0:
            self.hkv[z_new, t] += 1
            self.hkv_row_sums[z_new] += 1

    def draw_x(self, cid, pid, t_index, term):
        x_prev = self.X[cid][pid][t_index]
        z = self.Z[cid][pid]  # the topic of this post

        # exclude the current term
        self.gui[cid, x_prev] -= 1
        if x_prev == 0:
            self.hkv[z, term] -= 1
            self.hkv_row_sums[z] -= 1
        elif x_prev == 1:
            self.euv[cid, term] -= 1
            self.euv_row_sums[cid] -= 1
        else:
            self.suv[cid, term] -= 1
            self.suv_row_sums[cid] -= 1

        # get the full conditional distribution to draw its indicator
        p_x = self.delta + self.gui[cid]
        # p_x /= npy.sum(p_x)
        p_x[0] *= (self.beta[term] + self.hkv[z, term]) / (self.beta_sum + self.hkv_row_sums[z])
        p_x[1] *= (self.gamma[cid,term] + self.euv[cid,term]) / (self.gamma_row_sum[cid] + self.euv_row_sums[cid])
        p_x[2] *= (self._lambda[cid,term] + self.suv[cid, term]) / (self._lambda_row_sum[cid] + self.suv_row_sums[cid])

        """sample the new indicator of current term."""
        # x_new = tools.multinomial_sampling(p_x, 3)
        x_new = tools.random_sampling_for_multinomial(p_x,3)
        self.X[cid][pid][t_index] = x_new
        self.gui[cid, x_new] += 1
        if x_new == 0:
            self.hkv[z, term] += 1
            self.hkv_row_sums[z] += 1
        elif x_new == 1:
            self.euv[cid, term] += 1
            self.euv_row_sums[cid] += 1
        else:
            self.suv[cid, term] += 1
            self.suv_row_sums[cid] += 1

        return x_new

    def estimate(self):
        theta = npy.tile(self.alpha, (self.company_num, 1)) + self.tuk
        theta *= 1.0 / npy.tile(npy.sum(theta, axis=1), (self.topic_num, 1)).transpose()  # normalize
        phi = npy.tile(self.beta, (self.topic_num, 1)) + self.hkv
        phi *= 1.0 / npy.tile(npy.sum(phi, axis=1), (self.vocabulary_size, 1)).transpose()  # normalize
        mu = self.gamma + self.euv
        mu *= 1.0 / npy.tile(npy.sum(mu, axis=1), (self.vocabulary_size, 1)).transpose()
        psi = npy.tile(self.delta, (self.company_num, 1)) + self.gui
        psi *= 1.0 / npy.tile(npy.sum(psi, axis=1), (self.factor_num, 1)).transpose()  # normalize
        pi = self._lambda + self.suv
        pi *= 1.0 / npy.tile(npy.sum(pi, axis=1), (self.vocabulary_size, 1)).transpose()  # normalize

        self.theta = theta
        self.phi = phi
        self.mu = mu
        self.psi = psi
        self.pi = pi

        f = open('../data/results.data', 'w')
        cPickle.dump(theta, f)
        cPickle.dump(phi, f)
        cPickle.dump(mu, f)
        cPickle.dump(psi, f)
        cPickle.dump(pi, f)
        f.close()

    def log_complete_likelihood(self):
        """Calculate the complete log likelihood, log p(w,z,x), given the hyper-parameters.
        """
        l = 0
        ldelta_f_alpha = tools.log_delta_function(self.alpha)
        ldelta_f_beta = tools.log_delta_function(self.beta)
        ldelta_f_delta = tools.log_delta_function(self.delta)
        ldelta_f_lambda = tools.log_delta_function(self._lambda)
        ldelta_f_gamma = tools.log_delta_function(self.gamma)
        for cid in range(0, self.company_num):
            l += tools.log_delta_function(self.alpha + self.tuk[cid]) + tools.log_delta_function(
                self.delta + self.gui[cid]) - ldelta_f_alpha - ldelta_f_delta
            l += tools.log_delta_function(self.gamma[cid] + self.euv[cid]) - tools.log_delta_function(self.gamma[cid])
            l += tools.log_delta_function(self._lambda[cid] + self.suv[cid]) - tools.log_delta_function(self._lambda[cid])
        for k in range(0, self.topic_num):
            l += tools.log_delta_function((self.beta + self.hkv[k])) - ldelta_f_beta

        return l


if __name__ == '__main__':
    rma = RMA()
    rma.fit()
