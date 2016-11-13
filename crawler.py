"""Web Crawler"""
from urlparse import urljoin
import re
import bs4
from getSource import GetSource
from summarizer import Summarizer
from indexer_on_page import OnPageSummarizer
from summarizer2 import summary_generator
from pymongo import MongoClient
import requests


visited = set()
queue = list()
regex = r'^https?://([^.]*\.)?[^.]*\.stanford\.edu[^.]*'
pattern = re.compile(regex, re.UNICODE)

# opening file one for storing the resultant url and one
# for holding errors and exceptions
result_file = open('result.txt', 'w+')
er_file = open('errors.txt', 'w+')
lk_nr = open('ext.txt', 'r').read().split('\n')


def check_link(link):
    for ext in lk_nr:
        if ext in link:
            return False
    return True


def add_links_to_queue(ht_text, url):
    try:
        if ht_text is None:
            return
        sp = bs4.BeautifulSoup(ht_text, 'lxml')
        for tag in sp.find_all('a', href=True):
            base = req_obj.get_base_url()
            link = urljoin(base, tag['href'])
            if re.match(pattern, link) is not None:
                if link not in visited:
                    if check_link(link):
                        queue.append(link)
                        result_file.write(link.encode('utf-8') + '\n')
                        visited.add(link)
    except (requests.RequestException, requests.exceptions.SSLError) as trace:
        print str(trace) + '\n'
        er_file.write(url + '\n')
        er_file.write(str(trace) + '\n\n')


def bfs(level):
    length = len(queue)
    print "Length of queue: " + str(length) + " at level " + str(level)
    if length <= 0 or level <= 0:
        return
    i = 0
    while i < length:
        try:
            text = req_obj.get_html_text(queue[0])
            if text is None:
                raise requests.RequestException()
            add_links_to_queue(text, queue[0])
            # summary generated using summarizer1
            sum_obj.create_and_index_summary(
                req_obj.get_base_url(), text)
            # summary generated using summarizer2
            sum_obj2.create_and_index_summary(
                req_obj.get_base_url(), text)
            on_pg_sum.index_on_page_summary(text, queue[0])
        except requests.RequestException as trace:
            print str(trace) + '\n'
            er_file.write(queue[0] + '\n')
            er_file.write(str(trace) + '\n\n')
        queue.pop(0)
        i += 1
    bfs(level - 1)


def bfs_level(url_begin, level):
    queue.append(url_begin)
    visited.add(url_begin)
    bfs(level)


def database_setup():
    # setting up the database
    client = MongoClient('localhost', 27017)
    db = client["test_project"]
    col1 = db['summary']
    keys = open('stems.txt', 'r').read().split('\n')
    col1.insert({"_id": "_hashmap",
                 "Total_urls": 1,
                 "mapping": {'https://www;stanford;edu': 0}})
    # setting up summary2 in db
    col2 = db['summary2']
    col2.insert({"_id": "_hashmap",
                 "Total_urls": 1,
                 "mapping": {'https://www;stanford;edu': 0}})
    for word in keys:
        db.on_page_summary.insert(
            {"_id": word + "_title", "posting": []})
        db.on_page_summary.insert(
            {"_id": word + "_meta", "posting": []})
        db.on_page_summary.insert(
            {"_id": word + "_header", "posting": []})
        db.on_page_summary.insert(
            {"_id": word + "_table", "posting": []})
        db.on_page_summary.insert(
            {"_id": word + "_html", "posting": []})
        db.on_page_summary.insert(
            {"_id": word + "_cur_a", "posting": []})
        db.on_page_summary.insert(
            {"_id": word + "_a", "posting": []})
        db.on_page_summary.insert(
            {"_id": word + "_page", "posting": []})
        col1.insert({"_id": word, "df": 0, "postings": []})
        col2.insert({"_id": word, "df": 0, "postings": []})
    client.close()


if __name__ == '__main__':
    # Creating an object of class getSource
    database_setup()
    req_obj = GetSource()
    sum_obj = Summarizer()
    sum_obj2 = summary_generator()
    on_pg_sum = OnPageSummarizer()
    bfs_level('https://www.stanford.edu', 6)
