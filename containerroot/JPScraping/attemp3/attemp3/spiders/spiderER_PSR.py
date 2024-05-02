from attemp3.spiders.motherSpider import BaseSpider
from attemp3.items import WebDownloadedElement

import hashlib
from scrapy import Spider, Request
from scrapy.http import Response
from urllib.parse import urlparse
from attemp3.items import WebDownloadedElement
import os
import time
import datetime

class SpiderER_PSR(BaseSpider):
    name = 'spiER_PSR'
    
    start_urls = ["https://agrea.regione.emilia-romagna.it/", "https://agricoltura.regione.emilia-romagna.it/"]
    
    allowed_domains = [
        'agrea.regione.emilia-romagna.it',
        "agricoltura.regione.emilia-romagna.it"
    ]

    code_region = "ER_PSR"
    
    def complete_inizialization(self, item: WebDownloadedElement):
        item["domains"] = self.allowed_domains
        item.tableRow["cod_reg"] = self.code_region
        # item.tableRow.cod_reg = "ER"

        # # This method should be implemented by the subclass if they need specific item creation
        # raise NotImplementedError("You must implement the method create_item()")

    contains_keyword = ["PSR", "Piano di Sviluppo Rurale", "Sviluppo Rurale"]

    mycounter = 0

    def parse(self, response):
        # Common parsing logic
        hash_code = hashlib.sha256(response.body).hexdigest()



        b = str(response.body)

        timestamp = time.time()
        human_readable_timestamp = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        # self.log(f"FILE N {self.counter} - Time {human_readable_timestamp} [{timestamp} > {timestamp - self.lastTimestamp}]")
        self.log(f"FILE N {self.counter} - Time {human_readable_timestamp} [{timestamp - self.lastTimestamp}] / {response.url}")
        self.lastTimestamp = timestamp
        
        if any(key in b for key in self.contains_keyword): # se è del PSR passalo alla pipeline
            self.log(f"Passed file n {self.mycounter}")
            self.mycounter = self.mycounter + 1

            item = self.create_item(response, hash_code)
            self.complete_inizialization(item=item)
            yield item
        

        if response.headers.get('Content-Type', b'').startswith(b'text/html'):
            yield from self.follow_links(response)
    