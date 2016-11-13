# this module is for finding the html text for a given url
# here in this text of individual tags can found

from sumy.parsers.html import HtmlParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
import re
import bs4


class GetIndividualTagsText:

    def __init__(self, src_content, url):
        self.src_content = src_content
        self.soup = bs4.BeautifulSoup(self.src_content, 'lxml')
        self.LANGUAGE = "english"
        self.base_url = url

    def get_title_text(self):
        text = ""
        if self.soup is None:
            return ""
        try:
            for title_tag in self.soup.find_all('title'):
                text = text + " " + title_tag.get_text()

        except TypeError:
            pass
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)
        text = re.sub(r'@', r' @ ', text.encode('utf -8'))
        text = re.sub(r'[^a-zA-Z0-9@ ]', ' ', text.encode('utf -8'))
        return text

    def get_meta_text(self):
        text = ""
        if self.soup is None:
            return ""
        try:
            for meta_tag in self.soup.find_all('meta'):
                text = text + " " + meta_tag['content']
        except (TypeError, KeyError):
            pass
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)
        text = re.sub(r'@', r' @ ', text.encode('utf -8'))
        text = re.sub(r'[^a-zA-Z0-9@ ]', ' ', text.encode('utf -8'))
        return text

    def get_table_text(self):
        text = ""
        if self.soup is None:
            return ""
        try:
            for table_tag in self.soup.find_all('table'):
                text = text + " " + table_tag.get_text()
        except TypeError:
            pass
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)
        text = re.sub(r'@', r' @ ', text.encode('utf -8'))
        text = re.sub(r'[^a-zA-Z0-9@ ]', ' ', text.encode('utf -8'))
        return text

    def get_anchor_tag(self):
        text = ""
        if self.soup is None:
            return ""
        try:
            for tag in self.soup.find_all('a', href=True):
                text = text + " " + tag['href']
        except AttributeError as e:
            print e
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)
        text = re.sub(r'@', r' @ ', text.encode('utf -8'))
        text = re.sub(r'[^a-zA-Z0-9@ ]', ' ', text.encode('utf -8'))
        return text

    def get_header_text(self):
        text = ""
        if self.soup is None:
            return ""
        try:
            for header_tag in self.soup.find_all('h1'):
                text = text + header_tag.get_text() + " "

            for header_tag in self.soup.find_all('h2'):
                text = text + header_tag.get_text() + " "

            for header_tag in self.soup.find_all('h3'):
                text = text + header_tag.get_text() + " "

            for header_tag in self.soup.find_all('h4'):
                text = text + header_tag.get_text() + " "

            for header_tag in self.soup.find_all('h5'):
                text = text + header_tag.get_text() + " "

            for header_tag in self.soup.find_all('h6'):
                text = text + header_tag.get_text() + " "
        except TypeError:
            pass
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)
        text = re.sub(r'@', r' @ ', text.encode('utf -8'))
        text = re.sub(r'[^a-zA-Z0-9@ ]', ' ', text.encode('utf -8'))
        # print text
        return text

    def get_page_summary(self):
        parser = HtmlParser(
            self.src_content, Tokenizer(self.LANGUAGE), self.base_url)
        stemmer = Stemmer(self.LANGUAGE)
        summarizer = Summarizer(stemmer)
        summarizer.stop_words = get_stop_words(self.LANGUAGE)
        summary = ""
        try:
            for sentence in summarizer(parser.document, 10):
                summary = summary + " " + str(sentence)
            return summary
        except Exception:
            return ""
