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
            'ID_univoco', 'cod_reg', 'ID_counter', 'url_from', 'HTTP_status', 'hash_code',
            'file_downloaded_name', 'file_downloaded_dir', 'timestamp_download', 'timestamp_mod_author',
            'is_training',
            'aborted', 'abortReason', 'allowedContentType'
        ])
        self.exporter.writeheader()  # <--- Print the header
        
        
        
    def close_spider(self, spider):
        super().close_spider() # = to write self.pdLogFile.close()  
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.save_item_status(item)
        return item
    

    def behaviour_skipped(self, item : WebDownloadedElement, spider):
        #self.log("So no CVS row created")
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

                'is_training': item.tableRow['is_training'],
               
                'aborted': item.settingPart['aborted'],
                'abortReason': item.settingPart['abortReason'],
                'allowedContentType': item.settingPart['allowedContentType'],
            }
            self.exporter.writerow(row)
    