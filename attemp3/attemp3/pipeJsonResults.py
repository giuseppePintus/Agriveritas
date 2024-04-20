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

    def process_item(self, item, spider):
        if isinstance(item, WebDownloadedElement):
            row = {
                'IDuni': item.tableRow['IDuni'],
                'cod_reg': item.tableRow['cod_reg'],
                'url_from': item.tableRow['url_from'],
                'HTTPStatus': item.tableRow['HTTPStatus'],
                'hash_code': item.tableRow['hash_code'],
                'file_downloaded_name': item.tableRow['file_downloaded_name'],
                'file_downloaded_dir': item.tableRow['file_downloaded_dir'],
                'timestamp_download': item.tableRow['timestamp_download'],
                'timestamp_mod_author': item.tableRow['timestamp_mod_author'],
                'aborted': item.settingPart['aborted'],
                'abortReason': item.settingPart['abortReason'],
                'allowedContentType': item.settingPart['allowedContentType'],
            }
            json.dump(row, self.file, indent=4)
            self.file.write('\n')  # add a newline between each JSON object
        return item

    def close_spider(self, spider):
        try:
            super().close_spider()
        finally:
            self.file.close()