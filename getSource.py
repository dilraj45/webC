# get_html_file
import requests
from retrying import retry


def set_header():
    hdr = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:12.0)'
           ' Gecko/20100101 Firefox/21.0',
           'Accept':  'text/html,application/xhtml+xml,application/xml;'
           'q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1, utf-8; q=0.7,*; q=0.3',
           'Accept-Encoding': 'gzip, deflate',
           'Accept-Language': 'en-US,en;q=0.8'}
    return hdr


@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000)
def wait_for_connection():
    test = requests.get('http://216.58.197.46', timeout=2)
    test.raise_for_status()
    return
# retry if HTTP error or connection error occurs
# delay between consecutive retries is between 5 to 10 seconds


@retry(stop_max_attempt_number=5, wait_random_min=5000, wait_random_max=10000)
def get_html_text(url):
    hdr = set_header()
    try:
        htmlfile = requests.get(url, headers=hdr)
        htmlfile.raise_for_status()
    except requests.exceptions.SSLError:
        # check for https
        if url[4] == 's':
            url = url[0:4] + url[5:]
            raise
        else:
            htmlfile = requests.get(url, header=hdr, verify=False)
            htmlfile.raise_for_status()
    except requests.exceptions.ConnectionError:
        # checking for bad connection
        print "No Internet Connection!\nWaiting for connection"
        wait_for_connection()
        raise
    return htmlfile.text


@retry(stop_max_attempt_number=5, wait_random_min=5000, wait_random_max=10000)
def get_html_raw_response(url):
    hdr = set_header()
    try:
        htmlfile = requests.get(url, headers=hdr)
        htmlfile.raise_for_status()
    except requests.exceptions.SSLError:
        # check for https
        if url[4] == 's':
            url = url[0:4] + url[5:]
            raise
        else:
            htmlfile = requests.get(url, header=hdr, verify=False)
            htmlfile.raise_for_status()
    except requests.exceptions.ConnectionError:
        print "No Internet Connection!\nWaiting for connection"
        wait_for_connection()
        raise
    return htmlfile.content


@retry(stop_max_attempt_number=5, wait_random_min=5000, wait_random_max=10000)
def get_html_text_with_params(url, payload):
    # this method send requests with parameters in query to particular URL
    # payloads is a dictionary comprising of key value pair
    hdr = set_header()
    try:
        htmlfile = requests.get(url, headers=hdr, params=payload)
        htmlfile.raise_for_status()
    except requests.exceptions.SSLError:
        # check for https
        if url[4] == 's':
            url = url[0:4] + url[5:]
            raise
        else:
            htmlfile = requests.get(url, header=hdr, verify=False)
            htmlfile.raise_for_status()
    except requests.exceptions.ConnectionError:
        print "No Internet Connection!\nWaiting for connection"
        wait_for_connection()
        raise
    return htmlfile.text


@retry(stop_max_attempt_number=5, wait_random_min=5000, wait_random_max=10000)
def get_html_raw_response_with_params(url, payload):
    hdr = set_header()
    try:
        htmlfile = requests.get(url, headers=hdr, params=payload)
        htmlfile.raise_for_status()
    except requests.exceptions.SSLError:
        # check for https
        if url[4] == 's':
            url = url[0:4] + url[5:]
            raise
        else:
            htmlfile = requests.get(url, header=hdr, verify=False)
            htmlfile.raise_for_status()
    except requests.exceptions.ConnectionError:
        print "No Internet Connection!\nWaiting for connection"
        wait_for_connection()
        raise
    return htmlfile.content
