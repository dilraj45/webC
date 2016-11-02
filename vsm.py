"""Implementing vector space model"""
from pymongo import MongoClient
import math
import operator
import re


class Vector_Space_Model:

    def __init__(self):
        client = MongoClient()
        db = client['test_project']
        self.col = db.summary
        self.col1 = db.on_page_summary
        # fetching hashmap in main memory
        doc = self.col.find_one({"_id": "_hashmap"})
        self.hashmap = doc['mapping']
        self.reverse_hashmap = {v: k for k, v in self.hashmap.items()}
        self.total_docs = doc['Total_urls']
        # Initializing a dictionary for holding the ranks of each page
        # Ranks are initialized to zero
        self.rank_sum = {}
        self.rank_pg = {}
        self.final_rank = {}
        for key in self.hashmap:
            self.rank_sum[self.hashmap[key]] = 0
            self.rank_pg[self.hashmap[key]] = 0
        # Fetching the keyword list
        self.fp = open('stem_tw.txt', 'r').read().split('\n')
        self.result = open('r.txt', 'w+')

    def rank_summary(self, tw, df, postings):
        # fetching the posting list
        # tf for keyword is on ein query
        s = tw
        if df is 0:
            return
        m = math.log(float(self.total_docs + 1) / df, 10)
        s = s * m
        for x in postings:
            t = s * 51 * x[1]
            t = s / (50 + x[1])
            self.rank_sum[x[0]] = self.rank_sum[x[0]] + t

    def upload_ranks_db(self):
        self.col.insert({"_id": "ranks",
                         "ranks": self.rank_sum})

    def fetch_and_rank_summary(self):
        for pair in self.fp:
            keyword = pair.split(',')[0]
            tw = float(pair.split(',')[1])
            doc = self.col.find_one({'_id': keyword})
            df = doc['df']
            self.rank_summary(tw, df, doc["postings"])
        # normalizing ranks
        mx_key = max(self.rank_sum.iteritems(), key=operator.itemgetter(1))[0]
        mx = self.rank_sum[mx_key]
        for t in self.rank_sum:
            self.rank_sum[t] = self.rank_sum[t] / mx

    def rank_on_page(self, tw, df, postings):
        s = tw
        if df is 0:
            return
        m = math.log(float(self.total_docs + 1) / df, 10)
        s = s * m
        for x in postings:
            t = s * 50 * x[1]
            t = s / (49 + x[1])
            self.rank_pg[x[0]] = self.rank_pg[x[0]] + t

    def fetch_rank_on_page_features(self):
        for pair in self.fp:
            keyword = pair.split(',')[0]
            tw = float(pair.split(',')[1])
            # doc = self.col1.find_one({'_id': keyword + "_title"})
            # df = len(doc['posting'])
            # self.rank_on_page(tw, df, doc['posting'])
            # doc = self.col1.find_one({'_id': keyword + "_header"})
            # df = len(doc['posting'])
            # self.rank_on_page(tw, df, doc['posting'])
            # doc = self.col1.find_one({'_id': keyword + "_meta"})
            # df = len(doc['posting'])
            # self.rank_on_page(tw, df, doc['posting'])
            # doc = self.col1.find_one({'_id': keyword + "_cur_a"})
            # df = len(doc['posting'])
            # self.rank_on_page(tw, df, doc['posting'])
            # self.rank_on_page(tw, df, doc['posting'])
            # doc = self.col1.find_one({'_id': keyword + "_table"})
            # df = len(doc['posting'])
            # self.rank_on_page(df, doc['posting'])
            doc = self.col1.find_one({"_id": keyword + "_page"})
            df = len(doc['posting'])
            self.rank_on_page(tw, df, doc['posting'])
            # doc = self.col1.find_one({'_id': keyword + "_html"})
            # df = len(doc['posting'])
            # self.rank_on_page(tw, df, doc['posting'])

        # normalizing ranks
        mx_key = max(self.rank_pg.iteritems(), key=operator.itemgetter(1))[0]
        mx = self.rank_pg[mx_key]
        for t in self.rank_pg:
            self.rank_pg[t] = self.rank_pg[t] / mx

    def compute_final_ranks(self):
        for key in self.rank_sum:
            self.final_rank[key] = 0.1 * \
                self.rank_sum[key] + 0.9 * self.rank_pg[key]
        sorted_list = sorted(
            self.final_rank.items(), key=operator.itemgetter(1), reverse=True)
        for t in sorted_list:
            url = re.sub(r'[^\x00-\x7F]+', ' ', self.reverse_hashmap[t[0]])
            url = re.sub(r';', r'.', url)
            self.result.write(url +
                              "," + repr(self.final_rank[t[0]]))
            self.result.write('\n')

if __name__ == "__main__":
    obj = Vector_Space_Model()
    obj.fetch_and_rank_summary()
    obj.fetch_rank_on_page_features()
    obj.compute_final_ranks()
