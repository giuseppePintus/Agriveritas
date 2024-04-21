import csv
from attemp3.items import WebDownloadedElement
from attemp3.pipeInterface import PipeInterface
import time

class CsvPipeline(PipeInterface):
    logFile = "myLogCSV"

    csvFileName = "results"
    file = ""
    

    def open_spider(self, spider):
        super().open_spider(spider) # = to -> self.logFile += spider.code_region + ".txt"; and to ->self.pdLogFile = open(self.logFile, "w")
        a = time.time()
        self.csvFileName += f"_{time.strftime('%m_%d_%H_%M', time.gmtime(a))}_{spider.code_region}.csv"
        
        self.file = open(self.csvFileName, 'w', newline='')
        self.exporter = csv.DictWriter(self.file, fieldnames=[
            'IDuni', 'cod_reg', 'url_from', 'HTTPStatus', 'hash_code',
            'file_downloaded_name', 'file_downloaded_dir', 'timestamp_download',
            'timestamp_mod_author', 'aborted', 'abortReason', 'allowedContentType'
        ])
        self.exporter.writeheader()  # <--- Print the header
        
        
        
    def close_spider(self, spider):
        super().close_spider() # = to write self.pdLogFile.close()  
        self.exporter.finish_exporting()
        self.file.close()

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
            self.exporter.writerow(row)
        return item
    

    def behaviour_skipped(self, item : WebDownloadedElement, spider):
        self.log("So no CVS row created")
    