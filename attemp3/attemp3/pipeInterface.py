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

    verbose = False

    def log(self, toLog="", aCapo=0):
        if self.verbose:
            print(toLog)
        self.pdLogFile.write(("\n" * aCapo) + toLog+"\n")

    def open_spider(self, spider):
        super().open_spider(spider)
        self.logFile += spider.code_region + ".txt"
        self.pdLogFile = open(self.logFile, "w")
        
    def close_spider(self, spider):
        self.pdLogFile.close()  

    
    def process_item(self, item : WebDownloadedElement, spider):

        sett = item.settingPart
        if (sett["aborted"]):
            self.log(aCapo=2)
            self.log("SKIPPED ITEM: reason -> " + sett["abortReason"])
            self.log(aCapo=2)
            self.behaviour_skipped(item, spider)
            return item
        
    def behaviour_skipped(self, item : WebDownloadedElement, spider):
        raise NotImplementedError("This is pipeline interface, you have to implement a specific pipeline!")
