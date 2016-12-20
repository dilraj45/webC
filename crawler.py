"""Web Crawler"""
from urlparse import urljoin
import re
import bs4
from getSource import GetSource
from summarizer import Summarizer
from indexer_on_page import OnPageSummarizer
from summarizer2 import summary_generator
from vsm import VectorSpaceModel
from pymongo import MongoClient
from enum import Enum
import requests


class OrderingMetric(Enum):
    """enum ordering metric can use three value namely, VSM , FORWARD_LINK_COUNT,
    BACK_LINK_COUNT as ordering metric"""
    BACK_LINK_COUNT = 1
    FORWARD_LINK_COUNT = 2
    VSM = 3

visited = set()
queue = list()
regex = r'^https?://([^.]*\.)?[^.]*\.pec\.ac[^.]*'
pattern = re.compile(regex, re.UNICODE)
result_file = open('result.txt', 'w+')
er_file = open('errors.txt', 'w+')
lk_nr = open('ext.txt', 'r').read().split('\n')
ord_metric = OrderingMetric.VSM


def database_setup():
    """database_setup method is responsible for some initial database setups which
    are required by the crawler to work"""
    client = MongoClient('localhost', 27017)
    db = client["test_project"]
    col1 = db['summary']
    keys = open('stems.txt', 'r').read().split('\n')
    col1.insert({"_id": "_hashmap",
                 "Total_urls": 1,
                 "mapping": {'http://www;pec;ac;in': 0}})
    # setting up summary2 in db
    col2 = db['summary2']
    col2.insert({"_id": "_hashmap",
                 "Total_urls": 1,
                 "mapping": {'http://www;pec;ac;in': 0}})
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


def check_for_file_link(link):
    """ Utility function,check_for_file_link checks whether or not argument passed
    to method is a link to a file or page. It return False in case the argument
    is a link file else it return True"""
    for ext in lk_nr:
        if ext in link:
            return False
    return True


def add_links_to_queue(ht_text, url):
    """add_links_to_queue is utility method used by bfs. It is responsible for
    fetching link from page passed as an argument and adding the links to
    queue for visiting if they already had not been visited."""
    try:
        if ht_text is None:
            return
        sp = bs4.BeautifulSoup(ht_text, 'lxml')
        for tag in sp.find_all('a', href=True):
            base = req_obj.get_base_url()
            link = urljoin(base, tag['href'])
            if re.match(pattern, link) is not None:
                if link not in visited:
                    if check_for_file_link(link):
                        queue.append(link)
                        visited.add(link)
    except (requests.RequestException, requests.exceptions.SSLError) as trace:
        print str(trace) + '\n'
        er_file.write(url + '\n')
        er_file.write(str(trace) + '\n\n')


def bfs(level):
    """ bfs is the method that actually ensure the traversal of web pages
    in accordance with level order paradigm. bfs uses breadth first search
    algorithm for graphs, thus it also keep track of already visited pages,
    in order to avoid visiting the same page again."""
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


def bfs_level(level):
    """ bfs_level method can be used to visit all the web pages in breadth
    first ordering i.e. without using any ordering metric to determine
    the order in which pages, should be visited. bfs_level restrict the
    depth up to which the pages are explored. Depth is determined by the
    value passed for level while calling bfs_level"""
    queue.append(seed_url)
    visited.add(seed_url)
    bfs(level)


def compare(l1, l2):
    """compare is a utility function used by sort method"""
    if link_weights[l1] < link_weights[l2]:
        return 1
    elif link_weights[l1] == link_weights[l2]:
        return 0
    else:
        return -1


def ordered_crawling():
    """ ordered_crawling method traverse the pages according to a particular
    ordering metric. Ordering metric is decided on the basis of value
    passed to ordering_metric as an argument. If the value ordering_metric is
    BACK_LINK_COUNT it uses back link count as ordering metric, if the value passed
    is FORWARD_LINK_COUNT then it uses forward link count as an ordering metric,
    if value passed is VSM it uses ranks calculated according to vector space model
    as an ordering metric."""
    queue.append(seed_url)
    visited.add(seed_url)
    while len(queue) >= 0:
        try:
            text = req_obj.get_html_text(queue[0])
            print queue[0]
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

            result_file.write(str(queue[0]) + ", " + str(link_weights[queue[0]]))
            er_file.write("###########" + str(link_weights) + "\n\n\n\n")
            update_weights(text)
            queue.sort(compare)
            result_file.write("\n")
        except requests.RequestException as trace:
            print str(trace) + '\n'
            er_file.write(queue[0] + '\n')
            er_file.write(str(trace) + '\n\n')
        del link_weights[queue[0]]
        queue.pop(0)


def get_num_forward_link(link):
    """Returns the total number of forward links present on the web page
    obtained from link passed as an argument"""
    text = req_obj.get_html_text(link)
    soup = bs4.BeautifulSoup(text, 'lxml')
    le = soup.find_all('a', href=True)
    return len(le)


def update_weights(text):
    """This method update the weights allocated to each link according to
    ordering metric chosen. Weights are updated in link_weights list."""
    soup = bs4.BeautifulSoup(text, 'lxml')
    if ord_metric == OrderingMetric.BACK_LINK_COUNT:
        for l in soup.find_all('a', href=True):
            base = req_obj.get_base_url()
            link = urljoin(base, l['href'])
            if re.match(pattern, link) is not None:
                if link not in link_weights:
                    link_weights[link] = 1
                else:
                    link_weights[link] += 1

    elif ord_metric == OrderingMetric.FORWARD_LINK_COUNT:
        for l in soup.find_all('a', href=True):
            base = req_obj.get_base_url()
            link = urljoin(base, l['href'])
            if re.match(pattern, link) is not None:
                if link not in link_weights:
                    link_weights[link] = get_num_forward_link(link)

    elif ord_metric == OrderingMetric.VSM:
        vsmObj = VectorSpaceModel()
        vsmObj.fetch_and_rank_summary(queue, link_weights)

if __name__ == '__main__':
    # Creating an object of class getSource
    database_setup()
    print "database setup done"
    req_obj = GetSource()
    sum_obj = Summarizer()
    sum_obj2 = summary_generator()
    on_pg_sum = OnPageSummarizer()
    seed_url = 'http://www.pec.ac.in'
    link_weights = {seed_url: 0}
    #bfs_level(6)
    ordered_crawling()
