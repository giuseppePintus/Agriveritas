# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TableRowInfos(scrapy.Item):
    ID_univoco = scrapy.Field()
    cod_reg = scrapy.Field()
    ID_counter = scrapy.Field()
    url_from = scrapy.Field()
    HTTP_status = scrapy.Field()
    hash_code = scrapy.Field()
    
    file_downloaded_name = scrapy.Field()
    file_downloaded_dir = scrapy.Field()
    timestamp_download = scrapy.Field()
    timestamp_mod_author = scrapy.Field()

    embed_risorsa = scrapy.Field()
    is_training = scrapy.Field()
    
class SettingsElement(scrapy.Item):
    aborted = scrapy.Field()
    abortReason = scrapy.Field()
    allowedContentType = scrapy.Field()

    def __init__(self):
        super().__init__()
        self["aborted"] = False



class WebDownloadedElement(scrapy.Item):
    response = scrapy.Field()
    tableRow = TableRowInfos() #requiredMainTableInfo,
    domains = scrapy.Field()
    settingPart = SettingsElement()

    # def __init__(self, response, domains):
    #     super().__init__()
    #     self['response'] = response
    #     self['domains'] = domains
    #     self['tableRow'] = TableRowInfos()
    #     self['settingPart'] = SettingsElement()
    
