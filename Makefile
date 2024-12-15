USER_CONTAINER=pintus
HOME_CONTAINER_DIR=/home/${USER_CONTAINER}

LOCAL_DIR__ROOT_CONTAINER=containerroot
TEST_DIR__ROOT_CONTAINER=testroot
DOCKER_IMAGE_DIR=dockerImage

DOCKER_IMAGE=agriveritas
WEB_IMAGE=rag_gradio_image


SCRAPY_ROOT_COMMAND=JPScraping/attemp3/e.sh

region?=ER-PSR

WEB_PORT=37330


all:

.PHONY: setupMachine openMachine restartMilvusDb createMilvusDb setupWebMachine initPrg clear safeclear basicDownload download downloadAll test openWebApp openWebMachine


### creazione container docker ##################### 


#creazione container per scraping
setupMachine:
	echo "Creando ${DOCKER_IMAGE}"
	docker build -t ${DOCKER_IMAGE} ${DOCKER_IMAGE_DIR}/agriveritasMachine

#apertura container in shell bash
openMachine:
	docker run --rm -it \
		--net milvus \
		--gpus device=0 \
		-v ./${LOCAL_DIR__ROOT_CONTAINER}:${HOME_CONTAINER_DIR} ${DOCKER_IMAGE} 


#forzatura ripartenza istanza Milvus
restartMilvusDb:
	-docker-compose -f ${DOCKER_IMAGE_DIR}/milvus/docker-compose.yml stop
	-docker-compose -f ${DOCKER_IMAGE_DIR}/milvus/docker-compose.yml start

#creazione istanza Milvus
createMilvusDb:
	docker-compose -f ${DOCKER_IMAGE_DIR}/milvus/docker-compose.yml up -d
	make restartMilvusDb

#creazione container per scraping
setupWebMachine:
	echo "Creando ${WEB_IMAGE}"
	docker build -t ${WEB_IMAGE} ${DOCKER_IMAGE_DIR}/gradioMachine

initPrg:
	make setupMachine
	make setupWebMachine
	make createMilvusDb
	



### uso dei servizi docker ########################################################################################

#pulizia file scaricati per una certa regione
clear:
	-rm -rf containerroot/JPScraping/attemp3/download/${region}/*
	-rm containerroot/JPScraping/attemp3/*${region}.txt

#salvataggio file in un'altra destinazione logica ma pulizia di quella configurata in scrapy nel relativo file settings.py
safeclear:
	-cp -rf containerroot/JPScraping/attemp3/download/${region}/* rubbish/${region} && rm -rf containerroot/JPScraping/attemp3/download/${region}/*
	-mv containerroot/JPScraping/attemp3/*${region}.txt rubbish
	make clear

#avvia il processo di scraping per una regione
basicDownload:
	echo "Downloading "${region}" Agea"
	docker run --rm -it --net milvus -v ./${LOCAL_DIR__ROOT_CONTAINER}:${HOME_CONTAINER_DIR} \
		-e region=${region} \
		--gpus device=00 \
		${DOCKER_IMAGE} \
		${HOME_CONTAINER_DIR}/${SCRAPY_ROOT_COMMAND}
	

#resetta il mapping locale e riparte un nuovo download
download:
	make safeclear region=${region}
	make basicDownload region=${region}

# downloadAll:
# 	for R in ["ER", "V"]; do make clear region=${R}; make basicDownload region=${R}: done
# 	# make basicDownload region=${region}


#adattamento container per avviare foglio di testing
INIT_TEST = testAgriveritas.sh
test:
	docker run --rm -it\
		--gpus device=0 \
		-p ${WEB_PORT}:8501 \
		-v ./${TEST_DIR__ROOT_CONTAINER}:${HOME_CONTAINER_DIR} \
		${DOCKER_IMAGE} \
		bash ${HOME_CONTAINER_DIR}/${INIT_TEST} 
	

WEB_CONTAINER="rag_gradio_container"
#GRADIO_ROOT_COMMAND=interfacciaWeb/FastChat_RAG/launchWebGradio.sh
openWebApp:
	echo "Apro gradio!"
	docker run -it -v ./containerroot/interfacciaWeb/FastChat_RAG:/FastChat_RAG --name ${WEB_CONTAINER} \
		--net milvus \
		--ipc=host \
		--gpus=all \
		-p ${WEB_PORT}:7860 \
		${WEB_IMAGE} 


openWebMachine:
	docker start -i ${WEB_CONTAINER}





### comandi vecchi utili a rigenereare df_faq e df_chunk del paper ##########
#DATASET_CREATION_ROOT_COMMAND=testing/createDataset.sh
#createDataset:
#	docker run --rm -it -v ./${LOCAL_DIR__ROOT_CONTAINER}:${HOME_CONTAINER_DIR} \
#			--gpus device=1 \
#			--net milvus \
#			${DOCKER_IMAGE} \
#			${HOME_CONTAINER_DIR}/${DATASET_CREATION_ROOT_COMMAND} 

#FALSE_CREATION_ROOT_COMMAND=testing/generateFalseResponse.sh
#genFalse:
#	docker run --rm -it -v ./${LOCAL_DIR__ROOT_CONTAINER}:${HOME_CONTAINER_DIR} \
#			--gpus device=1 \
#			${DOCKER_IMAGE} \
#			${HOME_CONTAINER_DIR}/${FALSE_CREATION_ROOT_COMMAND} 

#EXTRACT_MILVUS_ROOT_COMMAND=testing/extractMilvus.sh
#extractChunk:
#	docker run --rm -it -v ./${LOCAL_DIR__ROOT_CONTAINER}:${HOME_CONTAINER_DIR} \
#			--net milvus \
#			${DOCKER_IMAGE} \
#			${HOME_CONTAINER_DIR}/${EXTRACT_MILVUS_ROOT_COMMAND} 


#TMP_ROOT_COMMAND=testing/tmp.sh
#tmp:
#	docker run --rm -it -v ./${LOCAL_DIR__ROOT_CONTAINER}:${HOME_CONTAINER_DIR} \
#			--net milvus \
#			${DOCKER_IMAGE} \
#			${HOME_CONTAINER_DIR}/${TMP_ROOT_COMMAND} 



## comandi vecchi utili a rigenereare df_faq e df_chunk del paper ##########
OTHER_COMMAND=other/other.sh
other:
	docker run --rm -it -v ./${LOCAL_DIR__ROOT_CONTAINER}:${HOME_CONTAINER_DIR} \
			--gpus device=0 \
			--net milvus \
			${DOCKER_IMAGE} \
			${HOME_CONTAINER_DIR}/${OTHER_COMMAND}

#avvia il processo di scraping generico usando un file di configurazione
crawl_website:
    echo "Starting general crawler with config: "${config}
    docker run --rm -it --net milvus -v ./${LOCAL_DIR__ROOT_CONTAINER}:${HOME_CONTAINER_DIR} \
        -e CONFIG_FILE=${config} \
        --gpus device=00 \
        ${DOCKER_IMAGE} \
        ${HOME_CONTAINER_DIR}/${SCRAPY_ROOT_COMMAND}

#resetta e avvia nuovo crawling
crawl_reset:
    make safeclear config=${config} \
    make crawl_website config=${config}
