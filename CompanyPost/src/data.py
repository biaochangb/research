# coding=utf-8
"""
A part of User modeling.
Author: Biao Chang, changb110@gmail.com, from University of Science and Technology of China
created at 2017/8/7.
"""

import cPickle
import math
import re
import sys
import traceback
import numpy as npy
import scipy.spatial.distance
import MySQLdb
import pynlpir
import tools

reload(sys)
sys.setdefaultencoding('utf-8')


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
    punctuation = "[+-\.\!\/_,$%^*(+\"\'=]+|[+——！。？、~@#￥%……&*（）]+|[｛－｜｝｝＞～～±～＋￥×§¬ø[▽◆◇○◎●★☆♡►▎▌█╰╯╮╭⊙o⊙≧≦≥≤∩∞√−↓←※•​【ლ╹◡╹ლ)̈абвгдежзийклмфцчшщыюя]+".decode(
        "utf8")
    url_regex = re.compile(
        r'(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(/\S+)?', re.IGNORECASE)
    chinese_regex = re.compile(ur'[^\u4e00-\u9fa5]', re.IGNORECASE)

    def __init__(self):
        # load stopwords
        f = open('../data/stopwords.txt', 'r')
        lines = f.readlines(-1)
        for line in lines:
            self.stopwords.add(line.strip().decode('utf-8'))

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

    def filterPost(self):
        """delete urls and special characters"""
        try:
            r = self.cursor.execute("SELECT * FROM company  order by cid")
            print 'company num:', r
            i = 0
            for c in self.cursor.fetchall():
                i += 1
                if i % 100 == 0:
                    print '---', i
                r = self.cursor.execute('SELECT pid,description FROM %s where cname="%s"' % (self.post_table, c[1]))
                for post in self.cursor.fetchall():
                    description = post[1]
                    description, n = self.url_regex.subn('', description)
                    description = description.decode("utf8")
                    description = re.sub(self.punctuation, " ".decode("utf8"), description)
                    r = self.cursor.execute(
                        'UPDATE %s set description="%s" where pid=%s' % (self.post_table, description, post[0]))
                    # print post[0], post[1]
                    # print '--',description
                self.conn.commit()

        except Exception as e:
            traceback.print_exc()
            self.conn.rollback()

    def tokenize(self):
        vocabulary = {}
        companies = []
        try:
            r = self.cursor.execute("SELECT * FROM vocabulary")
            for term in self.cursor.fetchall():
                vocabulary[term[1]] = term[0]
            print 'current size of the vocabulary:', r

            r = self.cursor.execute("SELECT * FROM %s where cid<=1000 order by cid DESC" % self.company_table)
            print 'company num:', r
            i = 0
            for c in self.cursor.fetchall():
                i += 1
                if i % 100 == 0:
                    print '---', i
                companies.append(c)
                c_terms = {}
                r = self.cursor.execute('SELECT pid,description FROM %s where cname="%s"' % (self.post_table, c[1]))
                print '--post num:', r, c[0]
                for post in self.cursor.fetchall():
                    # print '\t', post[0], post[1]
                    # temp = post[1].decode("utf8")
                    # temp = re.sub(self.punctuation, "".decode("utf8"),temp)
                    # temp = unicodedata.normalize('NFKC', post[1].lower().decode("utf8")) # full width char to half width
                    temp = re.sub(self.chinese_regex, ' ', post[1])
                    terms = pynlpir.segment(temp, pos_english=False, pos_tagging=False)
                    terms_new = []
                    vocabulary_new = {}
                    for t in terms:
                        t = t.strip()
                        if t not in self.stopwords:
                            if t not in vocabulary.keys():
                                vocabulary_new[t] = vocabulary.__len__()
                                vocabulary[t] = vocabulary_new[t]
                                # sql = 'INSERT INTO vocabulary VALUES(%s,"%s")' % (vocabulary[t], t)
                                # self.cursor.execute(sql)
                            terms_new.append(vocabulary[t])
                            if vocabulary[t] not in c_terms.keys():
                                c_terms[vocabulary[t]] = 0
                            c_terms[vocabulary[t]] += 1
                    sql = 'INSERT INTO %s(pid,cid,terms) VALUES(%s,%s,"%s")' % (
                        self.post_terms_table, post[0], c[0], terms_new)
                    self.cursor.execute(sql)
                    if vocabulary_new.__len__() > 0:
                        param = []
                        for t in vocabulary_new:
                            param.append([vocabulary_new[t], t])
                        sql = 'insert into vocabulary values(%s,%s)'
                        # print param
                        self.cursor.executemany(sql, param)
                sql = 'INSERT INTO %s(cid,terms) VALUES(%s,"%s")' % (
                    self.company_terms_table, c[0], c_terms)
                self.cursor.execute(sql)
                self.conn.commit()
                print 'current size of the vocabulary:', vocabulary.__len__()
        except Exception as e:
            traceback.print_exc()
            self.conn.rollback()

    def getTFIDF(self):
        i = 0
        vocabulary = {}
        companies = []
        term_frequency = {}
        document_frequency = {}
        try:
            r = self.cursor.execute("SELECT * FROM vocabulary")
            for term in self.cursor.fetchall():
                vocabulary[term[1]] = term[0]  # term -> id
            print 'current size of the vocabulary:', r

            company_num = self.cursor.execute("SELECT * FROM %s order by cid" % self.company_terms_table)
            print 'company num:', company_num
            for c in self.cursor.fetchall():
                companies.append(c)
                c_term_frequency = eval(c[1])
                sum = math.fsum(c_term_frequency.values())
                for tid in c_term_frequency:
                    c_term_frequency[tid] = c_term_frequency[tid] / sum  # normalize
                    if tid not in document_frequency.keys():
                        document_frequency[tid] = 0
                    document_frequency[tid] += 1
                term_frequency[c[0]] = c_term_frequency

            # get tf-idf vectors for each company
            tf_idf = []
            for c in companies:
                tf_idf_c = []
                for tid in vocabulary.values():
                    temp = 0
                    if tid in term_frequency[c[0]]:
                        temp = term_frequency[c[0]][tid] * math.log10(company_num*1.0 / (document_frequency[tid]))
                    else:
                        temp = 0
                    tf_idf_c.append(temp)
                    if temp < 0 or document_frequency[tid] > company_num:
                        print tid, temp, document_frequency[tid]
                        exit()
                tf_idf.append(tf_idf_c)
            cPickle.dump(tf_idf, open('../data/tf_idf.data', 'w'))
        except Exception as e:
            traceback.print_exc()
            self.conn.rollback()

    def extract_training_set(self, num):
        print num

    def load_recruitment_post_data(self, from_file=False):
        """load the recruitment posts and vocabulary from the database or file for the top1000 active companies.
        Returns:
            posts: list-like, every element is a dict {pid:[tid]}
        """
        posts = []
        vocabulary = {}
        if from_file:
            posts = cPickle.load(file('../data/posts.data', 'r'))
            company_num = len(posts)
            post_num = -1
            vocabulary = cPickle.load(file('../data/vocabulary.data', 'r'))
        else:
            company_num = self.cursor.execute("SELECT * FROM %s order by cid" % self.company_table)
            print 'Number of companies: ', company_num
            i = 0
            post_num = 0
            for c in self.cursor.fetchall():
                posts.append({})
                r = self.cursor.execute('SELECT * FROM %s where cid=%s' % (self.post_terms_table, c[0]))
                post_num += r
                for post in self.cursor.fetchall():
                    post_terms = eval(post[2])
                    posts[i][post[0]] = npy.asarray(post_terms)
                i += 1

            r = self.cursor.execute('SELECT * FROM vocabulary order by tid')
            for v in self.cursor.fetchall():
                vocabulary[v[0]] = v[1]
            cPickle.dump(posts, open('../data/posts.data', 'w'))
            cPickle.dump(vocabulary, open('../data/vocabulary.data', 'w'))

        print 'Number of companies: ', company_num
        print 'Number of posts: ', post_num
        print 'Size of the vocabulary: ', len(vocabulary)

        return posts, vocabulary

    def load_recruitment_competitors_data(self, n=5, from_file=False):
        if from_file:
            company_competitors = cPickle.load(file('../data/company_competitors.data', 'r'))
        else:
            tf_idf = npy.asarray(cPickle.load(file('../data/tf_idf.data', 'r')))
            company_num = self.cursor.execute("SELECT cid, cfields FROM %s order by cid" % self.company_table)
            # tf_idf = npy.asarray([[1,1,2],[1,2,1],[1,3,1],[2,3,2]], dtype=float)
            # company_num = len(tf_idf)
            print 'Number of companies: ', company_num, len(tf_idf)
            if n>=company_num:
                print 'n must be smaller than company_num.'
            d = scipy.spatial.distance.pdist(tf_idf, 'cosine')
            distances = scipy.spatial.distance.squareform(d)
            sorted_index = npy.argsort(distances, axis=1) # the i-th row is indices for the i-th company sorted by distances
            company_competitors = npy.zeros((company_num, len(tf_idf[0])))
            for i in range(company_num):
                nearest_companies_vectors = 0
                for j in range(1,n+1):
                    nearest_companies_vectors += tf_idf[sorted_index[i,j]]
                nearest_companies_vectors /= n
                company_competitors[i] = nearest_companies_vectors
            # cPickle.dump(company_competitors, open('../data/company_competitors.data', 'w'))
        return company_competitors

    def load_recruitment_industry_data(self, from_file=False):
        if from_file:
            company_industry_trends = cPickle.load(file('../data/company_industry_trends.data', 'r'))
        else:
            tf_idf = cPickle.load(file('../data/tf_idf.data', 'r'))
            company_num = self.cursor.execute("SELECT cid, cfields FROM %s order by cid" % self.company_table)
            print 'Number of companies: ', company_num, len(tf_idf)

            # get relationships between companies and industry labels
            company_industry_labels = []
            industry_cid={}
            cid = 0
            for c in self.cursor.fetchall():
                cfields = str.split(c[1].encode("utf8"), ',')
                company_industry_labels.append([])
                # print cfields
                for f in cfields:
                    field = f.strip()
                    company_industry_labels[cid].append(field)
                    if industry_cid.has_key(field):
                        industry_cid[field].append(cid)
                    else:
                        industry_cid[field] = [cid]
                cid += 1

            # use companies' tf_idf to determine vectors of an industry
            industry_vectors = {}
            for f,cids in industry_cid.items():
                industry_tf_idf = 0
                # print f, cids
                for cid in cids:
                    industry_tf_idf += npy.asarray(tf_idf[cid])
                industry_tf_idf /= len(cids)
                industry_vectors[f] = industry_tf_idf

            # use companies' industry labels to determine their industry trends
            company_industry_trends = npy.zeros((company_num,len(tf_idf[0])))
            for cid in range(0, company_num):
                c_labels = company_industry_labels[cid]
                industry_trends = 0
                for l in c_labels:
                    industry_trends += industry_vectors[l]
                industry_trends /= len(c_labels)
                company_industry_trends[cid] = industry_trends
            print company_industry_trends.shape
            # cPickle.dump(company_industry_trends, open('../data/company_industry_trends.data', 'w'))
        return company_industry_trends

    def extract_industry(self):
        try:
            r = self.cursor.execute("SELECT cid, cfields FROM company order by cid")
            print 'company num:', r
            i = 0
            for c in self.cursor.fetchall():
                i += 1
                if i%100 == 0:
                    print '--', i
                cid = c[0]
                cfields = str.split(c[1].encode("utf8"), ',')
                # print cid, cfields, c[1], unicode.encode(c[1])

                if cfields.__len__() > 0:
                    param = []
                    for field in cfields:
                        param.append([cid, field.strip()])
                    sql = 'insert into company_industry(cid,industry) values(%s,%s)'
                    # print param
                    self.cursor.executemany(sql, param)

        except Exception as e:
            traceback.print_exc()
            self.conn.rollback()

    def __del__(self):
        self.cursor.close()
        self.conn.commit()
        self.conn.close()

if __name__ == '__main__':
    data = Data()
    # data.loadPost2db('F:/changbiao/DATA/job.csv')
    # data.extract_training_set(1000)
    # data.filterPost()
    # data.tokenize()
    # data.getTFIDF()
    # data.extract_industry()
    id = data.load_recruitment_industry_data()
    cd = data.load_recruitment_competitors_data()
    print id.shape, cd.shape
    for i in range(len(id)):
        print npy.sum(id[i]), npy.sum(cd[i])
        print tools.log_delta_function(id[i]),tools.log_delta_function(cd[i])