# coding=utf-8
"""
A part of online Recruitment Market Analysis.
Author: Biao Chang, changb110@gmail.com, from University of Science and Technology of China
created at 2017/9/4.
"""

import time
import cPickle
import numpy as npy
import data
import lda


class Experiment:
    from_file = False

    def __init__(self):
        self.data_source = data.Data()
        self.training_posts, self.test_posts = self.data_source.split_data_for_lda(from_file=self.from_file)

    def training(self, topic_num, alpha, beta, n_iter=1500):
        self.topic_num = topic_num
        self.alpha = alpha
        self.beta = beta
        self.model = lda.LDA(topic_num, n_iter=n_iter, random_state=1, alpha=alpha, eta=beta)
        self.model.fit(self.training_posts)

    def test(self):
        company2word = npy.dot(self.model.doc_topic_,self.model.topic_word_)
        log_company2word = npy.log(company2word)
        ll = npy.sum(log_company2word*self.test_posts)
        print 'log likelihood = ', ll, ' perplexity=', npy.exp(-ll/npy.sum(self.test_posts))
        return ll

    def save_model(self):
        cPickle.dump(self.model, open('../data/model-lda-t%sa%sb%s.data'%(self.topic_num,self.alpha,self.beta), 'w'))

    def load_model(self):
        self.model = cPickle.load(file('../data/model-lda-t%sa%sb%s.data'%(self.topic_num,self.alpha,self.beta), 'r'))

if __name__ == '__main__':
    # alpha = 50.0 / topic_num
    s = time.time()
    e = Experiment()
    end = time.time()
    print 'Time cost of initialization: ', end - s
    alpha = 0.5
    beta = 0.1
    topic_nums = [10,50,100]
    topic_nums = [150,200,250,300]
    for k in topic_nums:
        s = time.time()
        e.training(k, alpha, beta, n_iter=1000)
        e.test()
        e.save_model()
        end = time.time()
        print 'Running time: ', end - s
    # cProfile.run('e.training(500)')
