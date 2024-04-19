#!/bin/bash
# pwd
# # Change to the project directory
# cd /home/jp/JPScraping/attemp3
# pwd

# echo "CIAO"

echo "" > myLogSpider.txt
if [[ ($# > 0) ]]; then
    if [[ ($1 == "C") || ($2 == "C") ]]; then
        rm -r downloadER
        rm -r downloadV
        rm *Log*.txt
    fi
    if [[ ($1 == "R") || ($2 == "R") ]]; then
        scrapy crawl scraperER --logfile JPSLog.txt
    fi
    if [[ ($1 == "V") || ($2 == "V") ]]; then
        scrapy crawl scraperVeneto --logfile JPSLog.txt
    fi
fi
    



# scrapy crawl try | tee JPLog.txt
