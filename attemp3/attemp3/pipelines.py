from pathlib import Path
import os
import scrapy
from scrapy.pipelines.files import FilesPipeline
import re
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class Attemp3Pipeline(FilesPipeline):

    logFile = "myLog.txt"
    pdLogFile = ""
    saveDir = ""

    def log(self, toLog="", aCapo=0):
        print(toLog)
        self.pdLogFile.write(("\n" * aCapo) + toLog+"\n")

    def open_spider(self, spider):
        super().open_spider(spider)
        self.pdLogFile = open(self.logFile, "w")
        self.target_directory = spider.settings.get('FILES_STORE')



    def close_spider(self, spider):
        #super().close_spider(spider)
        self.pdLogFile.close()  


    def process_item(self, item, spider):
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
        tabR = item["tableRow"]

        self.log(aCapo=3)
        self.log(" --- Analizzando l'header di risposta --- ")
        for x in resp.headers:
            self.log("-> " + str(x) + " _ " + str(resp.headers.get(x)))

        #Retrieve the Last-Modified header
        self.log()
        self.log(" --- prendendo il timestampUpload --- ")
        last_modified = resp.headers.get('Last-Modified')
        self.log(" " + str(last_modified))
        if last_modified:
            self.log("Eccolo! -> " + str(last_modified.decode()))
            tabR["timestampUpload"] = last_modified.decode()

        #self.log(self.file_path(item[""]))

        #Path(self.file_path(resp.request, resp)).write_bytes(resp.body)
        urlCleaned = resp.url.split("//")[1]
        contentType = str(resp.headers.get('Content-Type'))
        if contentType is None:
            contentType = "html"

        self.log("######### " + self.getFullNamePath(urlCleaned, contentType))

        if not os.path.exists(self.myFilePath(urlCleaned)):
            os.makedirs(self.myFilePath(urlCleaned))
       
        Path(self.getFullNamePath(urlCleaned, contentType)).write_bytes(resp.body)
        tabR["nomeFileScaricato"] = self.myFileName(urlCleaned, contentType)
        tabR["dirFileScaricato"] = self.myFilePath(urlCleaned)

        item["tableRow"] = tabR

        # self.log(" --- Analizzando i campi POST-DOWNLOAD --- ")
        # for key1 in item:
        #     self.log(" -> Analizzando " + key1)
        #     for key in key1:
        #         self.log(" ---> key: %s , value: %s" % (key, item[key]))
        self.log("Analizzando i risultati")
        for key in item:
            self.log("key: %s , value: %s" % (key, item[key]))

        self.log(aCapo=7)
        return item


    '''
    def process_itemOLD1(self, item, spider):
        self.log("CIAO")
        self.log(str(item))
        self.log(self.target_directory)
        self.log(str(type(item['response'])) + str(item['response']))
        
        self.log("Analizzando la risorsa")
        resp = item['response']
        self.log(resp.url)
        self.log(self.file_path(resp.request, resp))
        self.log(str(resp.headers))
        self.log("")
        self.log("Analizzando l'hash-code")
        id = item["IDres"]
        self.log(str(type(id)) + " - " + str(id))
        self.log()
        self.log()
        self.log()

        for x in resp.headers:
            self.log("-> " + str(x) + " _ " + str(resp.headers.get(x)))

        #Retrieve the Last-Modified header
        last_modified = resp.headers.get('Last-Modified')
        self.log("çççççççççç " + str(last_modified))
        if last_modified:
            self.log("çççççççççç " + str(last_modified.decode()))
            item['last_modified'] = last_modified.decode()
    
        for key in item:
            self.log("key: %s , value: %s" % (key, item[key]))
        #self.log(self.file_path(item[""]))

        #Path(self.file_path(resp.request, resp)).write_bytes(resp.body)
        urlCleaned = resp.url.split("//")[1]
        contentType = str(resp.headers.get('Content-Type'))
        if contentType is None:
            contentType = "html"

        self.log("######### " + self.getFullNamePath(urlCleaned, contentType))

        if not os.path.exists(self.myFilePath(urlCleaned)):
            os.makedirs(self.myFilePath(urlCleaned))
       
        Path(self.getFullNamePath(urlCleaned, contentType)).write_bytes(resp.body)

        self.log("  #########" * 10)

        return item
    '''
    
    def myFileName(self, url, contentType):
        fileName = url.split("/")[-1]
        # Replace invalid characters with "_"
        invalid_chars = r'[<>:"/\\|?*\x00-\x1F\x7F]'
        fileName = re.sub(invalid_chars, "_", fileName)
        if fileName == "":
            fileName = "index" # DA CONTROLLARE !!! 
        typeOfFile = "html"
        if "pdf" in contentType:
            typeOfFile = "pdf"
        
        if (not ".pdf" in fileName) and (not ".html" in fileName):
            fileName += "." + typeOfFile
        return  fileName 
    
    def myFilePath(self, url):
        tmp = self.target_directory
        for x in url.split("/")[:-1]:
            tmp = os.path.join(tmp,x)
        return tmp
    
    def getFullNamePath(self, url, contentType):
        return os.path.join(self.myFilePath(url), self.myFileName(url, contentType))

    
    
    
    # def file_path(self, request, response=None, info=None, *, item=None):
    #     # Get the original filename
    #     #filename = super().file_path(request, response=response, info=info, item=item)
        
    #     filename = response.url.split("/")[-1] + '.html'

    #     self.log("file_path")

    #     return os.path.join(self.target_directory, filename)

    # def item_completed(self, results, item, info):
    #     # Get the file paths from the results
    #     file_paths = [x['path'] for ok, x in results if ok]
    #     self.log("item_completed") 
    #     # Update the item with the file paths
    #     item['file_paths'] = file_paths

    #     self.log("CCCCCCCCCCCCCCCCCCCCCCCCCCCCCC")
    #     self.log(item)

    #     # Perform any other necessary manipulations

    #     return item
