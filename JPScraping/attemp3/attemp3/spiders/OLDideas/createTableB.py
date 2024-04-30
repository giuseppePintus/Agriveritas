import hashlib
from pathlib import Path
import scrapy
from scrapy.utils.project import get_project_settings
import time
from scrapy.selector import Selector
from urllib.parse import urlparse


class CreateTableB(scrapy.Spider):
    logFile = "myLogSpider.txt"
    pdLogFile = ""
    saveDir = ""

    visited = set()  # Set to keep track of visited URLs

    def log(self, toLog="", aCapo=0):
        print(("\n" * aCapo) + toLog)
        with open(self.logFile, "a") as f:
            f.write(("\n" * aCapo) + toLog + "\n")

    def JPnormalizeUrl(self, url):
        toRet = url
        lastC = str(url)[-1]
        finishUrls = ['/', '//', '\\']
        if lastC in finishUrls:  # and len(url.split("/")[-1].split(".")) == 1:
            toRet = url[:-1]
        return toRet

    def pushUrl(self, url):
        self.visited.add(url)

    def parse(self, response):
        # Compute the hash code of the response body
        hash_code = hashlib.sha256(response.body).hexdigest()

        requiredMainTableInfo = {
            "IDres": hash_code,
            "IDregion": self.region,  # Define region in child class
            "urlFrom": response.url,  # "sito web provenienza": "",
            "HTTPStatus": response.status,
            "fileDownloadedName": "",
            "fileDownloadedDir": "",
            "timestampDownload": time.time(),
            "timestampUpload": "",
            "aborted": False,
            "abortReason": ""
        }

        item = {
            "response": response,
            "tableRow": requiredMainTableInfo,
            "domains": self.allowed_domains
        }

        self.log("NUOVO FILE")
        if str(response.url).endswith(".html"):
            self.log("mmmmmmmmmmm " + str(response.url))

        self.log(str(item))
        self.log(str(response))
        self.log("")

        yield item

        # Extract links and follow them if not visited before
        if response.headers.get('Content-Type', b'').startswith(b'text/html'):
            links = response.css('a::attr(href)').getall()
            for link in links:
                tmpurl = response.urljoin(link)
                absolute_url = self.JPnormalizeUrl(tmpurl)
                parsed_url = urlparse(absolute_url)
                self.log("°°°°°°°°°°°°°°°°")
                self.log(str(link))
                self.log(str(absolute_url))
                self.log(str(parsed_url))
                self.log(str(parsed_url.netloc))
                self.log("°°°°°°°°°°°°°°°°", aCapo=2)
                if parsed_url.netloc == self.allowed_domains[0] and absolute_url not in self.visited:
                    self.pushUrl(absolute_url)
                    yield scrapy.Request(absolute_url, callback=self.parse)