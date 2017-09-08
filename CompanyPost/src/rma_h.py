# coding=utf-8
"""
A part of online Recruitment Market Analysis.
Author: Biao Chang, changb110@gmail.com, from University of Science and Technology of China
created at 2017/8/21.
"""

import cPickle
import time
import math
import numpy as npy

import random
import tools


class RMA_H:
    """The basic Recruitment Market Analysis model with factors of individual business requirements,
    and homogeneity with competitors, using collapsed Gibbs sampling"""

    def __init__(self, vocabulary, topic_num, alpha, beta, gamma, delta, _lambda):
        self.vocabulary = vocabulary
        self.vocabulary_size = len(vocabulary)
        self.topic_num = topic_num
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.delta = delta
        self._lambda = _lambda
        self.factor_num = 2
        self.log_likelihoods = []

    def test(self, data):
        print 'start testing'
        c_num = len(data)
        a0 = npy.tile(self.psi[:,0].reshape(self.company_num,1),(1,self.vocabulary_size))
        # a1= npy.tile(self.psi[:,1].reshape(self.company_num,1),(1,self.vocabulary_size))
        a2= npy.tile(self.psi[:,1].reshape(self.company_num,1),(1,self.vocabulary_size))
        "The probability to draw word j for company i"
        # company2word = a0*npy.dot(self.theta, self.phi) + a1*self.mu + a2*self.pi
        company2word = a0*npy.dot(self.theta, self.phi) + a2*self.pi
        log_company2word = npy.log(company2word)
        ll = 0
        n = 0
        for cid, posts in enumerate(data):
            for pid in posts:
                p_terms = posts[pid]
                n += len(p_terms)
                ll += npy.sum(log_company2word[cid,p_terms])
        print 'log likelihood = ', ll, ' perplexity=', npy.exp(-ll/n)

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
                posts = [(cid, pid, data[cid][pid]) for pid in data[cid]]
                map(self.draw, posts)
                # for pid in data[cid]:
                #     p_terms = data[cid][pid]
                #     self.draw_z(cid, pid, p_terms)
                #     self.draw_x2(cid, pid, p_terms)
                # for t_index in range(0, len(p_terms)):
                #     self.draw_x(cid, pid, t_index, p_terms[t_index])

                # ll = self.log_complete_likelihood()
                # self.log_likelihoods.append(ll)
            ll = 0
            time2 = time.time()
            print '%s-iteration: log_complete_likelihood = %s, running time: %ss' % (i, ll, time2 - time1)
        print 'Total running time: %ss' % (time2 - time0)
        self.estimate()

    def draw(self, post):
        cid, pid, p_terms = post
        self.draw_z(cid, pid, p_terms)
        self.draw_x2(cid, pid, p_terms)

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
        # self.euv = npy.zeros((company_num, self.vocabulary_size))
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
                    # elif x_t == 1:
                    #     self.euv[cid, tid] += 1
                    else:
                        self.suv[cid, tid] += 1
                self.X[cid][pid] = npy.asarray(self.X[cid][pid])

        self.beta_sum = npy.sum(self.beta)
        self.gamma_row_sum = npy.sum(self.gamma, axis=1)
        self._lambda_row_sum = npy.sum(self._lambda, axis=1)

        self.hkv_row_sums = npy.sum(self.hkv, axis=1)
        # self.euv_row_sums = npy.sum(self.euv, axis=1)
        self.suv_row_sums = npy.sum(self.suv, axis=1)

    def draw_z(self, cid, pid, terms):
        Z = self.Z
        X = self.X
        tuk = self.tuk
        hkv = self.hkv
        hkv_row_sums = self.hkv_row_sums

        z_prev = Z[cid][pid]
        # exclude the pid-post
        tuk[cid, z_prev] -= 1
        tx0 = terms[npy.where(X[cid][pid] == 0)]
        size = len(tx0)
        tx0_counts = {}  # the number of times each term appearing in tx0
        hkv_row_sums[z_prev] -= size
        for t in tx0:
            hkv[z_prev, t] -= 1
            tx0_counts[t] = tx0_counts.get(t, 0) + 1

        # get the full conditional distribution according to the sampling equation.
        p_z = self.alpha + tuk[cid]
        # p_z /= npy.sum(p_z)
        sum_beta_hk = self.beta_sum + hkv_row_sums[z_prev]
        y = self.beta + hkv[z_prev]

        # prod = 1.0/npy.prod(npy.linspace(sum_beta_hk, sum_beta_hk + size - 1, size))
        # for t in tx0_counts:
        #     prod *= npy.prod(npy.linspace(y[t], y[t] + tx0_counts[t] - 1, tx0_counts[t]))
        # p_z[z_prev] *= prod

        log_sum = -npy.sum(npy.log(npy.linspace(sum_beta_hk, sum_beta_hk + size-1, size)))  # avoid OverflowError
        bb = [abc for t in tx0_counts for abc in npy.linspace(y[t], y[t] + tx0_counts[t]-1,tx0_counts[t])]
        log_sum += npy.sum(npy.log(bb))
        # for t in tx0_counts:
        #     ss = self.beta[t] + hkv[z_prev][t]
        #     log_sum += npy.sum(npy.log(npy.linspace(ss, ss+ tx0_counts[t] - 1, tx0_counts[t])))
        p_z[z_prev] *= math.exp(log_sum)

        # sample the new topic of current post
        # z_new = tools.multinomial_sampling(p_z, self.topic_num)
        z_new = tools.random_sampling_for_multinomial(p_z, self.topic_num)
        Z[cid][pid] = z_new
        tuk[cid, z_new] += 1
        hkv_row_sums[z_new] += size
        for t in tx0:
            hkv[z_new, t] += 1

    def draw_x2(self, cid, pid, p_terms):
        delta = self.delta
        beta = self.beta
        _lambda = self._lambda
        hkv = self.hkv
        suv = self.suv
        gui = self.gui
        hkv_row_sums = self.hkv_row_sums
        suv_row_sums = self.suv_row_sums
        beta_sum = self.beta_sum
        _lambda_row_sum = self._lambda_row_sum
        z = self.Z[cid][pid]  # the topic of this post
        X = self.X
        for t_index in range(0, len(p_terms)):
            term = p_terms[t_index]
            x_prev = X[cid][pid][t_index]

            # exclude the current term
            gui[cid, x_prev] -= 1
            if x_prev == 0:
                hkv[z, term] -= 1
                hkv_row_sums[z] -= 1
            else:
                suv[cid, term] -= 1
                suv_row_sums[cid] -= 1

            # get the full conditional distribution to draw its indicator
            p_x = delta + gui[cid]
            p_x[0] *= (beta[term] + hkv[z, term]) / (beta_sum + hkv_row_sums[z])
            p_x[1] *= (_lambda[cid, term] + suv[cid, term]) / (_lambda_row_sum[cid] + suv_row_sums[cid])

            """sample the new indicator of current term."""
            p_x /= sum(p_x)
            v = random.random()
            if v <= p_x[0]:
                x_new = 0
                hkv[z, term] += 1
                hkv_row_sums[z] += 1
            else:
                x_new = 1
                suv[cid, term] += 1
                suv_row_sums[cid] += 1
            X[cid][pid][t_index] = x_new
            gui[cid, x_new] += 1

    def draw_x(self, cid, pid, t_index, term):
        Z = self.Z
        X = self.X
        # tuk = self.tuk
        hkv = self.hkv
        # euv = self.euv
        suv = self.suv
        gui = self.gui
        hkv_row_sums = self.hkv_row_sums
        # euv_row_sums = self.euv_row_sums
        suv_row_sums = self.suv_row_sums

        x_prev = X[cid][pid][t_index]
        z = Z[cid][pid]  # the topic of this post

        # exclude the current term
        gui[cid, x_prev] -= 1
        if x_prev == 0:
            hkv[z, term] -= 1
            hkv_row_sums[z] -= 1
        # elif x_prev == 1:
        #     euv[cid, term] -= 1
        #     euv_row_sums[cid] -= 1
        else:
            suv[cid, term] -= 1
            suv_row_sums[cid] -= 1

        # get the full conditional distribution to draw its indicator
        p_x = self.delta + gui[cid]
        # p_x /= npy.sum(p_x)
        p_x[0] *= (self.beta[term] + self.hkv[z, term]) / (self.beta_sum + self.hkv_row_sums[z])
        # p_x[1] *= (self.gamma[cid,term] + self.euv[cid,term]) / (self.gamma_row_sum[cid] + self.euv_row_sums[cid])
        p_x[1] *= (self._lambda[cid,term] + self.suv[cid, term]) / (self._lambda_row_sum[cid] + self.suv_row_sums[cid])

        """sample the new indicator of current term."""
        # x_new = tools.multinomial_sampling(p_x, 3)
        # x_new = tools.random_sampling_for_multinomial(p_x,3)
        p_x /= sum(p_x)
        v = random.random()
        if v <= p_x[0]:
            x_new = 0
        else:
            x_new = 1
        X[cid][pid][t_index] = x_new
        gui[cid, x_new] += 1
        if x_new == 0:
            hkv[z, term] += 1
            hkv_row_sums[z] += 1
        # elif x_new == 1:
        #     euv[cid, term] += 1
        #     euv_row_sums[cid] += 1
        else:
            suv[cid, term] += 1
            suv_row_sums[cid] += 1

    def estimate(self):
        print self.log_likelihoods
        theta = npy.tile(self.alpha, (self.company_num, 1)) + self.tuk
        theta *= 1.0 / npy.tile(npy.sum(theta, axis=1), (self.topic_num, 1)).transpose()  # normalize
        phi = npy.tile(self.beta, (self.topic_num, 1)) + self.hkv
        phi *= 1.0 / npy.tile(npy.sum(phi, axis=1), (self.vocabulary_size, 1)).transpose()  # normalize
        # mu = self.gamma + self.euv
        # mu *= 1.0 / npy.tile(npy.sum(mu, axis=1), (self.vocabulary_size, 1)).transpose()
        psi = npy.tile(self.delta, (self.company_num, 1)) + self.gui
        psi *= 1.0 / npy.tile(npy.sum(psi, axis=1), (self.factor_num, 1)).transpose()  # normalize
        pi = self._lambda + self.suv
        pi *= 1.0 / npy.tile(npy.sum(pi, axis=1), (self.vocabulary_size, 1)).transpose()  # normalize

        self.theta = theta
        self.phi = phi
        # self.mu = mu
        self.psi = psi
        self.pi = pi

        f = open('../data/rmah-result-theta-t%sb%sd%s.data'%(self.topic_num, self.beta[0], self.delta[0]), 'w')
        cPickle.dump(theta.tolist(), f)
        f.close()
        f = open('../data/rmah-result-phi-t%sb%sd%s.data'%(self.topic_num, self.beta[0], self.delta[0]), 'w')
        cPickle.dump(phi.tolist(), f)
        f.close()
        # f = open('../data/result-mu-t%sb%sd%s.data'%(self.topic_num, self.beta[0], self.delta[0]), 'w')
        # cPickle.dump(mu.tolist(), f)
        # f.close()
        f = open('../data/rmah-result-psi-t%sb%sd%s.data'%(self.topic_num, self.beta[0], self.delta[0]), 'w')
        cPickle.dump(psi.tolist(), f)
        f.close()
        f = open('../data/rmah-result-pi-t%sb%sd%s.data'%(self.topic_num, self.beta[0], self.delta[0]), 'w')
        cPickle.dump(pi.tolist(), f)
        f.close()
        f = open('../data/rmah-result-loglikelihood-t%sb%sd%s.data'%(self.topic_num, self.beta[0], self.delta[0]), 'w')
        cPickle.dump(self.log_likelihoods, f)
        f.close()
        f = open('../data/rmah-result-zx-t%sb%sd%s.data'%(self.topic_num, self.beta[0], self.delta[0]), 'w')
        cPickle.dump((self.Z, self.X), f)
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
    rma = RMA_H()
    rma.fit()
