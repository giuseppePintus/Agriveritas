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



import re
from bs4 import BeautifulSoup


# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class JPParser2(PipeInterface):

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
            fNameNew = fNameOLD[:-5] + "2JP" + ".txt"

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
                
        # Test the function
        with open(txt_file, 'w') as f:
            f.write(self.html_to_txt(html_file))



    def html_to_txt(self, html_file):
        with open(html_file, 'r') as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove script and style tags
        for script in soup.find_all('script'):
            script.decompose()
        for style in soup.find_all('style'):
            style.decompose()

        # Remove navigation and social links
        nav = soup.find('div', {'id': 'navigation'})
        if nav:
            nav.decompose()
        social = soup.find('div', {'id': 'social'})
        if social:
            social.decompose()

        # Extract main content
        text = ''
        for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'ul', 'div']):
            if element.name == 'p':
                text += element.get_text() + '\n\n'
            elif element.name == 'h1':
                text += element.get_text() + '\n\n'
            elif element.name == 'h2':
                text += element.get_text() + '\n\n'
            elif element.name == 'h3':
                text += element.get_text() + '\n\n'
            elif element.name == 'ul':
                for li in element.find_all('li'):
                    text += li.get_text() + '\n'
            elif element.name == 'div' and element.has_attr('class') and 'erogati' in element['class']:
                text += element.get_text() + '\n\n'

        # Remove extra newlines and whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'\s{2,}', ' ', text)

        return text

