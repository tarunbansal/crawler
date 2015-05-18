import urllib.request as urlcon
from urllib.parse import urlparse
from urllib.parse import urlunparse
from bs4 import BeautifulSoup
import sys
import time
import threading
import traceback
from collections import deque

VISITED_URLS = {}
CRAWL_BUFFER = deque([])
CRAWLER_DEFAULT_WORKERS = 10
WORKER_WAIT_INTERVAL = 1 #seconds
MAX_COUNT_LIMIT = None

class WorkerThread(threading.Thread):
    def __init__(self, crawler, name):
        threading.Thread.__init__(self)
        self.__crawler = crawler
        self.name = name
        
    def run(self):
        while not self.__crawler.kill and self.is_alive():
            try:
                if len(CRAWL_BUFFER) > 0:
                    strURL = CRAWL_BUFFER.popleft()
                    urlObj = URL(strURL)
                    print("URL " + str(urlObj.url) + " about to be crawled by Worker : " + str(self.name))
                    self.__crawler.crawl(urlObj)
                else:
                    print("No work for worker :" + str(self.name))
                time.sleep(WORKER_WAIT_INTERVAL)
            except Exception as e:
                print("Unknown exception occured while doing worker task" + str(e))
                traceback.print_exc()
        print("Stopping Worker : " + str(self.name))
        print("List of crawled URL's is : \n " + str(VISITED_URLS))

class URL():
    def __init__(self,strURL):
        self.url = strURL
        self.netloc = None
        self.scheme = None
        self.valid = True
        self.validateURL()
    
    def validateURL(self):
        pURL = urlparse(self.url)
        if pURL.netloc:
            self.netloc = pURL.netloc
        else:
            self.valid = False
        if pURL.scheme:
            self.scheme = pURL.scheme
        else:
            self.valid = False

class WebCrawler():
    kill = False
    count = 0
    listworkers = []
    def __init__(self):
        self.activeWorkers = []
        self.__startWorkers()

    def __startWorkers(self):
        try:
            for workerIndex in range(CRAWLER_DEFAULT_WORKERS):
                strWorkerName = "Worker " + str(workerIndex)
                worker = WorkerThread(self, strWorkerName)
                #worker.daemon = True
                worker.start()
                self.listworkers.append(worker)
        except Exception as e:
            print(" exception occured in crawler " + str(e))
            traceback.print_exc()
            exit()

    def crawl(self,urlObj):
        #BASE_URL = CRAWL_BUFFER.popleft()
        try:
            if ((urlObj.valid) and (urlObj.url not in VISITED_URLS.keys())):
                print("About to open url : " + str(urlObj.url))
                rsp = urlcon.urlopen(urlObj.url,timeout=2)
                hCode = rsp.read()
                soup = BeautifulSoup(hCode)
                #print(soup)
                links = self.scrap(soup)
                self.count += 1
                boolStatus = self.checkmax()
                if boolStatus:
                    VISITED_URLS.setdefault(urlObj.url,"True")
                else:
                    return
                for eachLink in links:
                    if eachLink not in VISITED_URLS:
                        parsedURL = urlparse(eachLink)
                        if parsedURL.scheme and "javascript" in parsedURL.scheme:
                            print("***************Javascript found in scheme " + str(eachLink) + "**************")
                            continue
                        if not parsedURL.scheme and not parsedURL.netloc:
                            print("No scheme and host found for "  + str(eachLink))
                            newURL = urlunparse(parsedURL._replace(**{"scheme":urlObj.scheme,"netloc":urlObj.netloc}))
                            #print("New URL is "  + str(newURL))
                            eachLink = newURL
                        elif not parsedURL.scheme :
                            print("Scheme not found for " + str(eachLink))
                            newURL = urlunparse(parsedURL._replace(**{"scheme":urlObj.scheme}))
                            #print("New URL is "  + str(newURL))
                            eachLink = newURL
                            #print("Scheme and host are found for "  + str(eachLink))
                        print(" Found child link " + eachLink)
                        CRAWL_BUFFER.append(eachLink)
            else:
                print("Invalid URL or URL present in visited " + str(urlObj.url))
        except Exception as e:
            print("Unknown exception occured while fetching HTML code" + str(e))
            traceback.print_exc()

    def scrap(self,soup):
        rec_links = []
        for link in soup.find_all('a'):
            rec_links.append(link.get('href'))
        return rec_links
    
    def checkmax(self):
        boolStatus = True
        if MAX_COUNT_LIMIT and self.count >= MAX_COUNT_LIMIT:
            print(" Maximum count reached. Now exiting and stopping workers :( ")
            self.kill = True
            boolStatus = False
        return boolStatus

if __name__ == '__main__':
    #getHTMLCode(str(sys.argv[1]))
    try:
        if len(sys.argv) == 3:
            MAX_COUNT_LIMIT = int(sys.argv[2])
        CRAWL_BUFFER.append(str(sys.argv[1]))
        webC = WebCrawler()
        while webC.listworkers[0].is_alive():
            webC.listworkers[0].join(1)
    except KeyboardInterrupt:
        print("**************** KBI *******************")
        webC.kill = True
        exit(0)
    except Exception as e:
        print("Unknown exception occured in main" + str(e))
        traceback.print_exc()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    