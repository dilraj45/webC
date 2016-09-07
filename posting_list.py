from getSource import get_html_text
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from robobrowser import RoboBrowser
import requests

#html_text=get_html_text(base)
#souphandler=BeautifulSoup(html_text)

def recursiveChildren(x):
    
    #With "childGenerator" in dir(x) we make sure that an element is a container, terminal nodes such as NavigableStrings are not containers and do not contain children.
    if "childGenerator" in dir(x):
      for child in x.childGenerator():
          name = getattr(child, "name", None)
          #print(type(child))
          if name is not None:
              name
             #print ("[Container Node]",child.name,child)
          recursiveChildren(child)
    else:
        try:
            if not x.isspace(): #Just to avoid printing "\n" parsed from document.
                print ("[Terminal Node]",x )
        except Exception as r:  
            print(r)
            
          

if __name__ == "__main__":
      result_file = open('result.txt', 'w')
      browser = RoboBrowser(history=True)
  #root="http://www.imperial.ac.uk/bio-inspired-technology/people/research-assistants-and-phd-students/"
     # base = u"http://web.mit.edu/physics/people/faculty/index.html"
      base=u"http://www.google.com"
      result_file = open('result.txt', 'w')
      try:
          browser.open(base)
      except requests.exceptions.ConnectionError as r:
          r.status_code = "Connection refused"

      html=browser.parsed()
      ## USING MODULEEEEES 
      html_text=get_html_text(base)

      
      htmltext=str(html)##NO NEED HERE 
#print(htmltext)
      souphandler=BeautifulSoup(html_text,"lxml")
  #print(type(souphandler))
     # sp= souphandler.prettify()
     # print(sp)
    #  print(souphandler.find_all())
      souphandler.get_text()
      html_tag=souphandler.find('div')
      tag=html_tag.children
          
      for child in tag:
           try:
              recursiveChildren(child)
           except Exception as r:  
              break
          
            #if child is not None:
                   # print(str(child))
                  
                    