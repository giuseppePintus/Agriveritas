import hashlib
from scrapy import Spider, Request
from scrapy.http import Response
from urllib.parse import urlparse
from attemp3.items import WebDownloadedElement
import os
import time

class BaseSpider(Spider):
    # Common attributes can be defined here if they are shared across spiders
    logFile = "myLogSpider"

    start_urls = []
    
    allowed_domains = []

    code_region = ""
    
    
    def start_requests(self):
        self.logFile += self.code_region + ".txt"

        if os.path.isfile(self.logFile):
            os.remove(self.logFile)
        for url in self.start_urls:
            yield Request(url, self.parse)
    
    def log(self, toLog="", aCapo=0):
        print(("\n" * aCapo) + toLog)
        with open(self.logFile, "a") as f:
            f.write(("\n" * aCapo) + toLog + "\n")
    
    def JPnormalizeUrl(self, url):
        lastC = str(url)[-1]
        finishUrls = ['/', '//', '\\']
        if lastC in finishUrls:
            return url[:-1]
        return url
    
    counter = 0

    def parse(self, response):
        # Common parsing logic
        hash_code = hashlib.sha256(response.body).hexdigest()
        item = self.create_item(response, hash_code)
        
        self.log("START PROCESSING NEW FILE ${self.counter}")

        yield item
        if response.headers.get('Content-Type', b'').startswith(b'text/html'):
            yield from self.follow_links(response)
    
    def follow_links(self, response):
        links = response.css('a::attr(href)').getall()
        for link in links:
            absolute_url = self.JPnormalizeUrl(response.urljoin(link))
            parsed_url = urlparse(absolute_url)
            if parsed_url.netloc in self.allowed_domains:
                yield Request(absolute_url, callback=self.parse)



    def create_item(self, response : Response, hash_code):
        item = WebDownloadedElement()

        item["response"] = response

        item.tableRow["IDuni"] = self.counter
        self.counter = self.counter + 1
        
        #cod_reg -> ci pensa complete
        item.tableRow["url_from"] = str(response.url)
        item.tableRow["HTTPStatus"] = response.status
        item.tableRow["hash_code"] = hash_code
        # item.tableRow.file_downloaded_name = scrapy.Field()
        # item.tableRow.file_downloaded_dir = scrapy.Field()
        item.tableRow["timestamp_download"] = time.time()
        # item.tableRow.timestamp_mod_author = scrapy.Field()

        #item.settingPart
        # aborted = scrapy.Field()
        item.settingPart["abortReason"] = ""
        item.settingPart["allowedContentType"] = [] #["html", "pdf"] # scrapy.Field()

        self.complete_inizialization(item)
        return item
        # return {
        #     "IDres": hash_code,
        #     "IDregion": "ER",
        #     "urlFrom": response.url,
        #     # Add other fields as necessary
        # }
        # # This method should be implemented by the subclass if they need specific item creation
        # raise NotImplementedError("You must implement the method create_item()")

    def complete_inizialization(self, item):
        # This method should be implemented by the subclass if they need specific item creation
        raise NotImplementedError("This is mother spider, you have to summon a child before use it!")
