from pymongo import MongoClient
from stemming.porter2 import stem
from get_individual_tags_text import*


class on_page_summarizer:

    def __init__(self):
        # for connection establishing
        self.client = MongoClient('localhost', 27017)
        # project name
        self.db = self.client['test_p']
        # creating collections for every word in the keyword list
        # reading form file
        self.fp = open('stems.txt', 'r').read().split('\n')
        # for getting text of a given url
        self.get_obj = get_individual_tags_text()

        for keyword in self.fp:
            # here collections are made automatically here
            self.creating_documents_for_every_word(keyword)
            # 1st attribute is for word's id and 2nd for posting list

    def creating_documents_for_every_word(self, keyword):
        # using keywor das our id
        # for every keywor dwe need to store a opsting list
        self.db[keyword].insert(
            {"_id": keyword + "title", "postings": []})  # [] null list
        self.db[keyword].insert({"_id": keyword + "meta", "posting": []})
        # for finding a document with a given id
        # doc = self.db[keyword].find_one({"_id": "title"})

        # self.db.keyword.update(
        #     {"_id": "title"},
        #     {"postings": new_list})

    def get_dict_words(self, on_page_summary_for_given_tag):
        word_stems = []
        for word in on_page_summary_for_given_tag.lower().split():
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
    def add_to_db_posting(self, keyword, count, tag, id_URL):
        self.db[keyword].update
        (
            {"_id": keyword + tag},
            {"posting", [id_URL, count]}
        )

    def for_title(self):
        title_text = self.get_obj.get_title_text()
        # convering the dictionary to key, value pairs stored in a list
        key_dic = {}
        key_dic = self.get_dict_words(title_text)
        for word in key_dic:
            self.add_to_db_posting(word, key_dic[word], "title", id_URL)

    def for_meta(self):
        meta_text = self.get_obj.get_meta_text()

        key_dic = {}
        key_dic = obj.get_dict_words(meta_text)
        # convering the dictionary to key, value pairs stored in a list
        for word in key_dic:
            self.add_to_db_posting(word, key_dic[word], "meta", id_U`RL)

    def index_on_page_summary(self):
        # for every tag
        self.for_title()
        self.for_meta()


obj = on_page_summarizer()
obj.index_on_page_summary()
