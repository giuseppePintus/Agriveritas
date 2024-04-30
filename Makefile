USER_CONTAINER=jp
HOME_CONTAINER_DIR=/home/${USER_CONTAINER}
LOCAL_DIR__ROOT_CONTAINER=containerroot
DOCKER_IMAGE=agriveritas1

SCRAPY_ROOT_COMMAND=JPScraping/attemp3/e.sh

region?=V


all:

.PHONY: setupMachine openMachine clear basicDownload download milvusCheck createWeb

setupMachine:
	echo "->"${DOCKER_IMAGE}
	docker build -t ${DOCKER_IMAGE} build/agriveritasMachine

openMachine: 	
	docker run --rm -it\
		-p 37336:8501 \
		--net milvus \
		-v ./${LOCAL_DIR__ROOT_CONTAINER}:${HOME_CONTAINER_DIR} ${DOCKER_IMAGE} 

clear:
	# -cp -rf containerroot/JPScraping/attemp3/download/${region}/* rubbish/${region} && rm -rf containerroot/JPScraping/attemp3/download/${region}/*
	# -mv containerroot/JPScraping/attemp3/*${region}.txt rubbish

basicDownload:
	# echo "Downloading "${region}" Agea"
	# docker run --net milvus -v ./${LOCAL_DIR__ROOT_CONTAINER}:${HOME_CONTAINER_DIR} \
	# 	-e region=${region} \
	# 	--gpus all \
	# 	${DOCKER_IMAGE} \
	# 	${HOME_CONTAINER_DIR}/${SCRAPY_ROOT_COMMAND} ${region}
	
download:
	make clear region=${region}
	make basicDownload region=${region}

# downloadAll:
# 	for R in ["ER", "V"]; do make clear region=${R}; make basicDownload region=${R}: done
# 	# make basicDownload region=${region}


MILVUS_ROOT_COMMAND=milvusAttemp/milvusSelect.sh

milvusCheck:
	echo "Select quasi * da Chuck, tabella Milvus"
	docker run --net milvus -v ./${LOCAL_DIR__ROOT_CONTAINER}:${HOME_CONTAINER_DIR} \
		${DOCKER_IMAGE} \
		${HOME_CONTAINER_DIR}/${MILVUS_ROOT_COMMAND} 
	


FLASK_ROOT_COMMAND=interfacciaWeb/activeWeb.sh

createWeb:
	echo "Apro il sito!"
	
	docker run --rm -v ./${LOCAL_DIR__ROOT_CONTAINER}:${HOME_CONTAINER_DIR} \
		--net milvus \
		-p 37336:8501 \
		${DOCKER_IMAGE} \
		${HOME_CONTAINER_DIR}/${FLASK_ROOT_COMMAND} 
	
