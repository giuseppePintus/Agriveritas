# Import required packages
import openai
import os

# Define Azure OpenAI endpoint parameters
openai.api_type = "azure"
openai.api_version = os.getenv("OPENAI_API_VERSION") # Set AOAI API version value as env variable
openai.api_base = os.getenv("OPENAI_API_BASE") # Set AOAI endpoint value as env variable
openai.api_key = os.getenv("OPENAI_API_KEY") # Set AOAI API key as env variable
GPT_deployment = os.getenv("OPENAI_API_DEPLOY") # Set AOAI GPT deployment name as env variable
ADA_deployment = os.getenv("OPENAI_API_DEPLOY_EMBED") # Set AOAI Ada deployment name as env variable

# Define Milvus vector store parameters
MILVUS_HOST = "localhost"
MILVUS_PORT = "19530"




#Loading data
from langchain.document_loaders import PyPDFLoader

# Create array of pages
loader = PyPDFLoader("data/NorthwindHealthPlus_BenefitsDetails.pdf")
pages = loader.load_and_split()
# Check number of pages
print(f"Number of pages in a new array: {len(pages)}")
print(f"Content of 1st page: {pages[0]}")



