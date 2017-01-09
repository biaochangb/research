#coding:utf-8
import os;
import MySQLdb
import math
import random
import time
import decimal
import pickle

class DataPreprocess:
    host = 'localhost'
    user = 'root'
    password = ''
    db = 'youku2014'
    video_id_table = 'video_profile'
    view_table = 'epiosde_view_mainland_chain'
    max_loop = 100
    dtw_file = '../result/dtw-date.pickle'
    first_n_days = 1

    def __init__(self):
        self.con = MySQLdb.connect(host=self.host, user=self.user, passwd=self.password, db=self.db)
        self.cursor = self.con.cursor()

    def __del__(self):
        self.con.commit()
        self.cursor.close()
        self.con.close()


    def setEpisodeOrderId(self):
        """设置每集播放记录的序号"""
        self.cursor.execute('SELECT vid,nth FROM youku2014.`epiosde_view_mainland_chain` GROUP BY vid,nth ORDER BY vid,nth')
        episodes = self.cursor.fetchall()
        m = len(episodes)
        j=0
        for episode in episodes:
            self.cursor.execute('select * FROM youku2014.`epiosde_view_mainland_chain` where vid=%d and nth=%d order by date'%(episode[0], episode[1]))
            records = self.cursor.fetchall()
            i = 0
            for record in records:
                self.cursor.execute('update youku2014.`epiosde_view_mainland_chain` set order_id=%d where id=%d'%(i,record[0]))
                i += 1
            j += 1
            if (j*100%m == 0):
                print('%%%d'%(j*100/m))


    def distance(self,x,y):
        return (x-y)**2


    def DTW(self,s,t):
        """计算两个时间序列的DTW距离"""
        n = len(s)
        m = len(t)
        dtw = [([float("inf")] * (m+1)) for i in range(n+1)]
        dtw[0][0] = 0
        for i in range(1, n+1):
            for j in range(1, m+1):
                cost = self.distance(s[i-1],t[j-1])
                dtw[i][j] = cost + min(dtw[i-1][j], dtw[i-1][j-1], dtw[i][j-1])

        return math.sqrt(dtw[n][m])

    def normalizeByMax_Min(self,x):
        """normalize x with the max-min method"""
        y = [x[0]]  # reserve vid
        max = x[1]
        min = x[1]
        for t in x[1:]:
            if t > max:
                max = t
            if t < min:
                min = t
        for t in x[1:]:
            y.append((t-min)*decimal.Decimal(1.0)/(max-min))
        return y


    def getFirstNDayViewByEpisode(self):
        """获取所有电视剧每集前nDay天的平均博放量序列"""
        all = []
        self.cursor.execute('SELECT DISTINCT vid FROM %s.%s'%(self.db,self.view_table))
        vids = self.cursor.fetchall()
        for vid in vids:
            self.cursor.execute(' SELECT update_rate FROM youku2014.video_profile WHERE id=%d'%vid)
            profile = self.cursor.fetchall()
            update_rate = profile[0][0]
            self.cursor.execute('SELECT vid,nth,date, AVG(vv) as vv FROM %s.%s WHERE vid=%d AND order_id<%d GROUP BY nth ORDER BY nth ,DATE' % (self.db, self.view_table, vid[0], self.first_n_days))
            records = self.cursor.fetchall()

            episodes = [vid[0]] #第一个元素是vid
            i = 0
            date = records[0][2]
            views = 0
            for episode in records:
                if episode[2] != date:
                    episodes.append(views/i)
                    i = 1
                    date = episode[2]
                    views = episode[3]
                else:
                    views += episode[3]
                    i += 1
            episodes.append(views/i)
            all.append(self.normalizeByMax_Min(episodes))
            # break
        # print all
        return all


    def saveDTWtoFile(self, firstNdays=3):
        print 'stat saving DTW to a file'
        self.first_n_days = firstNdays
        series = self.getFirstNDayViewByEpisode()
        num = len(series) # the number of teleplays
        dtw = [([-1] * (num)) for i in range(num)]
        for i in range(num):
            for j in range(num):
                if dtw[i][j] < 0:
                    dtw[i][j] = dtw[j][i] = self.DTW(series[i][1:], series[j][1:])

        write = open(self.dtw_file.__add__('.%d'%self.first_n_days), 'wb')
        pickle.dump(dtw, write)
        write.close()

    def readDTWfromFile(self):
        print 'stat reading DTW from a file'
        read = open(self.dtw_file.__add__('.%d'%self.first_n_days), 'rb')
        dtw = pickle.load(read)
        read.close()
        return dtw

    def k_mediods(self, path, k=3):
        """k-mediods clustering with dynamic time warping(DTW), where each cluster is represented by the most centrally located object in a cluster.
        L. Kaufman, P.J. Rousseeuw, Finding Groups in Data: An Introduction to Cluster Analysis, Wiley, New York, 1990.
        V. Estivill-Castro, A.T. Murray, Spatial clustering for data mining with genetic algorithms, http://citeseer.nj.nec.com/estivill-castro97spatial.html.
        On Clustering Multimedia Time Series Data Using K-Means and Dynamic Time Warping
        """
        series = self.getFirstNDayViewByEpisode()
        num = len(series) # the number of teleplays
        print 'size = ',num
        labels = [-1 for i in range(num)]  # 各电视剧初始化标签
        centers = [0 for i in range(k)]  # initial cluster centers
        clusters = [set() for i in range(k)]

        #initiate
        for i in range(k):
            j = random.randint(0, num-1)
            centers[i] = j
            clusters[i].add(j)   # series[j]对应的vid加入cluster i中
            labels[j] = i
        dtw = self.readDTWfromFile()

        #clustering
        print 'start clustering'
        for step in range(self.max_loop):
            print 'steps = ', step
            flag = 0 # the number of items which have changed its cluster during one step
            for i in range(num):
                min_d = float("inf")
                min_cindex = -1
                for j in range(k):
                    d = dtw[i][j]
                    if d < min_d:
                        min_cindex = j
                        min_d = d
                if min_cindex != labels[i]:
                    if labels[i] > -1:
                        clusters[labels[i]].discard(i)
                    clusters[min_cindex].add(i)
                    labels[i] = min_cindex
                    flag += 1

                    #update the min_index-cluster center
                    min_d = float("inf")
                    index = -1
                    for j in clusters[min_cindex]:
                        temp_d = 0
                        for p in clusters[min_cindex]:
                            temp_d  += dtw[i][j]
                        if temp_d < min_d:
                            index = j
                            min_d = temp_d
                        centers[min_cindex] = index
            print '\tflag = ',flag
            if flag == 0:
                break


        #output results
        write = file(path+'-firstN%d-k%d.txt'%(self.first_n_days,k), 'w')
        write.write( 'size of each cluster: ')
        for i in range(k):
            write.write('%d\t'%len(clusters[i]))
        write.writelines('\ncluster centers\n')
        for i in range(k):
            write.write('%s\n'%series[centers[i]])
        write.writelines('\n**********************************************\n')
        for i in range(k):
            nodes = []
            for j in clusters[i]:
                nodes.append(j)
            print 'size of cluster %d: %d'%(i,nodes.__len__())
            for s in range(nodes.__len__()):
                for t in range(s+1,nodes.__len__()):
                    if dtw[centers[i]][nodes[t]] < dtw[centers[i]][nodes[s]]:
                        #swap nodes[s] and nodes[t]
                        temp = nodes[s]
                        nodes[s] = nodes[t]
                        nodes[t] = temp
                write.write('%d,%s\n'%(i,series[nodes[s]]))
        write.close()


if __name__ == '__main__':
    start_time = time.time()
    preprocess = DataPreprocess()
    for k in range(2,7):
        preprocess.k_mediods('../result/normalized-teleplay-series-clustering',k)
    end_time = time.time()
    print 'running time: %f \r\n'%((end_time-start_time)/3600)
    # print len(prepreocess.getFirstNDayViewByEpisode())
    #prepreocess.setEpisodeOrderId()