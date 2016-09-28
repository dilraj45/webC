from getSource import*
from stemming.porter2 import stem
import bs4


class get_individual_tags_text:

    get_individual_tags_text(self):
        getSource get_source_obj = new getSource()
        self.soup = bs4.BeautifulSoup(getSource_obj.get_html_text(url), 'lxml')
        html_text = get_source_obj.get_html_text(URL)

    def get_title_text(self):
        try:
            for title_tag in self.soup_handler.find_all('title', href=True):
                text = text + title_tag.get_text()
        except Exception as e:
            # for debugging
            print e
            return text

    def get_meta_text(self):
        try:
            for meta_tag in self.soup_handler.find_all('meta', href=True):
                text = text + meta_tag.get_text()
        except Exception as e:
            # for debugging
            print e
            return text

# html_text = obj.get_html_text(url)
# obj.get_html_text(URL)


# get_individual_tags_text  tags_Object = new get_individual_tags_text()
