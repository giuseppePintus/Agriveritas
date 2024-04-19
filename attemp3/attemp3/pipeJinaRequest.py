from pathlib import Path
import os
import scrapy
from scrapy.pipelines.files import FilesPipeline
from attemp3.pipeInterface import PipeInterface
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


class JinaRequest(PipeInterface):

    logFile = "myLogJineRequest"
    pdLogFile = ""

    # def log(self, toLog="", aCapo=0):
    #     print(toLog)
    #     self.pdLogFile.write(("\n" * aCapo) + toLog+"\n")

    # def open_spider(self, spider):
    #     super().open_spider(spider)
    #     self.logFile += spider.code_region + ".txt"
    #     self.pdLogFile = open(self.logFile, "w")
    #     # super().open_spider(spider)
    #     # self.pdLogFile = open(self.logFile, "w")
    #     # # self.target_directory = spider.settings.get('FILES_STORE')

    # def close_spider(self, spider):
    #     #super().close_spider(spider)
    #     self.pdLogFile.close()  


    def process_item(self, item : WebDownloadedElement, spider):
        # item.tableRow.
        # item.tableRow.
        # item.tableRow.
        self.log(item.tableRow["url_from"])
        self.log(item.tableRow["file_downloaded_name"])
        self.log(item.tableRow["file_downloaded_dir"])
        self.makeReq(item.tableRow["url_from"])
        self.log(aCapo=3)
        
        # resp = item['response']
        # tabR = item["tableRow"]

        return item
    
    def makeReq(self, url):
        basicUrl = "https://r.jina.ai/" + url
        self.log(basicUrl, aCapo=1)

        # conn = http.client.HTTPSConnection("api.example.com")
        # headers = {"Authorization": "Bearer YOUR_TOKEN"}

        # conn.request("GET", "/data", headers=headers)
        # response = conn.getresponse()

        # if response.status == 200:
        #     data = json.loads(response.read().decode("utf-8"))
        #     print(data)
        # else:
        #     print(f"Request failed with status code {response.status}")
