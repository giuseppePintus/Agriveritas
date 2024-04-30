#!/bin/bash

pwd
# Change to the project directory
cd /home/jp/JPScraping/attemp3
pwd

echo "CIAO -> " ${region} " <-"

# echo "" > myLogSpider.txt
/usr/local/bin/scrapy crawl spi${region} --logfile JPSLog${region}.txt
#scrapy crawl try | tee JPLog.txt