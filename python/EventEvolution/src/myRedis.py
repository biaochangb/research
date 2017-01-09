__author__ = 'bchang'

import redis
import pickle

class Redis:
    redis = None
    redis_host = 'localhost'
    redis_port = 6379
    redis_key_prefix = "changbiao:event:evolution:twitter:sg:"

    redis_db = "../data/redis.db"

    def __init__(self):
        self.redis = redis.Redis(host= self.redis_host, port=self.redis_port, db=0)

    def getValidTopicID(self):
        """ valid topic IDs = filter - invalid """
        filter = self.redis.lrange(self.redis_key_prefix+"topics:filter", 0, -1)
        invalid = self.redis.lrange(self.redis_key_prefix+"topics:invalid", 0, -1)
        for t in filter:
            if t not in invalid:
                self.redis.rpush(self.redis_key_prefix + 'topics:valid', t)

    def saveData(self):
        write = open(self.redis_db, 'wb')
        events = self.redis.lrange("changbiao:event:evolution:twitter:sg:events", 0, -1)
        pickle.dump(events, write)
        all = self.redis.lrange("changbiao:event:evolution:twitter:sg:topics:all", 0, -1)
        pickle.dump(all, write)
        filter = self.redis.lrange("changbiao:event:evolution:twitter:sg:topics:filter", 0, -1)
        pickle.dump(filter, write)
        invalid = self.redis.lrange("changbiao:event:evolution:twitter:sg:topics:invalid", 0, -1)
        pickle.dump(invalid, write)
        valid = self.redis.lrange("changbiao:event:evolution:twitter:sg:topics:valid", 0, -1)
        pickle.dump(valid, write)
        write.close()

        read = open(self.redis_db, 'rb')
        d = pickle.load(read)
        print len(d)
        d = pickle.load(read)
        print len(d)
        d = pickle.load(read)
        print len(d)
        d = pickle.load(read)
        print len(d)
        d = pickle.load(read)
        print len(d),d[0]

    def load2Reids(self):
        read = open(self.redis_db, 'r')
        d = pickle.load(read)
        for e in d:
            self.redis.rpush('changbiao:event:evolution:twitter:sg:events', e)
        d = pickle.load(read)
        for e in d:
            self.redis.rpush('changbiao:event:evolution:twitter:sg:topics:all', e)
        d = pickle.load(read)
        for e in d:
            self.redis.rpush('changbiao:event:evolution:twitter:sg:topics:filter', e)
        d = pickle.load(read)
        for e in d:
            self.redis.rpush('changbiao:event:evolution:twitter:sg:topics:invalid', e)
        d = pickle.load(read)
        for e in d:
            self.redis.rpush('changbiao:event:evolution:twitter:sg:topics:valid', e)
        read.close()

if __name__ == '__main__':
    myRedis = Redis()
    #myRedis.getValidTopicID()
    #myRedis.saveData()
    #myRedis.load2Reids()
