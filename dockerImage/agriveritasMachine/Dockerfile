# # FROM huggingface/transformers-pytorch-latest-gpu

# FROM prova1_image

# # RUN pip install -r req.txt

# RUN pip install scrapy 
# RUN pip install beautifulsoup4
# RUN pip install --upgrade pymilvus langchain openai tiktoken
# #-r ../requirement.txt

FROM huggingface/transformers-pytorch-latest-gpu

COPY webRequirement.txt .
COPY scrapingRequirement.txt .

RUN pip install -r scrapingRequirement.txt
RUN pip install -r webRequirement.txt

EXPOSE 8501
