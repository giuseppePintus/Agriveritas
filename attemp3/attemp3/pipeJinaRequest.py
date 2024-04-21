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

    def process_item(self, item : WebDownloadedElement, spider):
        super().process_item(item=item, spider=spider)

        self.log(item.tableRow["url_from"], aCapo=5)
        self.log(item.tableRow["file_downloaded_name"])
        self.log(item.tableRow["file_downloaded_dir"])
        a : str
        a = item.tableRow["file_downloaded_name"] 
        self.log(a)
        if a.endswith("html"):
            cleanedText = self.makeReq(item.tableRow["url_from"])
            
            if cleanedText != "":
                fDir = item.tableRow["file_downloaded_dir"] 
                fName = item.tableRow["file_downloaded_name"][:-4] + "txt"
                filePath = os.path.join(fDir, fName)
                with open(filePath, "w", encoding="utf-8") as f:
                    f.write(cleanedText)

        else:
            self.log("NON posso usare Jina!")
        self.log(aCapo=3)

        return item

    def behaviour_skipped(self, item : WebDownloadedElement, spider):
        self.log("So no used Jina")
    
    def makeReq(self, url):
        basicUrl = "r.jina.ai"
        apiUrl = f"https://{basicUrl}/{url}"
        response = requests.get(apiUrl)
        res = ""

        # The status code will be 200 if the request was successful
        if response.status_code == 200:
            self.log(response.text)
            res = response.text
        else:
            self.log(f"Request failed with status code {response.status_code}")

        return res