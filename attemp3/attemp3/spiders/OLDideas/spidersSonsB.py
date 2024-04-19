import CreateTableB

class ERSpired(CreateTable):
    name = 'scraperER'
    start_urls = [
        "https://agrea.regione.emilia-romagna.it/",
    ]
    allowed_domains = ['agrea.regione.emilia-romagna.it']
    region = "ER"


class VenetoSpider(CreateTable):
    name = 'scraperVeneto'
    start_urls = [
        "https://www.avepa.it/",
    ]
    allowed_domains = ['www.avepa.it']
    region = "V"