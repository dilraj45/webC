from getSource import get_html_text
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from robobrowser import RoboBrowser
import requests

#html_text=get_html_text(base)
#souphandler=BeautifulSoup(html_text)2
def children_find(tag):     
      tag=tag.children    
      for child in tag:
           try:
              #print(child) 
              recursiveChildren(child)
           except Exception as r:  
               print(r)
               break
          
def recursiveChildren(x):
    
    #With "childGenerator" in dir(x) we make sure that an element is a container, terminal nodes such as NavigableStrings are not containers and do not contain children.
    if "childGenerator" in dir(x):
      for child in x.childGenerator():
          name = getattr(child, "name", None)
          #print(type(child))
          if name is not None:
              name
             #print ("[Container Node]",child.name,child)
          recursiveChildren(child.parent)
    else:
        try:
            if not x.isspace(): #Just to avoid printing "\n" parsed from document.
                print ("[Terminal Node]",x )
        except Exception as r:  
            print(r)
            
          

if __name__ == "__main__":
      
      result_file = open('result.txt', 'w')
  #root="http://www.imperial.ac.uk/bio-inspired-technology/people/research-assistants-and-phd-students/"
     # base = u"http://web.mit.edu/physics/people/faculty/index.html"
      base=u"https://www.stanford.edu/"
     # base="<span class='subtitle'>: HTML Tutorials</span>"
      result_file = open('result.txt', 'w')
      ## USING MODULEEEEES 
      html_text=get_html_text(base)
      
#print(htmltext)7
      souphandler=BeautifulSoup(html_text,"lxml")
      try:
          for h1_tag in souphandler.find_all('h1'):
              print("asd")
              print(h1_tag.get_text())
      except Exception as q:
          print(q)
      try:
          h2_tag=souphandler.find_all('h2').get_text()
          print(h2_tag)
      except Exception as q:
          print(q)
      try:
          h3_tag=souphandler.find_all('h3').get_text()
          print(h3_tag)
      except Exception as q:
          q
      try:
          for title_tag in souphandler.find_all('title'):
              print("asd")
              print(title_tag.get_text())
          
      except Exception as q:
          q    
      try:
          table_tag=souphandler.findall('table').get_text()
          print(table_tag)
      except Exception as q:
          q
      try:
           meta_tag=souphandler.find('meta').get_text()
           print(meta_tag)
      except Exception as q:
          q
      try:
          title_tag=souphandler.find('li').get_text()
          print(title_tag)
      except Exception as q:
          q        
      
          
      
     
     

                  
                    