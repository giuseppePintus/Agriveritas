# https://github.com/LazaUK/AOAI-LangChain-Milvus/blob/main/AOAI_langchain_Milvus.ipynb

# Import required packages
import openai
import os

# # Define Azure OpenAI endpoint parameters
# openai.api_type = "azure"
# openai.api_version = os.getenv("OPENAI_API_VERSION") # Set AOAI API version value as env variable
# openai.api_base = os.getenv("OPENAI_API_BASE") # Set AOAI endpoint value as env variable
# openai.api_key = os.getenv("OPENAI_API_KEY") # Set AOAI API key as env variable
# GPT_deployment = os.getenv("OPENAI_API_DEPLOY") # Set AOAI GPT deployment name as env variable
# ADA_deployment = os.getenv("OPENAI_API_DEPLOY_EMBED") # Set AOAI Ada deployment name as env variable

# Define Milvus vector store parameters
MILVUS_HOST = "0.0.0.0"
MILVUS_PORT = "9091"



from langchain.document_loaders import PyPDFLoader

# Create array of pages
loader = PyPDFLoader("try.pdf")
pages = loader.load_and_split()
# Check number of pages
print(f"Number of pages in a new array: {len(pages)}")
print(f"Content of 1st page: {pages[0]}")


documents = [t.page_content for t in pages]
for p in documents:
    print(p)




from langchain.text_splitter import RecursiveCharacterTextSplitter

#splitting the text into
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
texts = text_splitter.split_documents(pages) #documents

print("##########################################################")
for d in texts:
    print(d)

finChunks = [t.page_content for t in texts]



from pymilvus.model.hybrid import BGEM3EmbeddingFunction

bge_m3_ef = BGEM3EmbeddingFunction(
    model_name='BAAI/bge-m3',
    device='cuda',
    use_fp16=True
)
 
# docs = [
#     "Artificial intelligence was founded as an academic discipline in 1956.",
#     "Alan Turing was the first person to conduct substantial research in AI.",
#     "Born in Maida Vale, London, Turing was raised in southern England.",
# ]
 
docs_embeddings = bge_m3_ef.encode_documents(finChunks)
 
print("Embeddings:", docs_embeddings)
print("Dense document dim:", bge_m3_ef.dim["dense"], docs_embeddings["dense"][0].shape)
#print("Sparse document dim:", bge_m3_ef.dim["sparse"], list(docs_embeddings["sparse"])[0].shape)

from langchain.vectorstores import Milvus


collectionName = "try"
# Creating new collection in Milvus vector store
vector_store = Milvus.from_documents(
    texts,
    embedding = docs_embeddings,
    collection_name = collectionName,
    connection_args={"host": MILVUS_HOST, "port": MILVUS_PORT}
)

# Retrieving stored collection from Milvus vector store
vector_store = Milvus(
    embedding_function = bge_m3_ef,    
    collection_name = collectionName,
    connection_args={"host": MILVUS_HOST, "port": MILVUS_PORT}
) 
 
# queries = ["When was artificial intelligence founded",
#            "Where was Alan Turing born?"]
 
# query_embeddings = bge_m3_ef.encode_queries(queries)
 
# # Print embeddings
# print("Embeddings:", query_embeddings)
# # Print dimension of dense embeddings
# print("Dense query dim:", bge_m3_ef.dim["dense"], query_embeddings["dense"][0].shape)
# # Since the sparse embeddings are in a 2D csr_array format, we convert them to a list for easier manipulation.
# #print("Sparse query dim:", bge_m3_ef.dim["sparse"], list(query_embeddings["sparse"])[0].shape)


