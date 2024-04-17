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


class JinaRequest(FilesPipeline):

    logFile = "myLogJineRequest.txt"
    pdLogFile = ""
    saveDir = ""

    def log(self, toLog="", aCapo=0):
        print(toLog)
        self.pdLogFile.write(("\n" * aCapo) + toLog+"\n")

    def open_spider(self, spider):
        super().open_spider(spider)
        self.pdLogFile = open(self.logFile, "w")
        # self.target_directory = spider.settings.get('FILES_STORE')

    def close_spider(self, spider):
        #super().close_spider(spider)
        self.pdLogFile.close()  


    def process_item(self, item, spider):
        # self.log(" ### INIZIO NUOVO FILE ### ")
        # self.log("Analizzando la risorsa")
        # for key in item:
        #     self.log("key: %s , value: %s" % (key, item[key]))
        # self.log("")

        self.log(item["tableRow"]["urlFrom"])
        self.log(item["tableRow"]["fileDownloadedName"])
        self.log(item["tableRow"]["fileDownloadedDir"])
        self.log(aCapo=3)
        
        # resp = item['response']
        # tabR = item["tableRow"]

        return item
