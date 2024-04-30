from pathlib import Path
import os
import scrapy
from scrapy.pipelines.files import FilesPipeline
from attemp3.pipeInterface import PipeInterface
import re
from attemp3.items import WebDownloadedElement

import http.client
import json

import requests

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
        self.log(item.tableRow["url_from"], aCapo=5)
        self.log(item.tableRow["file_downloaded_name"])
        self.log(item.tableRow["file_downloaded_dir"])
        a : str
        a = item.tableRow["file_downloaded_name"] 
        self.log(a)
        if a.endswith("html"):
            self.makeReq(item.tableRow["url_from"])
        else:
            self.log("NON posso usare Jina!")
        self.log(aCapo=3)
        
        # resp = item['response']
        # tabR = item["tableRow"]

        return item
    
    def makeReq(self, url):
        basicUrl = "r.jina.ai"
        apiUrl = f"https://{basicUrl}/{url}"
        response = requests.get(apiUrl)

        # The status code will be 200 if the request was successful
        if response.status_code == 200:
            self.log(response.text)
        else:
            self.log(f"Request failed with status code {response.status_code}")

    
    def makeReqOLD(self, url):
        basicUrl = "r.jina.ai"
        apiUrl = f"https://{basicUrl}/{url}"
        self.log(apiUrl)

        conn = http.client.HTTPSConnection(basicUrl)
        # headers = {"Authorization": "Bearer YOUR_TOKEN"}
        headers = {"Accept": "text/event-stream"}

        conn.request("GET", f"/{url}", headers=headers)
        response = conn.getresponse()

        

        if response.status == 200:
            json_content = json.dumps(response.read().decode("unicode_escape"))
            b = json.loads(json_content)
            self.log(str(b))
            # a = "{" + response.read().decode("unicode_escape") + "}"
            # b = json.loads(a)
            # self.log(b)
            # # self.log(response.read().decode("utf-8"))
            # #self.log(#.decode("unicode_escape"))
            # # response.read().d
            # # data = json.loads()
            
            # # content = data["content"]
            # # self.log(content)
            # # data = json.loads(response.read().decode("utf-8"))
            # # data = response.read()
            # # self.log(data)
        else:
            self.log(f"Request failed with status code {response.status}")

        # basicUrl = "https://r.jina.ai/" + url
        # self.log(basicUrl)

        # conn = http.client.HTTPSConnection(basicUrl)
        # headers = {"Authorization": "Bearer YOUR_TOKEN"}

        # conn.request("GET")
        # response = conn.getresponse()

        if response.status == 200:
            data = json.loads(response.read().decode("utf-8"))
            self.log(data)
        else:
            self.log(f"Request failed with status code {response.status}")
