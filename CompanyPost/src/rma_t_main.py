# coding=utf-8
"""
A part of online Recruitment Market Analysis.
Author: Biao Chang, changb110@gmail.com, from University of Science and Technology of China
created at 2017/8/23.
"""
import numpy as npy
import cProfile
import data
import rma_t as rma
import time


class Experiment:
    from_file = False

    def __init__(self, topic_num, alpha, beta, delta, company_num=10):
        self.data_source = data.Data()
        self.data_source.getTFIDF()
        training_posts, test_posts, vocabulary, companies = self.data_source.load_recruitment_post_data(company_num, from_file=False)
        vocabulary_size = len(vocabulary)
        self.training_posts = training_posts
        self.test_posts = test_posts
        self.vocabulary = vocabulary
        self.topic_num = topic_num

        # symmetric priors
        self.alpha = npy.ones(topic_num) * alpha
        self.beta = beta * npy.ones(vocabulary_size)

        self.delta = delta * npy.ones(2)
        self._lambda = self.data_source.load_recruitment_competitors_data(companies, 5, from_file=self.from_file)
        self.gamma = self.data_source.load_recruitment_industry_data(companies, from_file=self.from_file)

        self.rma = rma.RMA_T(vocabulary, topic_num, self.alpha, self.beta, self.gamma, self.delta, self._lambda)

    def training(self, iter_num=100):
        self.rma.fit(self.training_posts, iter_num)

    def test(self):
        self.rma.test(self.test_posts)

if __name__ == '__main__':
    topic_num = 100
    alpha = 50.0 / topic_num
    alpha =0.5
    beta = 0.1
    delta = 0.5
    # e = Experiment(topic_num, alpha, beta, delta, 994)
    s = time.time()
    e = Experiment(topic_num, alpha, beta, delta, 300)
    end = time.time()
    print 'Time cost of initialization: ',end-s
    e.training(10)
    e.test()
    # cProfile.run('e.training(500)')
