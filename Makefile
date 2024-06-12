USER_CONTAINER=jp
HOME_CONTAINER_DIR=/home/${USER_CONTAINER}
LOCAL_DIR__ROOT_CONTAINER=containerroot
DOCKER_IMAGE=agriveritas
WEB_IMAGE=rag_gradio_image

SCRAPY_ROOT_COMMAND=JPScraping/attemp3/e.sh

region?=ER2PSR


all:

.PHONY: setupMachine openMachine clear basicDownload download milvusCheck createWeb

setupMachineAgriveritas:
	echo "Building -> "${DOCKER_IMAGE}
	docker build -t ${DOCKER_IMAGE} dockerImage/agriveritasMachine

setupMachineWeb:
	echo "Building -> "${DOCKER_IMAGE}
	docker build -t ${WEB_IMAGE} dockerImage/webapp

setupMachineMilvusCompose:
	echo "Building -> milvus compose"
	-docker-compose -f dockerImage/miluvs/docker-compose.yml build
	
setup:
	setupMachineAgriveritas
	setupMachineWeb
	setupMachineMilvusCompose


openMachine:
	docker run --rm -it\
		--net milvus \
		--gpus device=all \
		-p 37336:8501 \
		-v ./${LOCAL_DIR__ROOT_CONTAINER}:${HOME_CONTAINER_DIR} ${DOCKER_IMAGE} 

clear:
	-rm -rf containerroot/JPScraping/attemp3/download/${region}/*
	-rm containerroot/JPScraping/attemp3/*${region}.txt

safeclear:
	-cp -rf containerroot/JPScraping/attemp3/download/${region}/* rubbish/${region} && rm -rf containerroot/JPScraping/attemp3/download/${region}/*
	-mv containerroot/JPScraping/attemp3/*${region}.txt rubbish
	make clear

basicDownload:
	echo "Downloading "${region}" Agea"
	docker run --rm -it --net milvus -v ./${LOCAL_DIR__ROOT_CONTAINER}:${HOME_CONTAINER_DIR} \
		-e region=${region} \
		--gpus device=00 \
		${DOCKER_IMAGE} \
		${HOME_CONTAINER_DIR}/${SCRAPY_ROOT_COMMAND} ${region}
	
download:
	make safeclear region=${region}
	make basicDownload region=${region}

MILVUS_ROOT_COMMAND=milvusAttemp/milvusSelect.sh

milvusCheck:
	echo "Select quasi * da Chuck, tabella Milvus"
	docker run  --rm -it --net milvus -v ./${LOCAL_DIR__ROOT_CONTAINER}:${HOME_CONTAINER_DIR} \
		--gpus device=0 \
		${DOCKER_IMAGE} \
		${HOME_CONTAINER_DIR}/${MILVUS_ROOT_COMMAND} 
	

PARTITION_ROOT_COMMAND=milvusAttemp/partAtt.sh

milvusCheckPartition:
	echo "Select quasi * da Chuck, tabella Milvus, MIGLIORATO (inizio a toccare le partition)"
	docker run  --rm -it --net milvus -v ./${LOCAL_DIR__ROOT_CONTAINER}:${HOME_CONTAINER_DIR} \
		${DOCKER_IMAGE} \
		${HOME_CONTAINER_DIR}/${PARTITION_ROOT_COMMAND} 
	

PURG_ROOT_COMMAND=milvusAttemp/purg.sh
milvusPurg:
	echo "Select quasi * da Chuck, tabella Milvus, MIGLIORATO (inizio a toccare le partition)"
	docker run --rm -it --net milvus -v ./${LOCAL_DIR__ROOT_CONTAINER}:${HOME_CONTAINER_DIR} \
		${DOCKER_IMAGE} \
		${HOME_CONTAINER_DIR}/${PURG_ROOT_COMMAND} 
	

A_ROOT_COMMAND=a/milvusLight.sh
a:
	docker run --rm -it -v ./${LOCAL_DIR__ROOT_CONTAINER}:${HOME_CONTAINER_DIR} \
		${DOCKER_IMAGE} \
		${HOME_CONTAINER_DIR}/${A_ROOT_COMMAND} start
	

FLASK_ROOT_COMMAND=interfacciaWeb/activeWeb.sh

createWeb:
	echo "Apro il sito!"
	
	docker run --rm -it -v ./${LOCAL_DIR__ROOT_CONTAINER}:${HOME_CONTAINER_DIR} \
		--net milvus \
		--gpus device=0 \
		-p 37336:8501 \
		${DOCKER_IMAGE} \
		${HOME_CONTAINER_DIR}/${FLASK_ROOT_COMMAND} 
	

STREAMLIT_ROOT_COMMAND=streamlit/streamlit.sh

createWeb2:
	echo "Apro il sito!"
	
	docker run --rm -it -v ./${LOCAL_DIR__ROOT_CONTAINER}:${HOME_CONTAINER_DIR} \
		--net miluvs \
		-p 37336:8501 \
		${DOCKER_IMAGE} \
		${HOME_CONTAINER_DIR}/${STREAMLIT_ROOT_COMMAND} 
	


GRADIO_ROOT_COMMAND=interfacciaWeb/FastChat_RAG/launchWebGradio.sh

createWeb3:
	echo "Apro gradio!"
	docker run -it -v ./containerroot/interfacciaWeb/FastChat_RAG:/FastChat_RAG --name rag_gradio_container \
		--net milvus \
		--ipc=host \
		--gpus=all \
		-p 37336:7860 \
		${WEB_IMAGE} \
		# FastChat_RAG \ 
		# ${HOME_CONTAINER_DIR}/${GRADIO_ROOT_COMMAND} 


