"""This module aims at optimizing query vector so as to improve the
results obtained from vector space model"""

from pymongo import MongoClient
import re

# opening required files
keywords = open('stem_tw.txt', 'r+').read().split('\n')
query = {}
for i in keywords:
    print i.split(',')[1]
    query[i.split(',')[0]] = float(i.split(',')[1])

positiveExp = open('people.txt', 'r').read().split('\n')
# negativeExp = open('negativeResults.txt', 'r').split('\n')
newQuery = open('new_tw.txt', 'w')
total_doc = len(positiveExp)
# fetching required contents from database
client = MongoClient()
temp = client['stanford_test'].summary.find_one({"_id": "_hashmap"})['mapping']
inv_map = {v: k for k, v in temp.iteritems()}


def check_positive(url):
    if url in positiveExp:
        return True
    else:
        return False


def url_for_id(id):
    try:
        url = inv_map[id]
        url = re.sub(r';', r'.', url)
        return url
    except KeyError:
        return None


def rocchio_feedback():
    beta = 0.8
    gamma = 0.1
    for value in keywords:
        key = value.split(',')[0]

        # fetching postings list for that keyword
        key_ = client['stanford_test'].summary.find_one({"_id": key})
        key_posting = key_['postings']
        for i in key_posting:
            url = url_for_id(i[0])
            if url is None:
                continue
            if check_positive(url.encode('utf-8')):
                query[key] += (beta * i[1])/total_doc
            else:
                query[key] -= (gamma * i[1])/total_doc;


if __name__ == '__main__':
    rocchio_feedback()
    for i in query:
        newQuery.write(i + "," + str(query[i]) + "\n")
