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

import os
import re
from html.parser import HTMLParser


# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class JPParser(PipeInterface):

    logFile = "myLogJPParserRequest"
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

            fDir = item.tableRow["file_downloaded_dir"] 
            fNameOLD = item.tableRow["file_downloaded_name"]
            fNameNew = fNameOLD[:-5] + "JP" + ".txt"

            fPathOld = os.path.join(fDir, fNameOLD)
            fPathNew = os.path.join(fDir, fNameNew)

            self.compute_parsing(fPathOld, fPathNew)

        else:
            self.log("NON posso converite altri file!")
        self.log(aCapo=3)

        return item

    def behaviour_skipped(self, item : WebDownloadedElement, spider):
        self.log("So no used myParser")



    def compute_parsing(self, fromFile, toFile):
        # Example usage
        self.convert_html_to_text(fromFile, toFile)


    def convert_html_to_text(self, html_file, txt_file):
        with open(html_file, "r", encoding="utf-8") as f:
            html_content = f.read()

        converter = HTMLToTextConverter()
        converter.feed(html_content)
        text_content = converter.text

        with open(txt_file, "w", encoding="utf-8") as f:
            f.write(text_content)




import os
import re
from html.parser import HTMLParser

class HTMLToTextConverter(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = ""
        self.in_pre = False
        self.in_code = False
        self.in_heading = False
        self.heading_level = 0

    def handle_starttag(self, tag, attrs):
        if tag == "pre":
            self.in_pre = True
        elif tag == "code":
            self.in_code = True
        elif tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            self.in_heading = True
            self.heading_level = int(tag[1])

    def handle_endtag(self, tag):
        if tag == "pre":
            self.in_pre = False
        elif tag == "code":
            self.in_code = False
        elif tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            self.in_heading = False

    def handle_data(self, data):
        if self.in_pre or self.in_code:
            self.text += data
        else:
            self.text += re.sub(r"\s+", " ", data).strip()
            if self.in_heading:
                self.text += "\n" + "#" * self.heading_level + " "

    def handle_entityref(self, name):
        if name == "nbsp":
            self.text += " "
        else:
            self.text += f"&{name};"

    def handle_charref(self, name):
        if name.startswith("x"):
            self.text += chr(int(name[1:], 16))
        else:
            self.text += chr(int(name))

    
