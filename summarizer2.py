from bs4 import BeautifulSoup
import re
import requests


class summary_generator:

    def __init__(self):
        self.queue = []
        self.links_summary = {}
        self.title_string = ""
        self.heading_string = ""

    def generate_summary(self, idx):
        prev = idx - 1
        prev_string = None
        anchor_text = self.queue[idx].string
        if anchor_text is not None:
            anchor_text = re.sub(r'[^a-zA-Z0-9@ ]', r'',
                                 anchor_text.encode('utf-8'))
        else:
            anchor_text = ""
        while prev >= 0:
            prev_string = self.queue[prev].string
            if prev_string is not None:
                prev_string = re.sub(r'[^a-zA-Z0-9@ ]', r'',
                                     prev_string.encode('utf-8'))
                if prev_string != "":
                    break
            prev = prev - 1
        nxt = idx + 1
        nxt_string = None
        while nxt < len(self.queue):
            nxt_string = self.queue[nxt].string
            if nxt_string is not None:
                nxt_string = re.sub(r'[^a-zA-Z0-9@ ]', r'',
                                    nxt_string.encode('utf-8'))
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
        print "Length of list generated at level : " + str(len(self.queue))
        for idx, child in enumerate(self.queue):
            if child.name == 'title':
                # if it is title tag
                print "title tag found "
            if child.name == 'h1':
                print "h1 tag found "
            if child.name == 'a':
                summary = self.generate_summary(idx)
                print "----------URL----------:" + str(child['href'])
                print "Index: " + str(idx)
                print summary

    def add_children_to_queue(self, parent_tag):
        if parent_tag is None or parent_tag.name is None:
            return
        children = list(parent_tag.children)
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
            tag = self.queue[0]
            self.queue.pop(0)
            self.add_children_to_queue(tag)
            i = i + 1
        self.bfs()

    def bfs_level(self):
        while len(self.queue) > 0:
            self.bfs()

    def get_summary(self, src_content):
        """This function create a summary document for each
        link present on the page and create a posting list which
        is stored in the directory Postings

        Posting list will be created for each link in anchor tag"""

        # creating a soup object from requests object
        soup = BeautifulSoup(src_content, 'lxml')
        root = soup.find('html')
        self.queue.append(root)
        self.bfs_level()


htmlfile = requests.get('http://web.mit.edu')
htmlfile.raise_for_status()
obj = summary_generator()
print obj.get_summary(htmlfile.text)
