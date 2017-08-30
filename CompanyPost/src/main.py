# coding=utf-8
"""
A part of online Recruitment Market Analysis.
Author: Biao Chang, changb110@gmail.com, from University of Science and Technology of China
created at 2017/8/23.
"""
import numpy as npy
import cProfile
import data
import recruitment_market_analysis as rma


class Experiment:
    def __init__(self, topic_num, alpha, beta, delta):
        self.data_source = data.Data()
        posts, vocabulary = self.data_source.load_recruitment_post_data(from_file=False)
        vocabulary_size = len(vocabulary)
        company_num = len(posts)
        self.posts = posts
        self.vocabulary = vocabulary
        self.topic_num = topic_num

        # symmetric priors
        self.alpha = npy.ones(topic_num) * alpha
        self.beta = beta * npy.ones(vocabulary_size)

        self.delta = delta * npy.ones(3)
        self._lambda = self.data_source.load_recruitment_competitors_data(5, from_file=False)
        self.gamma = self.data_source.load_recruitment_industry_data(from_file=False)

        self.rma = rma.RMA(vocabulary, topic_num, self.alpha, self.beta, self.gamma, self.delta, self._lambda)

    def training(self, iter_num=100):
        self.rma.fit(self.posts, iter_num)


if __name__ == '__main__':
    topic_num = 100
    alpha = 50.0 / topic_num
    beta = 0.1
    delta = 0.5
    e = Experiment(topic_num, alpha, beta, delta)
    # e.training(100)
    cProfile.run('e.training(200)')