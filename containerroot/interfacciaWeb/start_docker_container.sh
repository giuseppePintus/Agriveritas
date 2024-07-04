#!/bin/bash


#docker run --name rag_gradio_container --net milvus -p 19530:19530 -p 37336:7860 --gpus=all --ipc=host -v ./FastChat_RAG:/FastChat_RAG -v ~/useful_cmd:/useful_cmd -it rag_gradio_image /bin/bash

docker run --name rag_gradio_container --net milvus -p 37336:7860 --gpus=all --ipc=host -v ./FastChat_RAG:/FastChat_RAG -v ~/useful_cmd:/useful_cmd -it rag_gradio_image /bin/bash