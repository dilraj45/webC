from bs4 import BeautifulSoup
import re
import requests


def create_summary(src_content):
    """This function create a summary document for each
    link present on the page and create a posting list which
    is stored in the directory Postings

    Posting list will be created for each link in anchor tag"""

    # creating a soup object from requests object
    soup = BeautifulSoup(src_content, 'lxml')
    # Obtaining the title string of page
    title_string = soup.title.string
    if title_string is not None:
        title_string = re.sub(r'[^a-zA-Z0-9@ ]', r'', title_string.encode())

    for anchor_tag in soup.find_all('a', href=True):

        # adding the anchor text to summary
        anchor_string = anchor_tag.string
        if anchor_string is not None:
            summary = re.sub(r'[^a-zA-Z0-9@ ]', r'',
                             anchor_string.encode('utf-8'))

        # adding the text of previous and next siblings to tags to summary
        n_sibling = anchor_tag.next_sibling
        while n_sibling is not None:
            # n_sibling.string can be None for DEBUGGING
            sib_string = n_sibling.string
            if sib_string is not None:
                sib_string = re.sub(r'[^a-zA-Z0-9@ ]', r'',
                                    sib_string.encode('utf-8'))
                if sib_string != "":
                    summary = summary + " " + sib_string
                    break
            n_sibling = n_sibling.next_sibling

        p_sibling = anchor_tag.previous_sibling
        while p_sibling is not None:
            sib_string = p_sibling.string
            if sib_string is not None:
                sib_string = re.sub(r'[^a-zA-Z0-9@ ]',
                                    r'', sib_string.encode('utf-8'))
                if sib_string != "":
                    summary = summary + " " + sib_string
                    break
            p_sibling = p_sibling.previous_sibling

        # Adding the content of heading tag that appears just above the given
        # tag in the parse tree
        # regular expression for heading tags
        regex = r'h[0-9]'
        pattern = re.compile(regex)
        heading_tag = anchor_tag.parent
        while heading_tag is not None:
            if re.match(pattern, heading_tag.name.encode('utf-8')) is not None:
                heading_string = heading_tag.string
                if heading_string is not None:
                    heading_string = re.sub(
                        r'[^a-zA-Z0-9@  ]', r'',
                        heading_string.encode('utf-8'))
                    if heading_string != "":
                        summary = summary + " " + heading_string
                        break
            heading_tag = heading_tag.parent

        # Adding the title text to summary
        # if title_string is not None and title_string != "":
        #     summary = summary + " " + title_string
        print summary
        # Indexing the summary of link
        # Index_summary(summary, anchor_tag['href'])
        summary = ""
htmlfile = requests.get("http://web.mit.edu")
create_summary(htmlfile.content)
