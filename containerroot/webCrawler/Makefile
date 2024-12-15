CRAWLER_IMAGE=general_crawler
DOCKER_DIR=dockerImage
CONFIG_DIR=config

.PHONY: build run clean

build:
	docker build -t ${CRAWLER_IMAGE} .

crawl:
	docker run --rm \
        -v ${PWD}/config:/crawler/config:ro \
        -v ${PWD}/output:/crawler/output \
        -v ${PWD}/logs:/crawler/logs \
        ${CRAWLER_IMAGE} \
        scrapy crawl general \
        -a config_file=/crawler/config/crawler_config.json \
        -a site=${site} \
        --logfile=/crawler/logs/crawler.log \
        -L DEBUG

clean:
	rm -rf output/* logs/*