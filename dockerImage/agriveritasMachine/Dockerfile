FROM huggingface/transformers-pytorch-latest-gpu
#FROM nvidia/cuda:11.7.1-cudnn8-runtime-ubuntu20.04

#RUN apt-get update && apt-get install -y python3 python3-pip

COPY scrapingRequirement.txt .
RUN pip3 install -r scrapingRequirement.txt

### cambiata interfaccia web ###
#COPY webRequirement.txt .
#RUN pip install -r webRequirement.txt

EXPOSE 8501
