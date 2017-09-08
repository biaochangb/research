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
from wordcloud import WordCloud
import random

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
        fig.savefig('../data/fig/word-cloud2.png')
        plt.savefig('../data/fig/word-cloud.png',bbox_inches='tight')

    def topic_words(self, phi_file, zx_file):
        print 'topic_words'
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
                if word == u'熟悉':
                    word = 'Familiar'
                word_probability[word] = phi[k,j]
            self.word_cloud(word_probability)
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
        plt.xlabel('Number of Job Posts', fontsize=25)
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
        plt.ylabel('Number of Job Posts', fontsize=25)
        # plt.title('Scores by group and Category')

        plt.xticks(fontsize=25)
        plt.yticks(fontsize=25)  # change the num axis size
        plt.tight_layout()
        plt.show()

        fig.savefig(self.base_path+'number_of_posts_per_day.pdf')

if __name__ == '__main__':
    fig = Fig()
    # fig.number_of_posts_per_day()
    # fig.number_of_posts_per_company()
    # # fig.test()
    # fig.number_of_comanies_per_industry()
    # fig.perplexity()

    phi_file = '../data/result-phi-t120b0.1d0.5.data'
    zx_file = '../data/result-zx-t120b0.1d0.5.data'
    fig.topic_words(phi_file,zx_file)