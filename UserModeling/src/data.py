# coding=utf-8
"""
A part of User modeling.
Author: Biao Chang, changb110@gmail.com, from University of Science and Technology of China
created at 2017/8/7.
"""

import MySQLdb


class Data:
    conn = None  # database connection
    cursor = None  # database cursor
    user_num = 0
    users = []
    USER_SUBSET_TABLE = 'cb_user_subset'
    WEIBO_SUBSET_TABLE = 'cb_weibo_subset'
    RELATION_SUBSET_TABLE = 'cb_relation_subset1000'
    USER_ALL_TABLE = 'userprofile'
    WEIBO_ALL_TABLE = 'weibo'
    RELATION_ALL_TABLE = 'relation'

    def __init__(self):
        self.conn = MySQLdb.connect(
            host='172.16.46.10',
            port=3306,
            user='root',
            passwd='123456',
            db='weibo',
        )
        self.cursor = self.conn.cursor()
        n = self.cursor.execute('SELECT host FROM %s' % self.USER_SUBSET_TABLE)
        for u in self.cursor.fetchall():
            self.users.append(u[0])
        print n, self.users

    def extract_training_set(self, user_num):
        self.user_num = user_num
        result = self.cursor.execute("SELECT * FROM uidmap")
        uidmap = {}
        for r in self.cursor.fetchall():
            uidmap[r[1]] = r[0]
        print uidmap.__len__(), uidmap[self.users[0]], self.users[0]

        for u in self.users:
            if u not in uidmap.keys():
                uidmap[u] = u
            r = self.cursor.execute(
                "INSERT INTO %s SELECT * FROM %s WHERE userId='%s' OR userId = '/u/%s' OR userId='/%s' " % (
                self.WEIBO_SUBSET_TABLE, self.WEIBO_ALL_TABLE, u,u, uidmap[u]))
            print r

def __del__(self):
    self.cursor.close()
    self.conn.commit()
    self.conn.close()


if __name__ == '__main__':
    data = Data()
    data.extract_training_set(1000)
