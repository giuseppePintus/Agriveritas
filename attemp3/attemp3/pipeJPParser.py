from pathlib import Path
import os
import scrapy
from scrapy.pipelines.files import FilesPipeline
from attemp3.pipeInterface import PipeInterface
import re
from attemp3.items import WebDownloadedElement

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


import re
from html.parser import HTMLParser
class HTMLToTextConverter(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = ""
        self.current_indent = 0
        self.elements_to_parse = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "a"]
        self.inner_text = ""
        self.inner_attrs = []

    def handle_starttag(self, tag, attrs):
        if tag == "br":
            self.text += "\n"
        elif tag in self.elements_to_parse:
            self.parse_element(tag, attrs=attrs)
            self.parse_inner_text(tag, attrs)
            
    def parse_element(self, tag, attrs):
        indent = "  " * self.current_indent
        if tag == "h1":
            self.text += f"{indent}# {self.get_text()}\n\n"
        elif tag in ["h2", "h3", "h4", "h5", "h6"]:
            level = {"h2": 2, "h3": 3, "h4": 4, "h5": 5, "h6": 6}[tag]
            self.text += f"{indent}#" * level + " " + self.get_text() + "\n\n"
        elif tag == "p":
            self.text += f"{indent}{self.get_text()}\n\n"
        elif tag == "a":
            for attr in attrs:
                if attr[0] == "href":
                    self.text += f"[{self.get_inner_text()}]({attr[1]})\n"
                    self.inner_text = ""  # Reset inner_text for the next occurrence
                    break
            else:
                self.text += f"{self.get_text()}\n"

    def parse_inner_text(self, tag, attrs):
        if tag == "a":
            self.inner_text = ""
            self.inner_attrs = attrs
        elif tag == "span":
            if any("class" in a and "innerText" in a for a in self.inner_attrs):
                self.inner_text += self.get_data()  # Get the current data in the parser

    def get_inner_text(self):
        return self.inner_text

    def get_text(self):
        text = super().get_starttag_text()
        return text.strip()

    def handle_endtag(self, tag):
        if tag == "li":
            self.text += "\n"
        elif tag in self.elements_to_parse:
            self.current_indent -= 1

    def handle_data(self, data):
        if data.strip():
            self.text += data.strip() + " "# import os
# import re
# from html.parser import HTMLParser

# class HTMLToTextConverter(HTMLParser):
#     def __init__(self):
#         super().__init__()
#         self.text = ""
#         self.in_pre = False
#         self.in_code = False
#         self.in_heading = False
#         self.heading_level = 0

#     def handle_starttag(self, tag, attrs):
#         if tag == "pre":
#             self.in_pre = True
#         elif tag == "code":
#             self.in_code = True
#         elif tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
#             self.in_heading = True
#             self.heading_level = int(tag[1])

#     def handle_endtag(self, tag):
#         if tag == "pre":
#             self.in_pre = False
#         elif tag == "code":
#             self.in_code = False
#         elif tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
#             self.in_heading = False

#     def handle_data(self, data):
#         if self.in_pre or self.in_code:
#             self.text += data
#         else:
#             self.text += re.sub(r"\s+", " ", data).strip()
#             if self.in_heading:
#                 self.text += "\n" + "#" * self.heading_level + " "

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

    
