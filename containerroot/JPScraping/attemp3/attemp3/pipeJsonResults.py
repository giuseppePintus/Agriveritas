import json
from attemp3.items import WebDownloadedElement
from attemp3.pipeInterface import PipeInterface
import time

class JsonPipeline(PipeInterface):
    logFile = "myLogJSON"
    jsonFileName = "results"
    file = ""

    def open_spider(self, spider):
        super().open_spider(spider)
        a = time.time()
        self.jsonFileName += f"_{time.strftime('%m_%d_%H_%M', time.gmtime(a))}_{spider.code_region}.json"
        self.file = open(self.jsonFileName, 'w')
        self.file.write('[')


    def close_spider(self, spider):
        super().close_spider(spider)

    def process_item(self, item, spider):
        self.save_item_status(item)
        return item
    
    def behaviour_skipped(self, item : WebDownloadedElement, spider):
        #self.log("So no JSON element created")
        self.save_item_status(item)


    def save_item_status(self, item):
        if isinstance(item, WebDownloadedElement):
            row = {
                'ID_univoco': item.tableRow['ID_univoco'],
                'cod_reg': item.tableRow['cod_reg'],
                'ID_counter': item.tableRow['ID_counter'],
                'url_from': item.tableRow['url_from'],
                'HTTP_status': item.tableRow['HTTP_status'],
                'hash_code': item.tableRow['hash_code'],

                'file_downloaded_name': item.tableRow['file_downloaded_name'],
                'file_downloaded_dir': item.tableRow['file_downloaded_dir'],
                'timestamp_download': item.tableRow['timestamp_download'],
                'timestamp_mod_author': item.tableRow['timestamp_mod_author'],

                'embed_risorsa': item.tableRow['embed_risorsa'],
                'is_training': item.tableRow['is_training'],
               
                'aborted': item.settingPart['aborted'],
                'abortReason': item.settingPart['abortReason'],
                'allowedContentType': item.settingPart['allowedContentType'],
            }
            json.dump(row, self.file, indent=4)
            self.file.write(',\n')  # add a newline between each JSON object
            self.log("dumped file " + item.tableRow['ID_univoco'])

    def close_spider(self, spider):
        try:
            super().close_spider()
        finally:
            self.file.write(']')
            self.file.close()