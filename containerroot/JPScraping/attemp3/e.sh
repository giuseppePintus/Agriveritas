#!/bin/bash

pwd
# Change from /home/jp to /home/pintus
cd /home/pintus/JPScraping/attemp3
pwd

##  echo "RECEIVED -> " ${region} " <-"

# echo "" > myLogSpider.txt
##  /usr/local/bin/scrapy crawl spi${region} --logfile JPSLog${region}.txt
#scrapy crawl try | tee JPLog.txt




echo "RECEIVED CONFIG -> " ${CONFIG_FILE} " <-"

# Launch the general crawler with the config file
/usr/local/bin/scrapy crawl general_crawler -a config_file=${CONFIG_FILE} --logfile crawler_log.txt