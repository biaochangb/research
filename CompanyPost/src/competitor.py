# coding=utf-8
"""
A part of online Recruitment Market Analysis.
Author: Biao Chang, changb110@gmail.com, from University of Science and Technology of China
created at 2017/9/2.
"""

import numpy as np

import MySQLdb
import cPickle
import scipy.spatial.distance


class Fig:
    """drawing figs according to the experiment results."""
    base_path = '../data/fig/'

    conn = MySQLdb.connect(host='172.16.46.211', port=3306, user='root', passwd='123456',
                           db='lagou', charset='utf8')  # database connection
    cursor = conn.cursor()  # database cursor
    chinese2englihs = {}
    stopwords = set()

    def __init__(self):
        r = self.cursor.execute("SELECT * FROM vocabulary_filter order by tid_new")
        vocabulary = []
        for row in self.cursor.fetchall():
            vocabulary.append(row[2])
        self.vocabulary = np.asarray(vocabulary)
        f = open('../data/chinese2englihs.txt', 'r')
        lines = f.readlines(-1)
        for line in lines:
            pair = line.split('\t')
            self.chinese2englihs[pair[0].decode('utf8')] = pair[1].strip()
        self.stopwords.add('priority')
        self.stopwords.add('communication')

    def competition_analysis_tfidf(self):
        r = self.cursor.execute("SELECT * FROM company_top1000 where cid<=1000 order by cid DESC")
        companies = []
        for c in self.cursor.fetchall():
            companies.append(c)
        print 'company num:', r, len(companies)
        tf_idf = np.asarray(cPickle.load(file('../data/tf_idf.data', 'r')))
        c = len(companies)
        n = 5  # top 5
        if n >= c:
            print 'n must be smaller than company_num.'
        d = scipy.spatial.distance.pdist(tf_idf, 'cosine')
        distances = scipy.spatial.distance.squareform(d)
        row_max = np.max(distances, axis=1)
        row_max = np.tile(row_max.reshape(c, 1), (1, c))
        distances /= row_max  # normalized by the max value in each row
        sorted_index = np.argsort(distances, axis=1)  # the i-th row is indices for the i-th company sorted by distances
        for i in range(c):
            print companies[i][1], companies[i][3],
            for j in range(1, n + 1):
                print companies[sorted_index[i, j]][1],
            print ''
            print '\t',
            for j in range(1, n + 1):
                print distances[i, sorted_index[i, j]],
            print ''

    def competition_analysis_rda(self, theta_file):
        r = self.cursor.execute("SELECT * FROM company_top1000 where cid<=1000 order by cid DESC")
        companies = []
        for company in self.cursor.fetchall():
            companies.append(company)
        print 'company num:', r, len(companies)
        theta = np.asarray(cPickle.load(file(theta_file, 'r')))
        c, k = theta.shape
        if c != r:
            print c, r
            exit()

        phi = np.asarray(cPickle.load(file('../data/result-phi-t120b0.1d0.5.data', 'r')))
        psi = np.asarray(cPickle.load(file('../data/result-psi-t120b0.1d0.5.data', 'r')))
        mu = np.asarray(cPickle.load(file('../data/result-mu-t120b0.1d0.5.data', 'r')))
        pi = np.asarray(cPickle.load(file('../data/result-pi-t120b0.1d0.5.data', 'r')))
        k, v = phi.shape

        # self.cursor.execute("SELECT * FROM company_terms_top1000 order by cid desc")
        # term_frequency = np.zeros((c, v))
        # cid = 0
        # for company in self.cursor.fetchall():
        #     c_term_frequency = eval(company[1])
        #     total = sum(c_term_frequency.values())
        #     for tid in c_term_frequency:
        #         term_frequency[cid, tid - 1] = c_term_frequency[tid] * 1.0 / total  # normalize
        #     cid += 1

        a0 = np.tile(psi[:, 0].reshape(c, 1), (1, v))
        a1 = np.tile(psi[:, 1].reshape(c, 1), (1, v))
        a2 = np.tile(psi[:, 2].reshape(c, 1), (1, v))
        "The probability to draw word j for company i"
        company2word = a0 * np.dot(theta, phi) + a1 * mu + a2 * pi
        # tf_idf = np.asarray(cPickle.load(file('../data/tf_idf.data', 'r')))
        # profile = np.log(company2word)*tf_idf
        # profile = np.log(company2word) * term_frequency
        # column_sum = np.sum(company2word, axis=0)
        # column_sum = np.tile(column_sum, (c, 1))
        profile = company2word

        cids = [993,972,929,939,968,982]
        print profile.shape
        d = scipy.spatial.distance.pdist(profile[cids], 'cosine')
        distances = scipy.spatial.distance.squareform(d)
        print 1-distances
        row_max = np.max(distances, axis=1)
        row_max = np.tile(row_max.reshape(6,1),(1,6))
        distances /= row_max   # normalized by the max value in each row
        print 1-distances
        exit()
        sorted_index = np.argsort(distances, axis=1)  # the i-th row is indices for the i-th company sorted by distances
        n = 5  # top 5
        for i in range(c):
            print companies[i][1], companies[i][3],
            for j in range(1, n + 1):
                print companies[sorted_index[i, j]][1],
            print ''
            print '\t',
            for j in range(1, n + 1):
                print distances[i, sorted_index[i, j]],
            print ''


    def __del__(self):
        self.cursor.close()
        self.conn.commit()
        self.conn.close()


if __name__ == '__main__':
    fig = Fig()
    # fig.number_of_posts_per_day()
    # fig.number_of_posts_per_company()
    # # fig.test()
    # fig.number_of_comanies_per_industry()
    # fig.perplexity()

    theta_file = '../data/result-theta-t120b0.1d0.5.data'
    phi_file = '../data/result-phi-t120b0.1d0.5.data'
    zx_file = '../data/result-zx-t120b0.1d0.5.data'
    # fig.topic_words_phi(phi_file, zx_file)
    # fig.company_topic_words(theta_file,phi_file,zx_file)
    psi_file = '../data/result-psi-t120b0.1d0.5.data'
    # fig.company_psi(psi_file)
    fig.competition_analysis_rda(theta_file)
    # fig.competition_analysis_tfidf()
