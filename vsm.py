"""Implementing vector space model"""
from pymongo import MongoClient
import math
import operator
import re


class VectorSpaceModel:

    def __init__(self):
        client = MongoClient()
        db = client['test_project']
        self.col = db.summary
        self.col1 = db.on_page_summary

        # fetching hash map in main memory
        doc = self.col.find_one({"_id": "_hashmap"})
        self.hash_map = doc['mapping']
        self.reverse_hash_map = {v: k for k, v in self.hash_map.items()}
        self.total_docs = doc['Total_urls']

        # Initializing a dictionary for holding the ranks of each page
        # Ranks are initialized to zero
        self.rank_sum = {}
        self.rank_pg = {}
        self.final_rank = {}
        for key in self.hash_map:
            self.rank_sum[self.hash_map[key]] = 0
            self.rank_pg[self.hash_map[key]] = 0

        # Fetching the keyword list
        self.fp = open('new_tw.txt', 'r').read().split('\n')
        self.result = open('temp.txt', 'w+')

    def rank_summary(self, tw, df, postings):
        # fetching the posting list
        s = tw
        if df is 0:
            return
        m = math.log(float(self.total_docs + 1) / df, 10)
        s *= m
        for x in postings:
            try:
                t = s * 51 * x[1]
                t /= (50 + x[1])
                self.rank_sum[x[0]] += t
            except KeyError as e:
                print e

    def upload_ranks_db(self):
        self.col.insert({"_id": "ranks",
                         "ranks": self.rank_sum})

    def fetch_and_rank_summary(self, list_urls=None, link_weights=None):
        """If list_urls is None then it updates result in local copy and return nothing
        else it  Returns the dictionary holding the link passed to this function as arg
        , along with it's rank calculated according to vector space model. If a dictionary
        is passed as argument then it update the value in that"""
        for pair in self.fp:
            keyword = pair.split(',')[0]
            tw = float(pair.split(',')[1])
            doc = self.col.find_one({'_id': keyword})
            df = doc['df']
            self.rank_summary(tw, df, doc["postings"])
        # normalizing ranks
        mx_key = max(self.rank_sum.iteritems(), key=operator.itemgetter(1))[0]
        mx = self.rank_sum[mx_key]
        if mx != 0:
            for t in self.rank_sum:
                self.rank_sum[t] = self.rank_sum[t] / mx
        if list_urls is not None:
            if link_weights is None:
                link_ranks = {}
                try:
                    for link in list_urls:
                        url = link
                        link = re.sub(r'\.', r';', link)
                        link_ranks[url] = self.rank_sum[self.hash_map[link]]
                    return link_ranks
                except KeyError:
                    pass
            else:
                for link in list_urls:
                    url = link
                    link = re.sub(r'\.', r';', link)
                    link_weights[url] = self.rank_sum[self.hash_map[link]]

    def rank_on_page(self, tw, df, postings):
        s = tw
        if df is 0:
            return
        m = math.log(float(self.total_docs + 1) / df, 10)
        s *= m
        for x in postings:
            try:
                t = s * 50 * x[1]
                t /= (49 + x[1])
                self.rank_pg[x[0]] += t
            except IndexError:
                pass

    def fetch_rank_on_page_features(self):
        for pair in self.fp:
            keyword = pair.split(',')[0]
            tw = float(pair.split(',')[1])
            doc = self.col1.find_one({'_id': keyword + "_title"})
            df = len(doc['posting'])
            self.rank_on_page(tw, df, doc['posting'])
            # doc = self.col1.find_one({'_id': keyword + "_header"})
            # df = len(doc['posting'])
            # self.rank_on_page(tw, df, doc['posting'])
            doc = self.col1.find_one({'_id': keyword + "_meta"})
            df = len(doc['posting'])
            self.rank_on_page(tw, df, doc['posting'])
            doc = self.col1.find_one({'_id': keyword + "_cur_a"})
            df = len(doc['posting'])
            self.rank_on_page(tw, df, doc['posting'])
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
            if mx == 0:
                continue
            self.rank_pg[t] = self.rank_pg[t] / mx

    def compute_final_ranks(self):
        self.fetch_and_rank_summary()
        self.fetch_rank_on_page_features()
        for key in self.rank_sum:
            self.final_rank[key] = 0.1 * \
                self.rank_sum[key] + 0.9 * self.rank_pg[key]
        sorted_list = sorted(
            self.final_rank.items(), key=operator.itemgetter(1), reverse=True)
        for t in sorted_list:
            url = re.sub(r'[^\x00-\x7F]+', ' ', self.reverse_hash_map[t[0]])
            url = re.sub(r';', r'.', url)
            self.result.write(url +
                              "," + repr(self.final_rank[t[0]]))
            self.result.write('\n')

if __name__ == "__main__":
    obj = VectorSpaceModel()
    obj.compute_final_ranks()
