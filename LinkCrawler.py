import urllib.request as urlcon
import sys
import traceback

def validateURL(strURL):
    pass

def handleProxy(dictDetails):
    pass

def handleAuth(dictDetails):
    pass

def getHTMLCode(strURL):
    try:
        validateURL(strURL)
        rsp = urlcon.urlopen(strURL)
        hcode = rsp.read()
        print(hcode)
    except Exception as e:
        print("Unknown exception occured while fetching HTML code" + str(e))
        traceback.print_exc()
        
def scrapLinks(strCode):
    pass

getHTMLCode(str(sys.argv[1]))