# coding=utf-8
"""
A part of User modeling.
Author: Biao Chang, changb110@gmail.com, from University of Science and Technology of China
created at 2017/8/7.
"""

import MySQLdb
import pynlpir


class Data:
    conn = MySQLdb.connect(host='localhost', port=3306, user='root', passwd='123456',
                           db='lagou', charset='utf8')  # database connection
    cursor = conn.cursor()  # database cursor
    stopwords = set()
    company_table = 'company_top1000'
    company_terms_table = 'company_terms_top1000'
    post_table = 'post'
    post_terms_table = 'post_terms_top1000'
    vocabulary_table = 'vocabulary'

    def __init__(self, database):
        # load stopwords
        f = open('../data/stopwords.txt', 'r')
        line = f.readline()
        for w in line.split('\t'):
            self.stopwords.add(w.strip().decode('utf-8'))

        pynlpir.open()

    def loadPost2db(self, post_file):
        f = open(post_file, 'r')
        output = open('F:/changbiao/DATA/job2.csv', 'w')
        line = f.readline()  # neglect the first line
        i = 0
        while line.__len__() > 0:
            i += 1
            if i % 1000 == 0:
                print i
            line = f.readline()
            fields = line.split(',')
            line = line.replace('\\', '/')
            output.write(line)
            # if fields[0]=='67':
            #     exit()

    def tokenize(self):
        vocabulary = {}
        vocabulary_new = {}
        companies = []
        try:
            r = self.cursor.execute("SELECT * FROM vocabulary")
            for term in self.cursor.fetchall():
                vocabulary[term[1]] = term[0]
            print 'current size of the vocabulary:', r

            r = self.cursor.execute("SELECT * FROM %s order by post_num asc" % self.company_table)
            print 'company num:', r
            i = 0
            for c in self.cursor.fetchall():
                i += 1
                if i%100 ==0:
                    print '---', i
                companies.append(c)
                c_terms = {}
                r = self.cursor.execute('SELECT pid,description FROM %s where cname="%s"' % (self.post_table, c[1]))
                print 'post num:', r
                for post in self.cursor.fetchall():
                    terms = pynlpir.segment(post[1], pos_english=False, pos_tagging=False)
                    terms_new = []
                    for t in terms:
                        t = t.strip()
                        if t not in self.stopwords:
                            if t not in vocabulary.keys():
                                vocabulary_new[t] = vocabulary.__len__()
                                vocabulary[t] = vocabulary_new[t]
                            terms_new.append(vocabulary[t])
                            if vocabulary[t] not in c_terms.keys():
                                c_terms[vocabulary[t]] = 0
                            c_terms[vocabulary[t]] += 1
                    sql = 'INSERT INTO %s(pid,cid,terms) VALUES(%s,%s,"%s")' % (
                        self.post_terms_table, post[0], c[0], terms_new)
                    self.cursor.execute(sql)
                sql = 'INSERT INTO %s(cid,terms) VALUES(%s,"%s")' % (
                    self.company_terms_table, c[0], c_terms)
                self.cursor.execute(sql)
                self.conn.commit()
            param = []
            for t in vocabulary_new:
                param.append([vocabulary_new[t], t])
            sql = 'insert into vocabulary values(%s,%s)'
            self.cursor.executemany(sql, param)
            self.conn.commit()
            print 'current size of the vocabulary:', vocabulary.__len__()
        except Exception as e:
            print e
            self.conn.rollback()

    def extract_training_set(self, num):
        print  num


def __del__(self):
    self.cursor.close()
    self.conn.commit()
    self.conn.close()


if __name__ == '__main__':
    data = Data('weibo')
    # data.loadPost2db('F:/changbiao/DATA/job.csv')
    data.extract_training_set(1000)
    data.tokenize()
