from bs4 import BeautifulSoup
import re
from pymongo import MongoClient
from stemming.porter2 import stem
from urlparse import urljoin
import requests


class summarizer:

    def __init__(self):
        # establishing connection with the mongodb database
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['test_project']
        self.col = self.db.summary
        self.cur_id = -1
        self.keyword_list = open("stems.txt", "r").read().split('\n')

        # fetching the mapping list from database
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

    def create_and_index_summary(self, base_url, src_content):
        """This function create a summary document for each
        link present on the page and create a posting list which
        is stored in the directory Postings

        Posting list will be created for each link in anchor tag"""

        # creating a soup object from requests object
        soup = BeautifulSoup(src_content, 'lxml')
        # Obtaining the title string of page
        title_string = ""
        if soup.title is not None:
            title_string = soup.title.string
            if title_string is not None:
                title_string = re.sub(r'@', r' @ ', title_string)
                title_string = re.sub(r'[^a-zA-Z0-9@ ]', r'',
                                      title_string.encode('utf-8').lower())

        for anchor_tag in soup.find_all('a', href=True):

            # filtering the out of domain urls
            regex = r'^https?://([^.]*\.)?[^.]*\.stanford\.edu[^.]*'
            pattern = re.compile(regex, re.UNICODE)
            temp_url = urljoin(base_url, anchor_tag['href'])
            if re.match(pattern, temp_url.encode('utf-8')) is None:
                continue

            # Adding the anchor text to summary
            anchor_string = anchor_tag.string
            summary = ""
            if anchor_string is not None:
                summary = re.sub(r'@', r' @ ', anchor_string.encode('utf -8'))
                summary = re.sub(r'[^a-zA-Z0-9@ ]', r'',
                                 summary.lower())
            # Adding the href of anchor tag to summary
            try:
                href = anchor_tag['href']
                href = re.sub(r'@', r' @ ', href.encode('utf -8'))
                href = re.sub(r'[^a-zA-Z0-9@ ]', r'',
                              href.lower())
                summary = summary + " " + href
            except AttributeError as e:
                print e
            # Adding the text of previous and next siblings to tags to summary
            n_sibling = anchor_tag.next_sibling
            while n_sibling is not None:
                # n_sibling.string can be None for DEBUGGING
                sib_string = n_sibling.string
                if sib_string is not None:
                    sib_string = re.sub(
                        r'@', r' @ ', sib_string.encode('utf-8'))
                    sib_string = re.sub(r'[^a-zA-Z0-9@ ]', r'',
                                        sib_string.lower())
                    if sib_string != "":
                        summary = summary + " " + sib_string
                        break
                n_sibling = n_sibling.next_sibling

            p_sibling = anchor_tag.previous_sibling
            while p_sibling is not None:
                sib_string = p_sibling.string
                if sib_string is not None:
                    sib_string = re.sub(
                        r'@', r' @ ', sib_string.encode('utf-8'))
                    sib_string = re.sub(r'[^a-zA-Z0-9@ ]',
                                        r'', sib_string.lower())
                    if sib_string != "":
                        summary = summary + " " + sib_string
                        break
                p_sibling = p_sibling.previous_sibling

            # Adding the content of heading tag that appears just above
            # the given tag in the parse tree
            # regular expression for heading tags

            regex = r'h[0-9]'
            pattern = re.compile(regex)
            heading_tag = anchor_tag.parent
            while heading_tag is not None:
                if re.match(pattern,
                            heading_tag.name.encode('utf-8')) is not None:
                    heading_string = heading_tag.string
                    if heading_string is not None:
                        heading_string = re.sub(
                            r'@', r' @ ', heading_string.encode('utf-8'))
                        heading_string = re.sub(
                            r'[^a-zA-Z0-9@  ]', r'',
                            heading_string.lower())
                        if heading_string != "":
                            summary = summary + " " + heading_string
                            break
                heading_tag = heading_tag.parent

            # Adding the title text to summary
            if title_string is not None and title_string != "":
                summary = summary + " " + title_string
            self.index_summary(temp_url, summary)
            summary = ""


if __name__ == '__main__':
    htmlfile = requests.get('http://stanford.edu')
    obj = summarizer()
    obj.create_and_index_summary('http://stanford.edu', htmlfile.text)
