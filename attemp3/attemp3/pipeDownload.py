from pathlib import Path
import os
import scrapy
from scrapy.pipelines.files import FilesPipeline
from attemp3.pipeInterface import PipeInterface
import re
from attemp3.spiders.motherSpider import BaseSpider
from attemp3.items import WebDownloadedElement

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

class PipeDownload(PipeInterface):

    logFile = "myLogDownloadPipeline"
    pdLogFile = ""

    # abortContentTypeRule = [b"text/html", b"application/pdf"]

    mapperLongString = {}

    # def log(self, toLog="", aCapo=0):
    #     print(toLog)
    #     self.pdLogFile.write(("\n" * aCapo) + toLog+"\n")

    def open_spider(self, spider : BaseSpider):
        super().open_spider(spider)
    #     self.logFile += spider.code_region + ".txt"
    #     self.pdLogFile = open(self.logFile, "w")
        self.target_directory = spider.settings.get('FILES_STORE')

    # def close_spider(self, spider):
    #     super().close_spider(spider)
    #     self.pdLogFile.close()  


    
    

    def process_item(self, item : WebDownloadedElement, spider):
        self.log("")
        self.log(" ### INIZIO NUOVO FILE ### ")
        self.log("Analizzando la risorsa")
        for key in item:
            self.log("key: %s , value: %s" % (key, item[key]))

        self.log("")
        # self.log(" --- Analizzando i campi PRE-DOWNLOAD --- ")
        # for key1 in item:
        #     self.log(" -> Analizzando " + key1)
        #     for key in key1:
        #         self.log(" ---> key: %s , value: %s" % (str(key), str(key1[str(key)])))

        resp = item['response']
        doms = item["domains"]
        tabR = item.tableRow
        settings = item.settingPart

        settings["abortReason"]

        self.log(aCapo=2)
        self.log(" --- Analizzando l'header di risposta --- ")
        for x in resp.headers:
            self.log("-> " + str(x) + " _ " + str(resp.headers.get(x)))

        #Retrieve the Last-Modified header
        self.log()
        self.log(" --- prendendo il timestampUpload --- ")
        last_modified = resp.headers.get('Last-Modified')
        self.log(" " + str(last_modified))
        tabR["timestamp_mod_author"] = "" #defaul value
        if last_modified:
            self.log("Eccolo! -> " + str(last_modified.decode()))
            tabR["timestamp_mod_author"] = last_modified.decode()

        #download page
        urlCleaned = resp.url.split("//")[1]
        contentType = str(resp.headers.get('Content-Type'))

        fPath = self.myFilePath(urlCleaned, tabR["cod_reg"], doms)
        fName = self.myFileName(urlCleaned, contentType)
        fPN = self.getFullNamePath(urlCleaned, contentType, tabR["cod_reg"], doms)

        allowedContentType = settings["allowedContentType"]
        if len(allowedContentType) != 0:
            extension = fName[-6:]
            if not any(aCT in extension for aCT in allowedContentType):
                return self.skipElementForContentType(item)

        # desideredContentType = [None, ]

        # if contentType is None:
        #     contentType = "html"


        self.log("######### " + fPN)
        if not os.path.exists(fPath):
            os.makedirs(fPath)
        
        # if any(desired_type in contentType for desired_type in desideredContentType):
        #     if re
        Path(fPN).write_bytes(resp.body)
        tabR["file_downloaded_name"] = fName
        tabR["file_downloaded_dir"] = fPath
        
        self.log(aCapo=7)
        return item
    
    def skipElementForContentType(self, item : WebDownloadedElement):
        item.settingPart["aborted"] = True
        item.settingPart["abortReason"] = "This element is not a type into " + item.settingPart["allowedContentType"]
        return item
    
    def behaviour_skipped(self, item : WebDownloadedElement, spider):
        self.log("Skipped element")


    def myFileName(self, url, contentType):
        fileName = url.split("/")[-1]
        # Replace invalid characters with "_"
        invalid_chars = r'[<>:"/\\|?*\x00-\x1F\x7F]'
        fileName = re.sub(invalid_chars, "_", fileName)

        if fileName == "":
            fileName = "index.html" # DA CONTROLLARE !!! 
        
        if "html" in contentType and not "html" in fileName:
            fileName += "." + "html"
        
        tollerance = 40
        if len(fileName) > tollerance:
            fileName = fileName[:tollerance] + "." + fileName.split(".")[-1]

        return fileName 
    
    def myFilePath(self, url, idR, toPreserve=[]):
        tmp = os.path.join(self.target_directory,idR)
        upperbound = 10
        for x in url.split("/"):
            if not x in toPreserve and len(x) > upperbound:
                if x in self.mapperLongString.keys():
                    x = self.mapperLongString[x]
                else:
                    hv = hash(x)
                    toMod = -1 * hv if hv < 0 else hv
                    mod = (str(toMod)*5)[:upperbound]
                    self.log("WOW, ha oltrepassato il limite!" + x + " -> " + mod)
                    self.mapperLongString[x] = mod
                    x = mod
                    
            tmp = os.path.join(tmp,x)
        
        self.log("%%%%%%%%%%%%%%%%%%%%%%%")
        self.log(str(url) + "  " + tmp)
        self.log("%%%%%%%%%%%%%%%%%%%%%%%")

        return tmp
    
    def getFullNamePath(self, url, contentType, idR, toPreserve=[]):
        return os.path.join(self.myFilePath(url,idR,toPreserve=toPreserve), self.myFileName(url, contentType))
