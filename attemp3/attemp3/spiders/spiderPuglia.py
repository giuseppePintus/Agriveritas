from attemp3.spiders.motherSpider import BaseSpider
from attemp3.items import WebDownloadedElement

class SpiderPuglia(BaseSpider):
    name = 'spiP'
    
    start_urls = [
        "https://psr.regione.puglia.it/"
    ]
    
    allowed_domains = [
        'psr.regione.puglia.it'
    ]

    code_region = "P"
    
    def complete_inizialization(self, item: WebDownloadedElement):
        item["domains"] = self.allowed_domains
        item.tableRow["cod_reg"] = self.code_region

        # # This method should be implemented by the subclass if they need specific item creation
        # raise NotImplementedError("You must implement the method create_item()")
