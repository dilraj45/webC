from bs4 import BeautifulSoup
from pymongo import MongoClient
from urlparse import urljoin
from stemming.porter2 import stem
import re
import requests


class summary_generator:

    def __init__(self):
        self.queue = []
        self.links_summary = {}
        self.title_string = ""
        self.heading_string = ""
        self.base_url = None
        # establishing connection with Mongodb database
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['test_project']
        self.col = self.db.summary2
        self.cur_id = -1
        self.keyword_list = open('stems.txt', 'r').read().split('\n')

        # fetching mapping list from database
        doc = self.col.find_one({"_id": "_hashmap"})
        self._hash = {}
        self._hash = doc['mapping']

    def add_to_db_posting(self, word, tf, flag):
        # adding the new entry to 'word' posting list
        # fetching the already existing posting list
        doc = self.col.find_one({"_id": word})
        l = doc['postings']

        # if flag is true then the document id may already be present in the
        # posting list of keyword
        if flag:
            # checking if document id is already present in the posting of word
            for term in l:
                if term[0] == self.cur_id:
                    term[1] = term[1] + tf
                    self.col.update({"_id": word},
                                    {"df": len(l),
                                     "postings": l})
                    return
        # adding the new value at correct position in the list
        index = 0
        while index < len(l) and tf <= l[index][1]:
            index = index + 1
        l.insert(index, [self.cur_id, tf])

        # updating the list in database
        self.col.update({"_id": word},
                        {"df": len(l),
                         "postings": l})

    def index_summary(self, url, summary):
        # assigning a unique id to every url
        flag = False
        temp = re.sub(r'\.', r';', url)
        if temp in self._hash:
            self.cur_id = self._hash[temp]
            flag = True
        else:
            # generate new id for
            self.cur_id = len(self._hash) + 1
            self._hash[temp] = self.cur_id
            # updating the same in database
            self.col.update({"_id": "_hashmap"},
                            {"Total_urls": len(self._hash),
                             "mapping": self._hash})

        # Indexing the summary
        # Stemming of the summary
        word_stems = []
        for word in summary.lower().split():
            word_stems.append(stem(word))
        keys_dic = {}
        for word in word_stems:
            if word not in self.keyword_list:
                continue
            if word in keys_dic:
                keys_dic[word] = keys_dic[word] + 1
            else:
                keys_dic[word] = 1
        # converting the dictionary to key, value pairs stored in a list
        for word in keys_dic:
            self.add_to_db_posting(word, keys_dic[word], flag)

    def generate_summary(self, idx):
        prev = idx - 1
        prev_string = None
        anchor_text = None
        try:
            anchor_text = self.queue[idx].string
        except AttributeError as e:
            print e
        if anchor_text is not None:
            anchor_text = re.sub(r'@', r' @ ', anchor_text.encode('utf-8'))
            anchor_text = re.sub(r'[^a-zA-Z0-9@ ]', r' ', anchor_text)
        else:
            anchor_text = ""
        # Adding the anchor tag's href to anchor_text
        try:
            href = self.queue[idx]['href']
            href = re.sub(r'@', r' @ ', href.encode('utf-8'))
            href = re.sub(r'[^a-zA-Z0-9@ ]', r' ', href)
            anchor_text = anchor_text + " " + href
        except (AttributeError, TypeError) as e:
            print e
        while prev >= 0:
            prev_string = None
            try:
                prev_string = self.queue[prev].string
            except AttributeError:
                pass
            if prev_string is not None:
                prev_string = re.sub(r'@', r' @ ', prev_string.encode('utf-8'))
                prev_string = re.sub(r'[^a-zA-Z0-9@ ]', r' ', prev_string)
                if prev_string != "":
                    break
            prev = prev - 1
        nxt = idx + 1

        nxt_string = None
        while nxt < len(self.queue):
            nxt_string = self.queue[nxt].string
            if nxt_string is not None:
                nxt_string = re.sub(r'@', r' @ ', nxt_string.encode('utf-8'))
                nxt_string = re.sub(r'[^a-zA-Z0-9@ ]', r' ', nxt_string)
                if nxt_string != "":
                    break
            nxt = nxt + 1
        if nxt_string is not None and prev_string is not None:
            return nxt_string + " " + prev_string + " " + anchor_text
        elif nxt_string is not None:
            return nxt_string + " " + anchor_text
        elif prev_string is not None:
            return prev_string + " " + anchor_text
        else:
            return ""

    def search_and_summarize_tag(self):
        summary = ""
        for idx, child in enumerate(self.queue):
            # if it is title tag
            try:
                if child.name == 'title':
                    if child.string is not None:
                        self.title_string = child.string.encode('utf-8')
                # if tag is one from headings tag
                regex = r'h[0-9]'
                pattern = re.compile(regex)
                if child.name is not None:
                    if re.match(pattern, child.name.encode('utf-8')) \
                            is not None:
                        if child.string is not None:
                            self.heading_string = self.heading_string + \
                                child.string.encode('utf-8')

                # if tag is an anchor tag
                if child.name == 'a':
                    # creating a complete url
                    try:
                        temp_url = urljoin(
                            self.base_url, child['href'])
                        summary = self.generate_summary(idx)
                        self.index_summary(temp_url, summary)
                    except KeyError:
                        pass
            except AttributeError:
                print "Attribute error"

    def add_children_to_queue(self, parent_tag):
        try:
            if parent_tag is None or parent_tag.name is None:
                return
        except AttributeError:
            return
        children = parent_tag.contents
        for child in children:
            if child is not None:
                self.queue.append(child)

    def bfs(self):
        length = len(self.queue)
        i = 0
        if length <= 0:
            return
        self.search_and_summarize_tag()
        while i < length:
            if self.queue[0] is not None:
                tag = self.queue[0]
                self.add_children_to_queue(tag)
            self.queue.pop(0)

            i = i + 1
        self.bfs()

    def bfs_level(self):
        while len(self.queue) > 0:
            self.bfs()

    def create_and_index_summary(self, base_url, src_content):
        """This function create a summary document for each
        link present on the page and create a posting list which
        is stored in the directory Postings

        Posting list will be created for each link in anchor tag"""

        # creating a soup object from requests object
        self.base_url = base_url
        soup = BeautifulSoup(src_content, 'lxml')
        root = soup.find('html')
        self.queue.append(root)
        self.bfs_level()

if __name__ == '__main__':
    htmlfile = requests.get('http://web.mit.edu')
    htmlfile.raise_for_status()
    obj = summary_generator()
    print obj.create_and_index_summary('http://web.mit.edu', htmlfile.text)
