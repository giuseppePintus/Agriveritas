from attemp3.spiders.motherSpider import BaseSpider
from attemp3.items import WebDownloadedElement

class SpiderER(BaseSpider):
    name = 'spiER'
    
    start_urls = ["https://agrea.regione.emilia-romagna.it/"]
    
    allowed_domains = [
        'agrea.regione.emilia-romagna.it'
    ]

    code_region = "ER"
    
    def complete_inizialization(self, item: WebDownloadedElement):
        item["domains"] = self.allowed_domains
        item.tableRow["cod_reg"] = self.code_region
        # item.tableRow.cod_reg = "ER"

        # # This method should be implemented by the subclass if they need specific item creation
        # raise NotImplementedError("You must implement the method create_item()")
