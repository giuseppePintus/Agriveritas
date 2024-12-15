FROM huggingface/transformers-pytorch-latest-gpu

COPY scrapingRequirement.txt .

# Fix potential conflicts
RUN pip uninstall -y urllib3 transformers FlagEmbedding
RUN pip install -r scrapingRequirement.txt

# Add environment check
RUN python -c "import transformers; import urllib3; print('Dependencies OK')"

### cambiata interfaccia web ###
#COPY webRequirement.txt .
#RUN pip install -r webRequirement.txt

EXPOSE 8501
