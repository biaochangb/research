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
import unicodedata
import datetime

reload(sys)
sys.setdefaultencoding('utf-8')


class Data:
    conn = MySQLdb.connect(host='172.16.46.211', port=3306, user='root', passwd='123456',
                           db='lagou', charset='utf8')  # database connection
    cursor = conn.cursor()  # database cursor
    stopwords = set()
    company_table = 'company_top1000'
    company_terms_table = 'company_terms_top1000'
    post_table = 'post_top1000'
    post_terms_table = 'post_terms_top1000'
    vocabulary_table = 'vocabulary'
    punctuation = "[+-\.\!\/_,$%^*(+\"\'=;；,，+——！。？、~@#￥%……&*（）｛－｜｝｝＞ø～～±～＋￥×§¬ø[▽◆◇○◎●★☆♡►▎▌█╰╯╮╭⊙≧≦≥≤∩∞√−↓←※•​【ლ╹◡╹ლ)̈абвгдежзийклмфцчшщыюя]+".decode(
        "utf8")
    url_regex = re.compile(
        r'(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(/\S+)?', re.IGNORECASE)
    chinese_regex = re.compile(ur'[^\u4e00-\u9fff]', re.IGNORECASE)

    data_split_date = '2015-05-01'
    tf_idf = None

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
            r = self.cursor.execute("SELECT * FROM company order by cid")
            print 'company num:', r
            i = 0
            for c in self.cursor.fetchall():
                i += 1
                print c[0]
                if i % 100 == 0:
                    print '---', i
                r = self.cursor.execute('SELECT pid,description FROM %s where cname="%s"' % (self.post_table, c[1]))
                for post in self.cursor.fetchall():
                    description = post[1]
                    description = unicodedata.normalize('NFKC', description.lower().decode("utf8")) # full width char to half width
                    description, n = self.url_regex.subn('', description)
                    description = description.decode("utf8")
                    description = re.sub(self.punctuation, " ".decode("utf8"), description)
                    r = self.cursor.execute('UPDATE %s set description="%s" where pid=%s' % (self.post_table, description, post[0]))
                    # print post[0], post[1]
                    # print '--',description
                self.conn.commit()
            exit()
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
                    # temp = unicodedata.normalize('NFKC', post[1].lower().decode("utf8")) # full width char to half width
                    temp = post[1]
                    terms = pynlpir.segment(temp, pos_english=False, pos_tagging=False)
                    terms_new = []
                    vocabulary_new = {}
                    for t in terms:
                        t = t.strip()
                        if len(t)<=1:
                            continue
                        if (t not in self.stopwords) and (tools.is_chinese(t) or tools.is_english(t)):
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
                    # print sql
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
                print 'current size of the vocabulary:', vocabulary.__len__()
                # exit()
                self.conn.commit()
        except Exception as e:
            traceback.print_exc()
            self.conn.rollback()

    def updateCompanyTermFrequency(self):
        """update the company term-frequency vectors according to the training data"""
        r = self.cursor.execute("SELECT * FROM %s where cid<=1000 order by cid DESC" % self.company_table)
        print 'company num:', r
        for c in self.cursor.fetchall():
            c_terms = {}
            r = self.cursor.execute('SELECT * FROM %s where cid="%s" and publish_date <"%s"' % (self.post_terms_table, c[0], self.data_split_date))
            print '--post num:', r, c[0]
            for post in self.cursor.fetchall():
                p_terms = eval(post[2])
                for t in p_terms:
                    if t in c_terms:
                        c_terms[t] += 1
                    else:
                        c_terms[t] = 1
            sql = 'update %s set terms="%s" where cid=%s' % (self.company_terms_table, c_terms, c[0])
            # print sql
            # exit()
            self.cursor.execute(sql)

    def updateTermFrequency(self):
        """count the term frequencies and filter out <=2, move to a new vocabulary table."""
        print 'get the frequency for each term'
        company_num = self.cursor.execute("SELECT * FROM %s order by cid desc" % self.company_terms_table)
        term_frequency ={}
        for c in self.cursor.fetchall():
            c_terms = eval(c[1])
            for term, frequency in c_terms.items():
                if term in term_frequency:
                    term_frequency[term] += frequency
                else:
                    term_frequency[term] = frequency

        sql = 'UPDATE `vocabulary` SET `frequency` = %s WHERE `tid` = %s'
        param = []
        for t,f in term_frequency.items():
            param.append((f,t))
        self.cursor.executemany(sql, param)

        self.cursor.execute("INSERT INTO vocabulary_filter(tid_old,term) SELECT tid,term FROM vocabulary WHERE frequency>2 ORDER BY tid")

    def filterTerms(self):

        vocabulary_filter = {}
        self.cursor.execute("SELECT * FROM vocabulary_filter")
        for row in self.cursor.fetchall():
            vocabulary_filter[row[1]] = row[0]

        print "filter posts"
        self.cursor.execute("SELECT * FROM %s" %self.post_terms_table)
        for row in self.cursor.fetchall():
            pid = row[0]
            old_terms = eval(row[2])
            new_terms = []
            for t in old_terms:
                if t in vocabulary_filter:
                    new_terms.append(vocabulary_filter[t])
            self.cursor.execute('update %s set terms="%s" where pid=%s'%(self.post_terms_table,new_terms,pid))

        print 'filter companies'
        self.cursor.execute("SELECT * FROM %s" %self.company_terms_table)
        for row in self.cursor.fetchall():
            cid = row[0]
            old_terms = eval(row[1])
            new_terms = {}
            for term,frequency in old_terms.items():
                if term in vocabulary_filter:
                    new_terms[vocabulary_filter[term]] = frequency
            self.cursor.execute('update %s set terms="%s" where cid=%s' % (self.company_terms_table, new_terms, cid))


    def getTFIDF(self, save_to_file=False):
        try:
            vocabulary = {}
            companies = []
            term_frequency = {}
            r = self.cursor.execute("SELECT * FROM vocabulary_filter")
            for term in self.cursor.fetchall():
                vocabulary[term[2]] = term[0]  # term -> id
            print 'current size of the vocabulary:', r

            document_frequency = npy.zeros(len(vocabulary))
            company_num = self.cursor.execute("SELECT * FROM %s order by cid desc" % self.company_terms_table)
            print 'company num:', company_num
            for c in self.cursor.fetchall():
                companies.append(c)
                c_term_frequency = eval(c[1])
                total = sum(c_term_frequency.values())
                ctf = npy.zeros(len(vocabulary))
                for tid in c_term_frequency:
                    ctf[tid-1] = c_term_frequency[tid]*1.0 / total     # normalize
                    document_frequency[tid-1] += 1
                term_frequency[c[0]] = ctf

            # get tf-idf vectors for each company
            tf_idf = npy.zeros((company_num,len(vocabulary)))
            for i,c in enumerate(companies):
                tf_idf[i] = term_frequency[c[0]]*npy.log((company_num+1.0)/(document_frequency+1)) # smooth
            if save_to_file:
                cPickle.dump(tf_idf.tolist(), open('../data/tf_idf.data', 'w'))
        except Exception as e:
            traceback.print_exc()
            self.conn.rollback()
        self.tf_idf = tf_idf
        return tf_idf

    def extract_training_set(self, num):
        print num

    def split_data_for_lda(self, from_file=False):
        if from_file:
            training_posts,test_posts = cPickle.load(file('../data/posts-lda.data', 'r'))
        else:
            vocabulary ={}
            r = self.cursor.execute("SELECT * FROM vocabulary_filter")
            for term in self.cursor.fetchall():
                vocabulary[term[2]] = term[0]  # term -> id
            print 'current size of the vocabulary:', r
            company_num = self.cursor.execute("SELECT * FROM %s order by cid desc" % self.company_table)
            training_posts = npy.ones((company_num,len(vocabulary)),dtype=npy.int32)
            test_posts = npy.zeros((company_num,len(vocabulary)),dtype=npy.int32)
            post_num = 0
            cid = 0
            for c in self.cursor.fetchall():
                r = self.cursor.execute('SELECT * FROM %s where cid=%s' % (self.post_terms_table, c[0]))
                post_num += r
                for post in self.cursor.fetchall():
                    terms = npy.asarray(eval(post[2]))-1    # '-1' is converting the database index to the vector index
                    if str(post[3]) < self.data_split_date:
                        for t in terms:
                            training_posts[cid,t] += 1
                    else:
                        for t in terms:
                            test_posts[cid,t] += 1
                cid += 1
            cPickle.dump((training_posts, test_posts), open('../data/posts-lda.data', 'w'))
            print 'Number of posts: ', post_num
        return training_posts, test_posts

    def load_recruitment_post_data(self, company_num, from_file=False):
        """load the recruitment posts and vocabulary from the database or file for the top1000 active companies.
        Returns:
            posts: list-like, every element is a dict {pid:[tid]}
        """
        training_posts = []
        test_posts = []
        vocabulary = {}
        companies = []
        if from_file:
            training_posts,test_posts,companies = cPickle.load(file('../data/posts.data', 'r'))
            company_num = len(training_posts)
            post_num = -1
            vocabulary = cPickle.load(file('../data/vocabulary.data', 'r'))
        else:
            self.cursor.execute("SELECT * FROM %s order by cid desc limit %s" %(self.company_table, company_num))
            post_num = 0
            for c in self.cursor.fetchall():
                training_post_terms = {}
                test_post_terms = {}
                r = self.cursor.execute('SELECT * FROM %s where cid=%s' % (self.post_terms_table, c[0]))
                post_num += r
                for post in self.cursor.fetchall():
                    terms = npy.asarray(eval(post[2]))-1    # '-1' is converting the database index to the vector index
                    if str(post[3]) < self.data_split_date:
                        training_post_terms[post[0]] = terms
                    else:
                        test_post_terms[post[0]] = terms
                training_posts.append(training_post_terms)
                test_posts.append(test_post_terms)
                companies.append(c)

            r = self.cursor.execute('SELECT * FROM vocabulary_filter order by tid_new')
            for v in self.cursor.fetchall():
                vocabulary[v[0]] = v[2]
            cPickle.dump((training_posts,test_posts,companies), open('../data/posts.data', 'w'))
            cPickle.dump(vocabulary, open('../data/vocabulary.data', 'w'))

        print 'Number of companies: ', company_num
        print 'Number of posts: ', post_num
        print 'Size of the vocabulary: ', len(vocabulary)

        return training_posts, test_posts, vocabulary, companies

    def load_recruitment_competitors_data(self, companies, n=5, from_file=False):
        if from_file:
            company_competitors = cPickle.load(file('../data/company_competitors.data', 'r'))
            company_competitors = npy.asarray(company_competitors)
        else:
            # tf_idf = npy.asarray(cPickle.load(file('../data/tf_idf.data', 'r')))
            tf_idf = self.tf_idf
            company_num = len(companies)
            # tf_idf = npy.asarray([[1,1,2],[1,2,1],[1,3,1],[2,3,2]], dtype=float)
            # company_num = len(tf_idf)
            print 'Number of companies: ', company_num, len(tf_idf)
            if n>=company_num:
                print 'n must be smaller than company_num.'
            d = scipy.spatial.distance.pdist(tf_idf[:company_num], 'cosine')
            distances = scipy.spatial.distance.squareform(d)
            sorted_index = npy.argsort(distances, axis=1) # the i-th row is indices for the i-th company sorted by distances
            company_competitors = npy.zeros((company_num, len(tf_idf[0])))
            for i in range(company_num):
                nearest_companies_vectors = 0
                for j in range(1,n+1):
                    nearest_companies_vectors += tf_idf[sorted_index[i,j]]
                nearest_companies_vectors /= n
                company_competitors[i] = nearest_companies_vectors
            # cPickle.dump(company_competitors.tolist(), open('../data/company_competitors.data', 'w'))
        return company_competitors

    def load_recruitment_industry_data(self, companies, from_file=False):
        if from_file:
            company_industry_trends = cPickle.load(file('../data/company_industry_trends.data', 'r'))
            company_industry_trends = npy.asarray(company_industry_trends)
        else:
            # tf_idf = npy.asarray(cPickle.load(file('../data/tf_idf.data', 'r')))
            tf_idf = self.tf_idf
            company_num = len(companies)
            print 'Number of companies: ', company_num, len(tf_idf)

            # get relationships between companies and industry labels
            company_industry_labels = {}
            industry_cid={}
            i = 0
            for c in companies:
                cfields = str.split(c[3].encode("utf8"), ',')
                cid = i
                company_industry_labels[cid] = []
                # print cfields
                for f in cfields:
                    field = f.strip()
                    company_industry_labels[cid].append(field)
                    if field in industry_cid:
                        industry_cid[field].append(cid)
                    else:
                        industry_cid[field] = [cid]
                i += 1

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
            for i in range(company_num):
                cid = i
                c_labels = company_industry_labels[cid]
                industry_trends = 0
                for l in c_labels:
                    industry_trends += industry_vectors[l]
                industry_trends /= len(c_labels)
                company_industry_trends[i] = industry_trends
            print company_industry_trends.shape
            # cPickle.dump(company_industry_trends.tolist(), open('../data/company_industry_trends.data', 'w'))
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
    # data.filterPost()
    # data.tokenize()
    # data.updateTermFrequency()
    # data.filterTerms()

    # data.extract_training_set(1000)

    # data.updateCompanyTermFrequency()
    # data.getTFIDF(save_to_file=True)
    # data.extract_industry()
    # p,t,v,c = data.load_recruitment_post_data(100,from_file=False)
    # id = data.load_recruitment_industry_data()
    # cd = data.load_recruitment_competitors_data()
    # print id.shape, cd.shape
    # for i in range(len(id)):
    #     print npy.sum(id[i]), npy.sum(cd[i])
    #     print tools.log_delta_function(id[i]),tools.log_delta_function(cd[i])
