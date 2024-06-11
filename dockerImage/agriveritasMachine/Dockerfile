# # FROM huggingface/transformers-pytorch-latest-gpu

# FROM prova1_image

# # RUN pip install -r req.txt

# RUN pip install scrapy 
# RUN pip install beautifulsoup4
# RUN pip install --upgrade pymilvus langchain openai tiktoken
# #-r ../requirement.txt

FROM huggingface/transformers-pytorch-latest-gpu
#FROM nvidia/cuda:11.7.1-cudnn8-runtime-ubuntu20.04

#RUN apt-get update && apt-get install -y python3 python3-pip

COPY webRequirement.txt .
COPY scrapingRequirement.txt .

RUN pip install -r scrapingRequirement.txt
RUN pip install -r webRequirement.txt

EXPOSE 8501
