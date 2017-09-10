# coding=utf-8
"""
A part of online Recruitment Market Analysis.
Author: Biao Chang, changb110@gmail.com, from University of Science and Technology of China
created at 2017/9/2.
"""

import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
from matplotlib.transforms import blended_transform_factory
from collections import OrderedDict

import MySQLdb
import cPickle
import lda.datasets
from wordcloud import WordCloud, STOPWORDS
import random
import scipy.spatial.distance

import plotly.plotly as py
import plotly.tools as tls
import seaborn as sns
import matplotlib.cm as cm

def my_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    # return "hsl(0, 0%%, %d%%)" % random.randint(60, 100)
    return "#3A5FCD"


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
        f = open('../data/chinese2englihs.txt','r')
        lines = f.readlines(-1)
        for line in lines:
            pair = line.split('\t')
            self.chinese2englihs[pair[0].decode('utf8')] = pair[1].strip()
        self.stopwords.add('priority')
        self.stopwords.add('communication')

    def perplexity(self):
        methods = ['TMRDA','TMRDA-H','TMRDA-T','LDA']
        p = [605.2164493,613.9806323,619.6238275,2103.891295]

        ind = np.arange(len(methods))  # the x locations for the groups
        width = 0.35  # the width of the bars

        fig, ax = plt.subplots()
        rects1 = ax.bar(ind,p, color='r')

        # add some text for labels, title and axes ticks
        ax.set_ylabel('Scores')
        ax.set_title('Scores by group and gender')
        ax.set_xticks(ind + width / 2)
        ax.set_xticklabels(methods)
        plt.show()

    def word_cloud(self, words, file=''):
        # lower max_font_size
        wordcloud = WordCloud(font_path='C:/Windows/Fonts/ARIALUNI.TTF',background_color='white',
                              color_func=my_color_func, width=2000, height=2000).generate_from_frequencies(words)
        fig = plt.figure()
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.tight_layout()
        # plt.show()
        # fig.savefig('../data/fig/word-cloud2.png')
        plt.savefig(file,bbox_inches='tight')

    def company_psi(self, psi_file):
        psi = np.asarray(cPickle.load(file(psi_file, 'r')))
        c,f = psi.shape
        print c,f
        cids = np.arange(1,c+1)
        fig, ax = plt.subplots(figsize=(12, 6))
        # line1 = ax.plot(cids, psi[:,0], label='IBR',linewidth=1)
        # line2 = ax.plot(cids, psi[:,1], label='IT',linewidth=1)
        # line3 = ax.plot(cids, psi[:,2], label='HC',linewidth=1)

        line1 = ax.plot(cids, psi[:,0], label='Business Requirements',linewidth=1)
        line2 = ax.plot(cids, psi[:,1], label='Industry Trends',linewidth=1)
        line3 = ax.plot(cids, psi[:,2], label='Homogeneity',linewidth=1)

        ax.set_ylim([0,1])
        plt.xlabel('Sorted Company ID', fontsize=25)
        plt.ylabel('Weight', fontsize=25)
        # plt.title('Scores by group and Category')
        plt.xticks(fontsize=25)
        plt.yticks(fontsize=25)  # change the num axis size
        # leg = ax.legend(fontsize=20)
        leg = plt.legend(loc=1, ncol=5, mode="expand", borderaxespad=0., fontsize=20)
        # get the individual lines inside legend and set line width
        for line in leg.get_lines():
            line.set_linewidth(4)

        plt.tight_layout()
        plt.show()
        fig.savefig('../data/fig/company_factors_weight.pdf')


    def competition_analysis_tfidf(self):
        r = self.cursor.execute("SELECT * FROM company_top1000 where cid<=1000 order by cid DESC")
        companies = []
        for c in self.cursor.fetchall():
            companies.append(c)
        print 'company num:', r, len(companies)
        tf_idf = np.asarray(cPickle.load(file('../data/tf_idf.data', 'r')))
        c = len(companies)
        n = 5   # top 5
        if n >= c:
            print 'n must be smaller than company_num.'

        cids = [993,972,929,939,968,982]
        print tf_idf.shape
        d = scipy.spatial.distance.pdist(tf_idf[cids], 'cosine')
        distances = scipy.spatial.distance.squareform(d)
        print 1-distances
        row_max = np.max(distances, axis=1)
        print row_max
        row_max = np.tile(row_max.reshape(6,1),(1,6))
        distances /= row_max   # normalized by the max value in each row
        print 1-distances
        exit()

        sorted_index = np.argsort(distances,axis=1)  # the i-th row is indices for the i-th company sorted by distances
        for i in range(c):
            print companies[i][1], companies[i][3],
            for j in range(1, n + 1):
                print companies[sorted_index[i,j]][1],
            print ''
            print '\t',
            for j in range(1, n + 1):
                print distances[i, sorted_index[i,j]] ,
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
            print c,r
            exit()

        phi = np.asarray(cPickle.load(file('../data/result-phi-t120b0.1d0.5.data', 'r')))
        psi = np.asarray(cPickle.load(file('../data/result-psi-t120b0.1d0.5.data', 'r')))
        mu = np.asarray(cPickle.load(file('../data/result-mu-t120b0.1d0.5.data', 'r')))
        pi = np.asarray(cPickle.load(file('../data/result-pi-t120b0.1d0.5.data', 'r')))
        k,v = phi.shape


        self.cursor.execute("SELECT * FROM company_terms_top1000 order by cid desc")
        term_frequency = np.zeros((c,v))
        cid = 0
        for company in self.cursor.fetchall():
            c_term_frequency = eval(company[1])
            total = sum(c_term_frequency.values())
            for tid in c_term_frequency:
                term_frequency[cid, tid - 1] = c_term_frequency[tid] * 1.0 / total  # normalize
            cid += 1

        a0 = np.tile(psi[:,0].reshape(c,1),(1,v))
        a1= np.tile(psi[:,1].reshape(c,1),(1,v))
        a2= np.tile(psi[:,2].reshape(c,1),(1,v))
        "The probability to draw word j for company i"
        company2word = a0*np.dot(theta, phi) + a1*mu + a2*pi
        tf_idf = np.asarray(cPickle.load(file('../data/tf_idf.data', 'r')))
        # profile = np.log(company2word)*tf_idf
        profile = np.log(company2word)*term_frequency

        cids = [993,972,929,939,968,982]
        d = scipy.spatial.distance.pdist(profile[cids], 'cosine')
        distances = scipy.spatial.distance.squareform(d)
        row_max = np.max(distances, axis=1)
        row_max = np.tile(row_max.reshape(c,1),(1,c))
        distances /= row_max   # normalized by the max value in each row
        print distances
        exit()
        sorted_index = np.argsort(distances, axis=1)  # the i-th row is indices for the i-th company sorted by distances
        n = 5   # top 5
        for i in range(c):
            print companies[i][1], companies[i][3],
            for j in range(1, n + 1):
                print companies[sorted_index[i,j]][1],
            print ''
            print '\t',
            for j in range(1, n + 1):
                print distances[i, sorted_index[i,j]] ,
            print ''


    def company_topic_words(self, theta_file, phi_file, zx_file):
        print 'topic_words_phi'
        print self.vocabulary[:5]
        theta = np.asarray(cPickle.load(file(theta_file, 'r')))
        phi = np.asarray(cPickle.load(file(phi_file, 'r')))
        z, x = cPickle.load(file(zx_file, 'r'))
        c, topic_num = theta.shape
        print topic_num, c
        cid = 0    # baidu
        z_list = [z[cid][pid] for pid in z[cid]]
        z_counts = np.bincount(z_list)
        z_index_sorted_asc = np.argsort(z_counts)   # sorted by counts
        topk = 10
        topn = 50
        shift = 5
        words_eng  = set()
        print self.chinese2englihs
        for i in range(topk):
            k = z_index_sorted_asc[-1-i]
            word_index_sorted_asc = np.argsort(phi[k])   # sorted by the probability
            words = self.vocabulary[word_index_sorted_asc][-shift:-(topn+shift):-1]
            print('Topic %s, %s\t: %s'%(k,z_counts[k], ' '.join(words)))
            word_probability = {}
            for j in word_index_sorted_asc[-shift:-(topn+shift):-1]:
                # print self.vocabulary[j]
                word = self.chinese2englihs[self.vocabulary[j]]
                words_eng.add(word)
                word_probability[word] = phi[k,j]
            self.word_cloud(word_probability, '../data/fig/word-cloud-phi-cid%s-k%s.png'%(cid,k))
        # for w in words_eng:
        #     print w
        print len(words_eng)

    def topic_words_phi(self, phi_file, zx_file):
        print 'topic_words_phi'
        print self.vocabulary[:5]
        phi = np.asarray(cPickle.load(file(phi_file, 'r')))
        z, x = cPickle.load(file(zx_file, 'r'))
        c = len(z)
        topic_num, v = phi.shape
        print topic_num, v, c
        z_list = [z[cid][pid] for cid in range(c) for pid in z[cid]]
        z_counts = np.bincount(z_list)
        z_index_sorted_asc = np.argsort(z_counts)   # sorted by counts
        topk = 1
        topn = 50
        words_eng  = set()
        print self.chinese2englihs
        for i in range(topk):
            k = z_index_sorted_asc[-1-i]
            word_index_sorted_asc = np.argsort(phi[k])   # sorted by the probability
            words = self.vocabulary[word_index_sorted_asc][-1:-(topn+1):-1]
            print('Topic %s, %s\t: %s'%(k,z_counts[k], ' '.join(words)))
            word_probability = {}
            for j in word_index_sorted_asc[-1:-(topn+1):-1]:
                print self.vocabulary[j]
                word = self.chinese2englihs[self.vocabulary[j]]
                words_eng.add(word)
                word_probability[word] = phi[k,j]
            self.word_cloud(word_probability, '../data/fig/word-cloud-phi-k%s.png'%k)
        for w in words_eng:
            print w
        print len(words_eng)

    def __del__(self):
        self.cursor.close()
        self.conn.commit()
        self.conn.close()

    def test(self):
        linestyles = OrderedDict(
            [('solid', (0, ())),
             ('loosely dotted', (0, (1, 10))),
             ('dotted', (0, (1, 5))),
             ('densely dotted', (0, (1, 1))),

             ('loosely dashed', (0, (5, 10))),
             ('dashed', (0, (5, 5))),
             ('densely dashed', (0, (5, 1))),

             ('loosely dashdotted', (0, (3, 10, 1, 10))),
             ('dashdotted', (0, (3, 5, 1, 5))),
             ('densely dashdotted', (0, (3, 1, 1, 1))),

             ('loosely dashdotdotted', (0, (3, 10, 1, 10, 1, 10))),
             ('dashdotdotted', (0, (3, 5, 1, 5, 1, 5))),
             ('densely dashdotdotted', (0, (3, 1, 1, 1, 1, 1)))])

        plt.figure(figsize=(10, 6))
        ax = plt.subplot(1, 1, 1)

        X, Y = np.linspace(0, 100, 10), np.zeros(10)
        for i, (name, linestyle) in enumerate(linestyles.items()):
            ax.plot(X, Y + i, linestyle=linestyle, linewidth=1.5, color='black')

        ax.set_ylim(-0.5, len(linestyles) - 0.5)
        print linestyles.keys()
        plt.yticks(np.arange(len(linestyles)), linestyles.keys())
        plt.xticks([])

        # For each line style, add a text annotation with a small offset from
        # the reference point (0 in Axes coords, y tick value in Data coords).
        # reference_transform = blended_transform_factory(ax.transAxes, ax.transData)
        # for i, (name, linestyle) in enumerate(linestyles.items()):
        #     ax.annotate(str(linestyle), xy=(0.0, i), xycoords=reference_transform,
        #                 xytext=(-6, -12), textcoords='offset points', color="blue",
        #                 fontsize=8, ha="right", family="monospace")

        plt.tight_layout()
        plt.show()

    def number_of_comanies_per_industry(self):
        industries = ['Information Security','Tourism','Healthcare','Life Service','Hardware','Advertising','Social Network',
                      'Education','Entertainment','Enterprise Service','Game','Data Service','O2O','Fiance','E-commerce','Mobile Internet']
        nums = [6,20,20,20,25,25,31,56,64,70,72,81,95,115,257,587]

        plt.rcdefaults()
        fig, ax = plt.subplots(figsize=(10, 7))
        ax.barh(range(len(nums)), nums, align='center',color='#3A5FCD', ecolor='black')
        ax.invert_yaxis()  # labels read top-to-bottom
        plt.xlabel('Number of Companies', fontsize=20)
        plt.xticks(fontsize=20)
        plt.yticks(np.arange(len(industries)), industries, fontsize=20)
        ax.set_ylim(-1,16)

        # fig, ax = plt.subplots(figsize=(10, 8))
        # ax.bar(range(0,len(nums)),nums,color='#3A5FCD')
        # plt.ylabel('Number of companies', fontsize=25)
        # plt.xticks(np.arange(len(industries))+0.5, industries, fontsize=25,rotation=90)
        # plt.yticks(fontsize=25)
        plt.tight_layout()
        plt.show()
        fig.savefig(self.base_path+'number_of_comanies_per_industry.pdf')

    def number_of_posts_per_company(self):
        y = np.loadtxt('../data/number_of_posts_per_company.txt')
        x = range(1,len(y)+1)
        # fig, ax = plt.subplots()
        # ax.plot(x, y, color='#3A5FCD', linewidth=2)
        print y.shape
        fig, ax = plt.subplots()
        # ax.hist(y, bins=[-10, 0,10,100,1000,2000,2500],color='red', linewidth=2)
        ax.hist(y, bins=1000, color='#3A5FCD')
        ax.set_xlim(0, 100)
        plt.xlabel('Number of Job Postings', fontsize=25)
        plt.ylabel('Number of Companies', fontsize=25)
        plt.xticks(fontsize=25)
        plt.yticks(fontsize=25)
        plt.tight_layout()
        plt.show()
        fig.savefig(self.base_path+'number_of_posts_per_company.pdf')

    def number_of_posts_per_day(self):
        years = mdates.YearLocator()  # every year
        months = mdates.MonthLocator()  # every month
        yearsFmt = mdates.DateFormatter('%Y')

        f = open('../data/number_of_posts_per_day.txt', 'r')
        lines = f.readlines(-1)
        x = []
        y = []
        datemin = datetime.datetime(9999, 1, 1)
        datemax = datetime.datetime(1, 1, 1)
        for line in lines:
            d,n = line.split('\t')
            d = datetime.datetime.strptime(d,'%Y/%m/%d')
            if d < datemin:
                datemin = d
            if d > datemax:
                datemax = d
            x.append(d)
            y.append(n)
        fig, ax = plt.subplots()
        ax.plot(x, y, color='#3A5FCD', linewidth=2)

        # format the ticks
        # ax.xaxis.set_major_locator(years)
        # ax.xaxis.set_major_formatter(yearsFmt)
        # ax.xaxis.set_minor_locator(months)

        ax.set_xlim(datemin, datemax)
        ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
        # ax.grid(True)

        # rotates and right aligns the x labels, and moves the bottom of the
        # axes up to make room for them
        fig.autofmt_xdate()

        plt.xlabel('Date', fontsize=25)
        plt.ylabel('Number of Job Postings', fontsize=25)
        # plt.title('Scores by group and Category')

        plt.xticks(fontsize=25)
        plt.yticks(fontsize=25)  # change the num axis size
        plt.tight_layout()
        plt.show()

        fig.savefig(self.base_path+'number_of_posts_per_day.pdf')

    def heatmap(self):

        rda = np.asarray( [[ 1.,0.44275077,0.08996832,0.05097737,0.05147542,0.],
     [ 0.49889342,1.,0.07416633,0.22477057,0.21493708,0.],
     [ 0.45122752,0.37914789,1.,0.15806962,0.24172798,0.],
     [ 0.32027036,0.38253938,0.,1.,0.55673654,0.31879002],
     [ 0.24567348,0.30572005,0.,0.50783234,1.,0.27649872],
     [ 0.3969743,0.32941291,0.,0.42646862,0.45138922,1.]])

        tf_idf = np.asarray([[ 1.,0.17184747,0.12164535,0.,0.03331166,0.01734349],
     [ 0.16683602,1.,0.05364767,0.04491571,0.03979023,0.],
     [ 0.15046604,0.090205,1.,0.04937981,0.,0.01813224],
     [ 0.,0.0506605,0.01712974,1.,0.1184358,0.07072743],
     [ 0.06503076,0.07688287,0.,0.1473618,1.,0.1169047 ],
     [ 0.03203517,0.02087602,0.,0.08462098,0.1005965,1.]])

        # n_points = 6
        # aa = np.linspace(0, 5, n_points)
        # bb = np.linspace(0, 5, n_points)
        # # a, b = np.meshgrid(b, a)
        # z = []
        # for a in aa:
        #     for b in bb:
        #         z.append(rda[5-a,5-b])
        # z = np.reshape(z, [len(aa), len(bb)])
        # fig, ax = plt.subplots()
        # im = ax.pcolormesh(aa, bb, rda)
        # fig.colorbar(im)
        # ax.axis('tight')
        # plt.show()

        data = rda
        fig, ax = plt.subplots()
        heatmap = ax.pcolor(data)

        # put the major ticks at the middle of each cell, notice "reverse" use of dimension
        ax.set_yticks(np.arange(data.shape[0])+0.5, minor=False)
        ax.set_xticks(np.arange(data.shape[1])+0.5, minor=False)

        column_labels = ['Baidu','Qihu360','Sougou','Jingdong','WeiPinHui','Alibaba']
        row_labels = ['Baidu','Qihu360','Sougou','Jingdong','WeiPinHui','Alibaba']
        ax.set_xticklabels(row_labels, minor=False)
        ax.set_yticklabels(column_labels, minor=False)
        plt.show()


    def heatmap2(self):
        rda = np.asarray([[1., 0.44275077, 0.08996832, 0.05097737, 0.05147542, 0.],
                          [0.49889342, 1., 0.07416633, 0.22477057, 0.21493708, 0.],
                          [0.45122752, 0.37914789, 1., 0.15806962, 0.24172798, 0.],
                          [0.32027036, 0.38253938, 0., 1., 0.55673654, 0.31879002],
                          [0.24567348, 0.30572005, 0., 0.50783234, 1., 0.27649872],
                          [0.3969743, 0.32941291, 0., 0.42646862, 0.45138922, 1.]])

        tf_idf = np.asarray([[1., 0.17184747, 0.12164535, 0., 0.03331166, 0.01734349],
                             [0.16683602, 1., 0.05364767, 0.04491571, 0.03979023, 0.],
                             [0.15046604, 0.090205, 1., 0.04937981, 0., 0.01813224],
                             [0., 0.0506605, 0.01712974, 1., 0.1184358, 0.07072743],
                             [0.06503076, 0.07688287, 0., 0.1473618, 1., 0.1169047],
                             [0.03203517, 0.02087602, 0., 0.08462098, 0.1005965, 1.]])
        np.random.seed(0)
        sns.set()
        uniform_data = np.random.rand(10, 12)
        ax = sns.heatmap(uniform_data)
        plt.show()

    def heatmap3(self):
        fig, axes = plt.subplots(figsize=(6, 5))

        data = np.asarray([[1,0.4104056,0.37466474,0.28806062,0.3117765,0.30040813],
                [0.4104056,1,0.33030706,0.32412783,0.32050075,0.29234291],
                [0.37466474,0.33030706,1,0.30025596,0.26390787,0.27725487],
                [0.28806062,0.32412783,0.30025596,1,0.37237973,0.33841427],
                [0.3117765,0.32050075,0.26390787,0.37237973,1,0.3499605],
                [0.30040813,0.29234291,0.27725487,0.33841427,0.3499605,1]])
        # data = np.ma.masked_greater(data, 1)
        ax = axes
        # im = ax.pcolormesh(data, edgecolors='white', linewidths=1,antialiased=True)
        im = ax.pcolormesh(data, cmap=cm.gray_r, edgecolors='white', linewidths=1,antialiased=True)
        # fig.colorbar(im)
        # ax.patch.set(hatch='xx', edgecolor='black')

        column_labels = ['Baidu','Qihu360','Sougou','Jingdong','VIPSHOP','Alibaba']
        row_labels = ['Baidu','Qihu360','Sougou','Jingdong','VIPSHOP','Alibaba']
        ax.set_yticks(np.arange(data.shape[0])+0.5, minor=False)
        ax.set_yticklabels(column_labels, minor=False,fontdict={'fontsize':25})
        plt.xticks(np.arange(data.shape[0])+0.5, row_labels, fontsize=25, rotation=30)
        plt.tight_layout()
        # plt.show()
        fig.savefig('../data/fig/heatmap-tfidf2.pdf')

        fig, axes = plt.subplots(figsize=(7, 5))
        data = np.asarray([[1,0.96524737,0.94324623,0.94081457,0.94084563,0.93763539],
                [0.96524737,1,0.93579179,0.94623646,0.94555449,0.93064822],
                [0.94324623,0.93579179,1,0.91292798,0.92157989,0.8965805],
                [0.94081457,0.94623646,0.91292798,1,0.96140416,0.94068567],
                [0.94084563,0.94555449,0.92157989,0.96140416,1,0.94326295],
                [0.93763539,0.93064822,0.8965805,0.94068567,0.94326295,1]])
        # data = np.ma.masked_greater(data, 1)
        ax = axes
        # im = ax.pcolormesh(data, edgecolors='white', linewidths=1,antialiased=True)
        im = ax.pcolormesh(data, cmap=cm.gray_r , edgecolors='black', linewidths=1,antialiased=True)
        bar = fig.colorbar(im)
        bar.ax.tick_params(labelsize=20)
        ax.patch.set(hatch='xx', edgecolor='black')

        column_labels = ['Baidu','Qihu360','Sougou','Jingdong','VIPSHOP','Alibaba']
        row_labels = ['Baidu','Qihu360','Sougou','Jingdong','VIPSHOP','Alibaba']
        # ax.set_xticks(np.arange(data.shape[1])+0.5, minor=False)
        # ax.set_xticklabels(row_labels, minor=False,fontdict={'fontsize':20})
        ax.set_yticks(np.arange(data.shape[0])+0.5, minor=False)
        ax.set_yticklabels(column_labels, minor=False,fontdict={'fontsize':25})
        plt.xticks(np.arange(data.shape[0])+0.5, row_labels, fontsize=25, rotation=30)
        plt.tight_layout()
        plt.show()
        fig.savefig('../data/fig/heatmap-rda2.pdf')


if __name__ == '__main__':
    fig = Fig()
    fig.number_of_posts_per_day()
    fig.number_of_posts_per_company()
    # # fig.test()
    # fig.number_of_comanies_per_industry()
    # fig.perplexity()

    theta_file = '../data/result-theta-t120b0.1d0.5.data'
    phi_file = '../data/result-phi-t120b0.1d0.5.data'
    zx_file = '../data/result-zx-t120b0.1d0.5.data'
    # fig.topic_words_phi(phi_file, zx_file)
    # fig.company_topic_words(theta_file,phi_file,zx_file)
    psi_file = '../data/result-psi-t120a0.1b0.1d0.5.data'
    # fig.company_psi(psi_file)
    # fig.competition_analysis_rda(theta_file)
    # fig.competition_analysis_tfidf()
    # fig.heatmap()
    # fig.heatmap2()
    # fig.heatmap3()