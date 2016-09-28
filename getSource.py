"""This is module for fetching the source code of a page when provided
   with a url, this module uses request module. Using this module you
   can get the html text of page or binary response depending upon
   your requirements. This module also keep track of the url of page you
   are accessing, (this can be used to check any redirection) which can
   accessed by calling get_base_url or get_base_hostname method. This
   module handles exceptions thrown by request module and comes with
   stand by support mechanisim in case of network failure"""

from urlparse import urlparse
import requests
from retrying import retry


class getSource:

    def __init__(self):
        self.base_url = ""

    def get_base_url(self):
        return self.base_url

    def get_base_hostname(self):
        return urlparse(self.base_url).hostname

    def set_header(self):
        hdr = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:12.0)'
               ' Gecko/20100101 Firefox/21.0',
               'Accept':  'text/html,application/xhtml+xml,application/xml;'
               'q=0.9,*/*;q=0.8',
               'Accept-Charset': 'ISO-8859-1, utf-8; q=0.7,*; q=0.3',
               'Accept-Encoding': 'gzip, deflate',
               'Accept-Language': 'en-US,en;q=0.8'}
        return hdr

    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000)
    def wait_for_connection(self):
        test = requests.get('http://216.58.197.46', timeout=2)
        test.raise_for_status()
        return
    # retry if HTTP error or connection error occurs
    # delay between consecutive retries is between 5 to 10 seconds

    @retry(stop_max_attempt_number=5, wait_random_min=5000,
           wait_random_max=10000)
    def get_html_text(self, url):
        hdr = self.set_header()
        htmlfile = None
        try:
            htmlfile = requests.get(url, headers=hdr)
            self.base_url = htmlfile.url
            htmlfile.raise_for_status()
        except requests.exceptions.SSLError:
            # check for https
            # openSSL can be used to bypass the SSL layer
            print "SSLError exception caught"
        except requests.exceptions.ConnectionError:
            # checking for bad connection
            print "No Internet Connection!\nWaiting for connection"
            self.wait_for_connection()
            raise
        if htmlfile is not None:
            return htmlfile.text
        else:
            return None

    @retry(stop_max_attempt_number=5, wait_random_min=5000,
           wait_random_max=10000)
    def get_html_binary_response(self, url):
        hdr = self.set_header()
        try:
            htmlfile = requests.get(url, headers=hdr)
            self.base_url = htmlfile.url
            htmlfile.raise_for_status()
        except requests.exceptions.SSLError:
            # check for https
            # openSSL can be used to deal with SSL Error
            print "SSLError exception caught"
        except requests.exceptions.ConnectionError:
            print "No Internet Connection!\nWaiting for connection"
            self.wait_for_connection()
            raise
        return htmlfile.content

    @retry(stop_max_attempt_number=5, wait_random_min=5000,
           wait_random_max=10000)
    def get_html_text_with_params(self, url, payload):
        # this method send requests with parameters in query to particular URL
        # payloads is a dictionary comprising of key value pair
        hdr = self.set_header()
        try:
            htmlfile = requests.get(url, headers=hdr, params=payload)
            self.base_url = htmlfile.url
            htmlfile.raise_for_status()
        except requests.exceptions.SSLError:
            # check for https
            print "SSLError exception caught"
        except requests.exceptions.ConnectionError:
            print "No Internet Connection!\nWaiting for connection"
            self.wait_for_connection()
            raise
        return htmlfile.text

    @retry(stop_max_attempt_number=5, wait_random_min=5000,
           wait_random_max=10000)
    def get_html_binary_with_params(self, url, payload):
        hdr = self.set_header()
        try:
            htmlfile = requests.get(url, headers=hdr, params=payload)
            self.base_url = htmlfile.url
            htmlfile.raise_for_status()
        except requests.exceptions.SSLError:
            # check for https
            print "SSLError exception caught"
        except requests.exceptions.ConnectionError:
            print "No Internet Connection!\nWaiting for connection"
            self.wait_for_connection()
            raise
        return htmlfile.content
