""" THIS module is for indexing the on page features of a URL
 here a collection is formed and each word is treated as document.
 Each document has a id from which it can be accessed. With each word
 a posting list is associated which has two attributes first the id of
 the URL and 2nd count of the number of times a word
 appears in a given URL """


from pymongo import MongoClient
from stemming.porter2 import stem
from get_text_from_tag_for_url import get_individual_tags_text
from get_text_from_html_tag import get_html_tag_text
import re


class on_page_summarizer:

    def __init__(self):
        # for connection establishing
        self.client = MongoClient('localhost', 27017)

        # project name
        self.db1 = self.client['test_project']

        # for getting text of a given url
        self.get_obj = None
        self.get_html_text_obj = None

        self.fp = open('stems.txt', 'r').read().split('\n')

        # to find the document for finding url an did mapping
        self.doc = self.db1.summary.find_one({"_id": "_hashmap"})
        # to get the dictionary
        self.dic = self.doc['mapping']
        # getting the id of URL
        self.id_of_url = None

    def get_dict_words(self, on_page_summary_for_given_tag):
        word_stems = []
        stemmed_words_list = on_page_summary_for_given_tag.lower().split()
        for word in stemmed_words_list:
            word_stems.append(stem(word))
        key_dic = {}
        for word in word_stems:
            if word in self.fp:
                if word in key_dic:
                    key_dic[word] = key_dic[word] + 1
                else:
                    key_dic[word] = 1

        return key_dic

    # HERE id of url is generated before it is called
    def add_to_db_posting(self, keyword, count, tag):
        doc = self.db1.on_page_summary.find_one({"_id": keyword + "_" + tag})
        posting_list = doc['posting']
        # adding the new value at coorect position in the list
        posting_list.append([self.id_of_url, count])
        print posting_list
        # updating the list in database
        self.db1.on_page_summary.update(
            {"_id": keyword + "_" + tag},
            {"posting": posting_list}
        )

    def for_title(self):

        title_text = self.get_obj.get_title_text()
        # convering the dictionary to key, value pairs stored in a list
        key_dic = {}
        key_dic = self.get_dict_words(title_text)
        for word in key_dic:
            self.add_to_db_posting(word, key_dic[word], "title")

    def for_meta(self):
        meta_text = self.get_obj.get_meta_text()
        key_dic = {}
        key_dic = self.get_dict_words(meta_text)
        # convering the dictionary to key, value pairs stored in a list
        for word in key_dic:
            self.add_to_db_posting(word, key_dic[word], "meta")

    def for_header(self):
        header_text = self.get_obj.get_header_text()
        key_dic = {}
        key_dic = self.get_dict_words(header_text)
        for word in key_dic:
            self.add_to_db_posting(word, key_dic[word], "header")

    def for_table(self):
        table_text = self.get_obj.get_table_text()
        key_dic = {}
        key_dic = self.get_dict_words(table_text)
        for word in key_dic:
            self.add_to_db_posting(word, key_dic[word], "table")

    def for_html(self):
        html_text = self.get_html_text_obj.get_html_text()
        key_dic = {}
        key_dic = self.get_dict_words(html_text)
        for word in key_dic:
            self.add_to_db_posting(word, key_dic[word], "html")

    def fetch_updated_list(self):
        self.doc = self.db1.summary.find_one({"_id": "_hashmap"})
        # to get the dictionary
        self.dic = self.doc['mapping']

    def index_on_page_summary(self, src_content, url):
        self.fetch_updated_list()
        self.get_obj = get_individual_tags_text(src_content)
        self.get_html_text_obj = get_html_tag_text(src_content)
        url = re.sub(r'\.', r';', url.encode('utf-8'))
        try:
            self.id_of_url = self.dic[url]
        except KeyError as e:
            print "Key Error-------"
            print e
        self.for_html()
        self.for_title()
        self.for_meta()
        self.for_header()
        self.for_table()
