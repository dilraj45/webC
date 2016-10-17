# this module is for finding the ktml text for a given url
# here in this text of individua ltags can found

import bs4
import re


class get_html_tag_text:

    def __init__(self, src_content):
        self.soup = bs4.BeautifulSoup(src_content, 'lxml')

    def get_html_text(self):
        text = ""
        if self.soup is None:
            return ""
        try:
            html_tag = self.soup.find('html')
            text = text + html_tag.get_text()

        except (TypeError, AttributeError):
            pass
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)
        text = re.sub(r'@', r' @ ', text.encode('utf -8'))
        text = re.sub(r'[^a-zA-Z0-9@ ]', '', text.encode('utf -8'))
        return text
