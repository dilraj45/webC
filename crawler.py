from getSource import get_html_text
import re,bs4
from urlparse import urlparse
from urlparse import urljoin
from sets import Set

visited = Set()
queue = list()
base = u"http://web.mit.edu"
regex = r'^https?://([^.]*\.)?[^.]*\.mit\.edu[^.]*'
pattern = re.compile(regex,re.UNICODE)  


def add_links_to_queue(url):
	try:
		sp = bs4.BeautifulSoup(get_html_text(url),'lxml')
		for tag in sp.find_all('a',href=True):
			link = urljoin(base,tag['href'])
			if(re.match(pattern,link) != None):
				if link not in visited:
					queue.append(link)
					visited.add(link)

	except Exception as e:
		print str(e)+'\n'				

def bfs(level):
	length = len(queue)
	print "Length of queue: "+str(length)+" at level"+str(level)
	if length < 0 or level <= 0:
		return
	for i in range(0,length):
		queue[0]
		add_links_to_queue(queue[0])
		queue.pop(0)
	bfs(level-1)	


def bfs_level(root,level):
	queue.append(base)
	visited.add(base)
	bfs(level)


bfs_level(base,4)