__author__ = 'bchang'

import redis
import requests
import Event
import Topic
import pickle
import re

class Data:
    redis = None
    redis_host = '10.0.109.33'
    redis_port = 8181
    redis_key_prefix = "changbiao:event:evolution:twitter:sg:"
    es_proxy = 'http://research.pinnacle.smu.edu.sg/clear/v2/home/event/proxy?' \
               'es=http://kappa1.larc.smu.edu.sg:9200/plr_sg_tweet_2015/_search&param='
    # plr_sg_tweet_2015: index of tweets in 2015

    events = []
    topics = []
    min_keywords_num = 6
    min_sharing_keywords_num = 3
    min_events_num_in_topic = 5
    max_events_num_in_topic = 20

    data_file = "../data/events.data"

    def __init__(self):
        self.redis = redis.Redis(host= self.redis_host, port=self.redis_port, db=0)

    def preprocessing(self):
        self.getEvents()
        print "Topics:", self.clusterEvents()
        self.saveData()

    def saveData(self):
        write = open(self.data_file, 'wb')
        pickle.dump(self.events, write)
        pickle.dump(self.topics, write)
        write.close()

        for e in self.events:
            self.redis.rpush(self.redis_key_prefix + 'events', e.__dict__)
        counts = {}
        for t in self.topics:
            self.redis.rpush(self.redis_key_prefix + 'topics:all', t.__dict__)
            n = len(t.events)
            if  self.min_events_num_in_topic <= n <= self.max_events_num_in_topic:
                self.redis.rpush(self.redis_key_prefix + 'topics:filter', t.id)
                if n in counts:
                    counts[n] += 1
                else:
                    counts[n] = 1
        print counts

    def loadData(self):
        print 'load Raw Data'
        read = open(self.data_file, 'rb')
        self.events = pickle.load(read)
        self.topics = pickle.load(read)
        read.close()
        return len(self.events), len(self.topics)

    def getEvents(self):
        """get events from Redis"""
        events_str = self.redis.lrange("twitter:sg:event:python:detections2", 0, -1)

        counts = {}
        for event_str in events_str:
            event = eval(event_str)
            n = len(event['keywords'])
            if (n < self.min_keywords_num) or (event['t'] > "2016-00-00 00:00:00") \
                or (not self.isValid(event['keywords'])):
                continue
            if n in counts:
                counts[n] += 1
            else:
                counts[n] = 1
            e = Event.Event()
            e.keywords = event['keywords']
            e.when = event['t']
            e.id = len(self.events)
            self.events.append(e)
        print counts, len(self.events)
        return len(self.events)

    def clusterEvents(self):
        for event in self.events:
            self.addEventToTopic(event)
        return len(self.topics)

    def addEventToTopic(self, event):
        """
            add a event to the topic which has the most similar keywords.
        """
        # find the topic that the event belongs to
        similarity_max = 0
        index_max = -1
        for i in range(len(self.topics)):
            a = set(event.keywords)
            b = self.topics[i].keywords
            k = len(a&b)    # the number of sharing keywords
            if similarity_max < k:
                similarity_max = k
                index_max = i
        if similarity_max <= self.min_sharing_keywords_num:
            # new topic
            topic = Topic.Topic()
            topic.id = len(self.topics)
            topic.keywords = set(event.keywords)
            topic.events = [event.id]
            self.topics.append(topic)
            event.topic_id = topic.id
        else:
            self.topics[index_max].events.append(event.id)
            self.topics[index_max].keywords = self.topics[index_max].keywords | set(event.keywords)
            event.topic_id = self.topics[index_max].id

    def extractTweets(self):
        """
        extract event-related tweets from ElasticSearch via API(http://kappa1.larc.smu.edu.sg:9200/plr_sg_tweet_2015/_search).
        A tweet is event-related if the text includes at least one keyword.
        """
        num_event = 0
        for event in self.events:
            n = len(event.keywords)
            num_event += 1
            query = ""
            # {"term":{"tweet.text":"aaafiiqqq"}},{"term":{"tweet.text":"foreigner"}}
            for keyword in event.keywords:
                query += '{"term":{"tweet.text":"' + keyword + '"}},'
            query = query[:-1]  # remove the last comma
            query = '{"query":{"bool":{"must":[],"must_not":[],"should":[' \
                    + query + ']}},"from":0,"size":10,"sort":[],"facets":{}}'
            # A tweet is event-related if the text includes at least one keyword.
            url = self.es_proxy + query
            r = requests.get(url)
            text = r.text.replace("false", "False")
            text = text.replace("true", "True")
            text = text.replace("null", "None")
            result = eval(text)
            print result['took'], len(result['hits']['hits'])

        print "Events:", num_event
        return 1

    def isValid(self, keywords):
        """
        Keywords are not recognisable if they contain non-ASCII or non-chinese characters.
        """
        flag = True
        for w in keywords:
            if (not self.is_ascii(w)) and (not self.is_chinese(w)):
                flag = False
                break
        return flag

    def is_ascii(self, s):
        return all(ord(c) < 128 for c in s)

    def is_chinese(self, s):
        r = re.findall(ur'[\u4e00-\u9fff]+', s)
        return len(r) > 0