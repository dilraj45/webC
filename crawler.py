from getSource import get_html_text
import requests
import re
import bs4
from urlparse import urljoin
from sets import Set

visited = Set()
queue = list()
base = u"http://web.mit.edu"
regex = r'^https?://([^.]*\.)?[^.]*\.mit\.edu[^.]*'
pattern = re.compile(regex, re.UNICODE)

# opening a file
result_file = open('result.txt', 'w')
er_file = open('errors.txt', 'w')


def add_links_to_queue(url):
    try:
        sp = bs4.BeautifulSoup(get_html_text(url), 'lxml')
        for tag in sp.find_all('a', href=True):
            link = urljoin(base, tag['href'])
            if re.match(pattern, link) is not None:
                if link not in visited:
                    queue.append(link)
                    result_file.write(str(link) + '\n')
                    visited.add(link)

    except requests.RequestException as e:
        print str(e) + '\n'
        er_file.write(url + '\n')
        er_file.write(str(e) + '\n\n')


def bfs(level):
    length = len(queue)
    print "Length of queue: " + str(length) + " at level" + str(level)
    if length < 0 or level <= 0:
        return
    i = 0
    while i < length:
        add_links_to_queue(queue[0])
        queue.pop(0)
        i = i + 1
    bfs(level - 1)


def bfs_level(level):
    queue.append(base)
    visited.add(base)
    bfs(level)


bfs_level(4)
