from pathlib import Path
import os
import scrapy
from scrapy.pipelines.files import FilesPipeline
import re
from attemp3.items import WebDownloadedElement

import http.client
import json


# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class PipeInterface(FilesPipeline):

    logFile = "HAVETOUPLOADIT"
    pdLogFile = ""

    def log(self, toLog="", aCapo=0):
        #print(toLog)
        self.pdLogFile.write(("\n" * aCapo) + toLog+"\n")

    def open_spider(self, spider):
        super().open_spider(spider)
        self.logFile += spider.code_region + ".txt"
        self.pdLogFile = open(self.logFile, "w")
        
    def close_spider(self, spider):
        self.pdLogFile.close()  

    
    def process_item(self, item : WebDownloadedElement, spider):

        sett = ite
        
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
        # desideredContentType = [None, "html", "pdf"]

        # if contentType is None:
        #     contentType = "html"

        fPath = self.myFilePath(urlCleaned, tabR["cod_reg"], doms)
        fName = self.myFileName(urlCleaned, contentType)
        fPN = self.getFullNamePath(urlCleaned, contentType, tabR["cod_reg"], doms)

        self.log("######### " + fPN)
        if not os.path.exists(fPath):
            os.makedirs(fPath)
        
        # if any(desired_type in contentType for desired_type in desideredContentType):
        #     if re
        Path(fPN).write_bytes(resp.body)
        tabR["file_downloaded_name"] = fName
        tabR["file_downloaded_dir"] = fPath
        
        
        # # else:
        # #     # do something else
        # #     tabR["aborted"] = True
        # #     tabR["abortReason"] = "Content tipe is not somethig like" + str(desideredContentType[1:])

        # item["tableRow"] = tabR
        # self.log("Analizzando i risultati")
        # for key in item:
        #     self.log("key: %s , value: %s" % (key, item[key]))

        self.log(aCapo=7)
        return item

