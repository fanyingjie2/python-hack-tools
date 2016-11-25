#encoding=utf-8
#!/usr/bin/python3

'''
fanyingjie
ÍøÕ¾ÅÀ³æ
'''

import requests
import re
from optparse import OptionParser
import sys


class Reptile(object):
    def __init__(self,url):
        if url.endswith('/') or '?' in url:
            self.url=url 
        else:
            self.url=url+'/'
        self.links=[] 
        self.tag=[] 
        self.start()



    def remove_is_not_link(self,links):  
        result=[]
        tag=['?','' ,'#','/','css','js','ico','img','doc','pdf','htm','html']
        for link in links:
            templink=link.split('.')[-1].lower()
            if "[" in link or '@' in link or  "'" in link  or "#" in link\
                    or 'history' in link.lower()  or "javascript" in link.lower() or templink in tag\
                    or '(' in link.lower() or 'mail' in link.lower():
                pass
            else:
                result.append(link)
        return  result

    def get_all_links(self,url): 
        result=[]
        try:
            f=requests.get(url,timeout=3)
            f.encoding='utf-8'
            text=f.content

            pattern = 'href="(\S+.)'
            links = re.findall(pattern, text)
            links = [link.split('"')[0] for link in links]
            result.extend(links)

            pattern = "href='(\S+.)"
            links = re.findall(pattern, text)
            links = [link.split("'")[0].strip() for link in links]
            result.extend(links)
        except Exception, e:
            print e

        return result

    def judge_links(self,links,url): 
        links=self.remove_is_not_link(links)

        judge_links = []
        length = len(url)
        hp = ""  
        while True:
            if url[length - 1] == '/':
                hp = url[:length]
                break
            length -= 1
        http = url.split("//")[0].split(":")[0]

        for link in links:

            if link.startswith('../'): 

                while True:
                    if link.startswith('../'):

                        if hp.count('/')>3:
                            link=link[3:]
                            temp_hp=hp.split('/')
                            hp=hp[:len(hp)-len(temp_hp[-1])-len(temp_hp[-2])-1]
                        else:
                            link=link[3:]
                    else:

                        break


            if link.startswith('./') and link.startswith('../')==False:
                link=link.replace('./','')

            if link.startswith(http): 
                if link.startswith(self.url):
                    judge_links.append(link)

            else:
                if link.startswith('/'):
                    judge_links.append(self.url + link[1:])
                else:
                    judge_links.append(hp + link)
        return judge_links

    def remove_repeat_link(self,link):
        if '?' in link:
            link1=link.split('&')
            result=""
            for link2 in link1:
                name=link2.split('=')[0]+'='
                result+=name
            if result in self.tag:
                return False
            else:
                self.tag.append(result)

                return True
        else:
            if link in self.tag:
                return False
            else:
                self.tag.append(link)

                return True


    def get_per_links(self,url):
        links=self.get_all_links(url)
        links=self.judge_links(links,url)
        temp_links=[]
        for link in links:
            if self.remove_repeat_link(link):
                print link
                temp_links.append(link)
        return temp_links

    def start(self):
        links = self.get_per_links(self.url)
        self.links.extend(links)

        while True:
            temp_links = []
            for link in links:
                temp_links.extend(self.get_per_links(link))
            if temp_links == []:
                break
            else:
                links = temp_links

    def get_result_links(self):
        self.start()
        return self.links


def main():
    parser = OptionParser()
    parser.add_option("-u", "--url", dest="url",help="please input url [www.example.com/]")
    (options, args) = parser.parse_args()
    if options.url:
        test=Reptile(options.url)
        links=test.get_result_links()
main()
print ('end')
