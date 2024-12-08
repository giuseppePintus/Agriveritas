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
    






#DA PROVARE
# import re
# from html.parser import HTMLParser

# class HTMLToTextConverter(HTMLParser):
#     def __init__(self):
#         super().__init__()
#         self.text = ""
#         self.current_element = None
#         self.current_level = 0
#         self.elements_to_parse = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "a"]
#         self.links = {}
#         self.current_link = None

#     def handle_starttag(self, tag, attrs):
#         self.current_level = len(attrs)
#         self.current_element = tag

#     def handle_endtag(self, tag):
#         if tag in self.elements_to_parse:
#             self.current_level -= len(self.parse_attrs(tag))

#     def handle_data(self, data):
#         if self.current_level == 0 or self.current_element not in self.elements_to_parse:
#             return

#         if self.current_element == "a":
#             href = self.get_attr("href", self.parse_attrs(self.current_element))
#             self.links[self.get_text()] = href
#         else:
#             self.text += data.strip() + "\n"

#     def handle_entityref(self, name):
#         if name == "nbsp":
#             self.text += " "
#         else:
#             self.text += f"&{name};"

#     def handle_charref(self, name):
#         if name.startswith("x"):
#             self.text += chr(int(name[1:], 16))
#         else:
#             self.text += chr(int(name))

#     def parse_attrs(self, tag):
#         attrs = {}
#         for attr in self.parse_entities(self.get_starttag_text()):
#             key, value = attr.split("=")
#             attrs[key] = value
#         return attrs

#     def parse_entities(self, data):
#         return re.split(r'([^=]+)=([^>]+)', data)

#     def get_text(self):
#         text = super().get_starttag_text()
#         return text.strip()

#     def get_link(self):
#         return self.current_link

# if __name__ == "__main__":
#     converter = HTMLToTextConverter()
#     html = """
#     <!-- Your provided HTML content here -->
#     """
#     converter.feed(html)
#     print(converter.text)