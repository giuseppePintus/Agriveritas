import hashlib
from scrapy import Spider, Request
from scrapy.http import Response
from urllib.parse import urlparse
from attemp3.items import WebDownloadedElement
import os
import time
import datetime

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

    
    lastTimestamp = 0

    def parse(self, response):
        # Common parsing logic
        hash_code = hashlib.sha256(response.body).hexdigest()
        item = self.create_item(response, hash_code)
        timestamp = time.time()
        human_readable_timestamp = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        # self.log(f"FILE N {self.counter} - Time {human_readable_timestamp} [{timestamp} > {timestamp - self.lastTimestamp}]")
        self.log(f"FILE N {self.counter} - Time {human_readable_timestamp} [{timestamp - self.lastTimestamp}] / {response.url}")
        self.lastTimestamp = timestamp

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

        item.tableRow["ID_counter"] = str(self.counter)
        
        self.counter = self.counter + 1
        
        #cod_reg -> ci pensa complete
        item.tableRow["url_from"] = str(response.url)
        item.tableRow["HTTP_status"] = response.status
        item.tableRow["hash_code"] = hash_code
        # item.tableRow.file_downloaded_name = scrapy.Field()
        # item.tableRow.file_downloaded_dir = scrapy.Field()
        item.tableRow["timestamp_download"] = time.time()
        # item.tableRow.timestamp_mod_author = scrapy.Field()
        #embed_risorsa = scrapy.Field()
        # True if "faq" in l else False
        item.tableRow["is_training"] = False if "faq" in str(response.url) else True
        self.log(toLog=f" istrain?? --> {str(response.url)} -> {item.tableRow['is_training']}",aCapo=1 )
        ### qui ### ID_univoco = scrapy.Field()
        ### ragnoFiglio ### cod_reg = scrapy.Field()
        ### qui ### ID_counter = scrapy.Field()
        ### qui ### url_from = scrapy.Field()
        ### qui ### HTTP_status = scrapy.Field()
        ### qui ### hash_code = scrapy.Field()
        
        ### downloadPipe ### file_downloaded_name = scrapy.Field()
        ### downloadPipe ### file_downloaded_dir = scrapy.Field()
        ### qui ### timestamp_download = scrapy.Field()
        ### downloadPipe ###timestamp_mod_author = scrapy.Field()

        ### milvusPipe ###embed_risorsa = scrapy.Field()
        ### qui ### is_training = scrapy.Field()
    

        #item.settingPart
        # aborted = scrapy.Field()
        item.settingPart["abortReason"] = ""
        item.settingPart["allowedContentType"] = [".html", ".pdf", "html", "pdf"] # scrapy.Field()

        self.complete_inizialization(item)
        item.tableRow["ID_univoco"] = f"{item.tableRow['cod_reg']}_{item.tableRow['ID_counter']}"



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

class GeneralWebSpider(BaseSpider):
    name = "general_crawler"
    
    def __init__(self, start_urls=None, allowed_domains=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = start_urls.split(',') if start_urls else []
        self.allowed_domains = allowed_domains.split(',') if allowed_domains else []
        
    def parse(self, response):
        # Create item for current page
        item = self.create_item(response, self.generate_hash(response.url))
        yield item
        
        # Follow links
        for next_page in response.css('a::attr(href)').getall():
            if next_page:
                yield response.follow(next_page, self.parse)
