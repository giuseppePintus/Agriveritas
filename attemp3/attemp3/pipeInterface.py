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
        print(toLog)
        self.pdLogFile.write(("\n" * aCapo) + toLog+"\n")

    def open_spider(self, spider):
        super().open_spider(spider)
        self.logFile += spider.code_region + ".txt"
        self.pdLogFile = open(self.logFile, "w")
        
    def close_spider(self, spider):
        self.pdLogFile.close()  
