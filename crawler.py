"""Web Crawler"""
from urlparse import urljoin
import re
from sets import Set
import bs4
from getSource import getSource
from summarizer import summarizer
from pymongo import MongoClient
import requests

visited = Set()
queue = list()
regex = r'^https?://([^.]*\.)?[^.]*\.mit\.edu[^.]*'
pattern = re.compile(regex, re.UNICODE)

# opening file one for storing the resultant url and one
# for holding errors and exceptions
result_file = open('result.txt', 'w+')
er_file = open('errors.txt', 'w+')


def add_links_to_queue(url):
    try:
        ht_text = req_obj.get_html_text(url)
        if ht_text is None:
            return
        sp = bs4.BeautifulSoup(ht_text, 'lxml')
        for tag in sp.find_all('a', href=True):
            base = 'http://' + req_obj.get_base_hostname()
            link = urljoin(base, tag['href'])
            if re.match(pattern, link) is not None:
                if link not in visited:
                    queue.append(link)
                    result_file.write((link).encode('utf-8') + '\n')
                    visited.add(link)

    except (requests.RequestException, requests.exceptions.SSLError)as trace:
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
        add_links_to_queue(queue[0])
        try:
            sum_obj.create_and_index_summary(
                req_obj.get_base_hostname(), req_obj.get_html_text(queue[0]))
        except requests.RequestException as trace:
            print str(trace) + '\n'
            er_file.write(queue[0] + '\n')
            er_file.write(str(trace) + '\n\n')
        queue.pop(0)
        i = i + 1
    bfs(level - 1)


def bfs_level(url_begin, level):
    queue.append(url_begin)
    visited.add(url_begin)
    bfs(level)


def database_setup():
    # setting up the database
    client = MongoClient('localhost', 27017)
    db = client["test_project"]
    col = db["summary"]
    keys = open('stems.txt', 'r').read().split('\n')
    col.insert({"_id": "_hashmap",
                "Total_urls": 0,
                "mapping": {}})
    for word in keys:
        col.insert({"_id": word, "df": 0, "postings": []})

if __name__ == '__main__':
    # Creating an object of class getSource
    database_setup()
    req_obj = getSource()
    sum_obj = summarizer()
    bfs_level('http://web.mit.edu', 5)
