#coding:utf-8

__author__ = 'bchang'

import os;
import MySQLdb
import math
import random
import time
import decimal
import pickle
from numpy import *
from NAR import *
from ARMA import *

class Visiting:
    host = 'localhost'
    user = 'root'
    password = ''
    db = 'youku2014'
    video_id_table = 'video_profile'
    view_table = 'epiosde_view_mainland_chain'
    matrix_path = '../result/p%dq%d.txt'
    views_file = '../result/views.pickle'

    def __init__(self):
        self.con = MySQLdb.connect(host=self.host, user=self.user, passwd=self.password, db=self.db)
        self.cursor = self.con.cursor()
        self.views, self.serials_episodes_records = self.loadRawData()

    def __del__(self):
        self.con.commit()
        self.cursor.close()
        self.con.close()

    def saveAllRawData(self):
        print 'save Raw Data'
        self.cursor.execute('SELECT a.vid,episode_num FROM (SELECT vid,MAX(nth) AS episode_num FROM youku2014.epiosde_view_mainland_chain GROUP BY vid) AS a WHERE a.episode_num>10')
        vids = self.cursor.fetchall()   # ids of all serials

        MAX_EPISODE_NUM = 100
        RECORDS_LIMIT = 50
        views = array([zeros([MAX_EPISODE_NUM,RECORDS_LIMIT]) for i in range(len(vids))])
        serials_episodes_records = {}
        shape(views)
        k = 0
        for vid in vids:
            serial_views = zeros([MAX_EPISODE_NUM,RECORDS_LIMIT])
            episode_num = {}
            for nth in range(1,vid[1]+1):
                sql = 'SELECT vv FROM youku2014.epiosde_view_mainland_chain WHERE vid=%d and nth=%d ORDER BY DATE limit %d'%(vid[0], nth, RECORDS_LIMIT)
                self.cursor.execute(sql)
                episode_views = self.cursor.fetchall()
                episode_num[nth] = len(episode_views)
                if episode_num[nth]==0:
                    continue
                array2 = array(episode_views)
                serial_views[nth-1][0:episode_num[nth]] = array2[:,0]
                #serial_views.append(list(array2[:,0]))
            views[k] = serial_views
            serials_episodes_records[k] = episode_num;
            k += 1
            #print views,k,serials_episodes_records,sql
            #break
        write = open(self.views_file, 'wb')
        pickle.dump(views, write)
        pickle.dump(serials_episodes_records,write)
        write.close()

    def loadRawData(self):
        print 'load Raw Data'
        read = open(self.views_file, 'rb')
        views = pickle.load(read)
        serials_episodes_records = pickle.load(read)
        read.close()
        return views,serials_episodes_records

    def experiment(self):
        """cross validation"""
        n_fold = 5
        nar = NAR()
        arma = ARMA()
        # nar.crossValidation(self.views,n_day,self.serials_episodes_records,n_fold)
        # arma.crossValidation(self.views,n_day,self.serials_episodes_records,n_fold)
        for n_day in range(0,7):
            error = []
            type = 0
            # for lbd in  range(0,50,2):
            #     arma.lbd = exp(lbd/10.0)
            #     p,q,w,rmse = arma.crossValidation(self.views,n_day,self.serials_episodes_records,n_fold, type)
            #     print 'lambda =',exp(lbd/10.0),rmse,q
            p,w,rmse = nar.crossValidation(self.views,n_day,self.serials_episodes_records,n_fold, type)
            error.append(rmse)
            print w
            # p,q,w,rmse = arma.crossValidation(self.views,n_day,self.serials_episodes_records,n_fold, type)
            # error.append(rmse)
            # if type==1:
            #     continue

            # type = 0
            # print '\t type=',type
            # p,w,rmse = nar.crossValidation(self.views,n_day,self.serials_episodes_records,n_fold, type)
            # error.append(rmse)
            # p,q,w,rmse = arma.crossValidation(self.views,n_day,self.serials_episodes_records,n_fold, type)
            # error.append(rmse)
            # print 'n-day =',n_day,error


if __name__ == '__main__':
    print 'start'
    start_time = time.time()
    visiting = Visiting()
    #visiting.saveAllRawData()
    visiting.experiment()
    end_time = time.time()
    print 'running time: %f \r\n'%((end_time-start_time)/3600)