CRAWLER_IMAGE=general_crawler
DOCKER_DIR=dockerImage
CONFIG_DIR=config

.PHONY: build run clean

build:
    docker build -t ${CRAWLER_IMAGE} ${DOCKER_DIR}

run:
    docker run --rm -v ${PWD}/config:/crawler/config \
        -v ${PWD}/output:/crawler/output \
        -v ${PWD}/logs:/crawler/logs \
        ${CRAWLER_IMAGE} \
        python -m scrapy crawl general \
        -a config_file=/crawler/config/crawler_config.json

clean:
    rm -rf output/*
    rm -rf logs/*