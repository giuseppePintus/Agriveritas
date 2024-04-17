#!/bin/bash

pwd
# Change to the project directory
cd /home/jp/JPScraping/attemp3
pwd

echo "CIAO"

echo "" > myLogSpider.txt
/usr/local/bin/scrapy crawl try --logfile JPSLog.txt
#scrapy crawl try | tee JPLog.txt