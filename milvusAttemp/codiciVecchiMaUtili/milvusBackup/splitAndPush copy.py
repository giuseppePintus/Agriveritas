# # https://github.com/LazaUK/AOAI-LangChain-Milvus/blob/main/AOAI_langchain_Milvus.ipynb
import time

# # # Define Milvus vector store parameters
# # MILVUS_HOST = "0.0.0.0"
# # MILVUS_PORT = "9091"

# from langchain.document_loaders import PyPDFLoader

filename="try.pdf"

# # Create array of pages
# loader = PyPDFLoader("try.pdf")
# pages = loader.load_and_split()
# # Check number of pages
# print(f"Number of pages in a new array: {len(pages)}")
# print(f"Content of 1st page: {pages[0]}")

# # documents = [t.page_content for t in pages]
# # for p in documents:
# #     print(p)

# from langchain.text_splitter import RecursiveCharacterTextSplitter
# #splitting the text into
# text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
# texts = text_splitter.split_documents(pages) #documents

# print("##########################################################")
# for d in texts:
#     print(d)

# finChunks = [t.page_content for t in texts]



# from pymilvus.model.hybrid import BGEM3EmbeddingFunction

# bge_m3_ef = BGEM3EmbeddingFunction(
#     model_name='BAAI/bge-m3',
#     device='cuda',
#     use_fp16=True
# )

# docs_embeddings = bge_m3_ef.encode_documents(finChunks)
 
# print("Embeddings:", docs_embeddings)
# print("Dense document dim:", bge_m3_ef.dim["dense"], docs_embeddings["dense"][0].shape)





















from pymilvus import connections, Collection, utility, FieldSchema, DataType, CollectionSchema

# Connect to the Milvus service
connections.connect("default", host="milvus-standalone", port="19530")   #host="milvus-standalone"

# # Define the schema for the collection
# schema = CollectionSchema(
#     fields=[
#         FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
#         FieldSchema(name="vec", dtype=DataType.FLOAT_VECTOR, dim=128),
#     ],
#     description="example collection"
# )

from pymilvus.orm.schema import CollectionSchema as ORMCollectionSchema


# class CustomCollectionSchema(ORMCollectionSchema):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self._strict = False

def concat_int_fields(ID_univoco_risorsa, ID_chunk):
    return f"{ID_univoco_risorsa}_{ID_chunk}"[:255]


def create_collections():
    risorsa_schema = CollectionSchema(
        fields=[
            FieldSchema(name="ID_univoco", dtype=DataType.INT64, is_primary=True),
            FieldSchema(name="cod_regione", dtype=DataType.VARCHAR, max_length=2),
            FieldSchema(name="url", dtype=DataType.VARCHAR, max_length=300),
            FieldSchema(name="HTTP_status", dtype=DataType.INT16),
            FieldSchema(name="hash_code", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="file_name", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="file_dir", dtype=DataType.VARCHAR, max_length=300),
            # FieldSchema(name="original_content", dtype=DataType.BINARY, max_length=1),
            # FieldSchema(name="parsed_content", dtype=DataType.BINARY, max_length=1),
            FieldSchema(name="timestamp_download", dtype=DataType.INT32),
            FieldSchema(name="timestamp_mod_author", dtype=DataType.INT32),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=128)  # Add a vector field
        ],
        description="RISORSA collection"
    )

    chunk_schema = CollectionSchema(
        fields=[
            # FieldSchema(name="ID_univoco_risorsa", dtype=DataType.INT64, is_primary=True),
            # FieldSchema(name="ID_chunk", dtype=DataType.INT64, is_primary=True),
            # FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1024)
            FieldSchema(name="ID", dtype=DataType.VARCHAR, max_length=255, is_primary=True),
            FieldSchema(name="ID_univoco_risorsa", dtype=DataType.INT64),
            FieldSchema(name="ID_chunk", dtype=DataType.INT64),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1024)
        ],
        description="CHUNK collection"
    )

    # Create the RISORSA collection
    risorsa_collection = Collection(name="RISORSA", schema=risorsa_schema)

    # Create an index on the primary key field "ID_univoco" for the RISORSA collection
    risorsa_collection.create_index(
        field_name="ID_univoco",
        index_params={"index_type": "STL_SORT"}
    )

    # Create an index on the vector field "vector" for the RISORSA collection
    risorsa_collection.create_index(
        field_name="vector",
        index_params={"index_type": "FLAT", "metric_type": "L2"}
    )

    # Create the CHUNK collection
    chunk_collection = Collection(name="CHUNK", schema=chunk_schema)

    # Create an index on the primary key field "ID" for the CHUNK collection
    chunk_collection.create_index(
        field_name="ID",
        index_params={"index_type": "Trie"}
    )

    # Create an index on the vector field "embedding" for the CHUNK collection
    chunk_collection.create_index(
        field_name="embedding",
        index_params={"index_type": "FLAT", "metric_type": "L2"}
    )

    return [risorsa_schema, chunk_schema]



getTime = None

counterFile = 0
counterEmbedding = 0
url = ""
httpStatus = 200
hashCode = "012345678_012345678_012345678_012345678_012345678_012345678_1234"
myFilename = filename
myPath = "/"
timestamp_download = int(time.time())
timestamp_mod_author = int(getTime) if getTime else 0

import random
from itertools import chain

def generateRandomEmbedding(amount):
    v = [[random.uniform(0.0, 1.0)] * amount]
    return list(chain.from_iterable(v))  # Flatten the 2D list

 
risorsa_collection, chunk_collection = create_collections()

# Drop the existing collections (if any)
if utility.has_collection("RISORSA"):
    risorsa_collection = Collection("RISORSA")
    risorsa_collection.drop()

if utility.has_collection("CHUNK"):
    chunk_collection = Collection("CHUNK")
    chunk_collection.drop()

risorsa_collection, chunk_collection = create_collections()


amountPage = 5
amountChunck = 5
for i in range(0,amountPage):
    dataR = [{
        "ID_univoco": i,
        "cod_regione": "V",
        "url": url,
        "HTTP_status" : httpStatus,
        "hash_code" : hashCode,
        "file_name" : myFilename,
        "file_dir" : myPath,
        # FieldSchema(name="original_content", dtype=DataType.BINARY, max_length=1),
        # FieldSchema(name="parsed_content", dtype=DataType.BINARY, max_length=1),
        "timestamp_download" : timestamp_download,
        "timestamp_mod_author" : timestamp_mod_author,
        "vector" : generateRandomEmbedding(128)  # Add a vector field
    }]
    risorsa_collection.insert(dataR)
    for j in range(0,amountChunck):
        dataC = [{
            "ID" : concat_int_fields(i,j),
            "ID_univoco_risorsa" : i,
            "ID_chunk" : j,
            "embedding" : generateRandomEmbedding(1024)
        }]
        chunk_collection.insert(dataC)

#
risorsa_collection.flush()
chunk_collection.flush()

# # Create an index for the collection
# index_params = {"index_type": "IVF_FLAT", "metric_type": "L2", "params": {"nlist": 128}}
# collection.create_index("vec", index_params)

# Load the collection
risorsa_collection.load()
chunk_collection.load()


searchingChunk = generateRandomEmbedding(1024)
print("--> " + str(searchingChunk))
# Search the collection for vectors that are similar to [1]*128
results = chunk_collection.search(searchingChunk, "embedding", limit=3, param={"nprobe": 10})

# Print the results
for result in results:
    print(result)

# # Disconnect from the Milvus service
connections.disconnect("default")







#print("Sparse document dim:", bge_m3_ef.dim["sparse"], list(docs_embeddings["sparse"])[0].shape)



# from langchain.vectorstores import Milvus

# collectionName = "try"
# # Creating new collection in Milvus vector store
# vector_store = Milvus.from_documents(
#     texts,
#     embedding = docs_embeddings,
#     collection_name = collectionName,
#     connection_args={"host": MILVUS_HOST, "port": MILVUS_PORT}
# )

# # Retrieving stored collection from Milvus vector store
# vector_store = Milvus(
#     embedding_function = bge_m3_ef,    
#     collection_name = collectionName,
#     connection_args={"host": MILVUS_HOST, "port": MILVUS_PORT}
# ) 
 
# # queries = ["When was artificial intelligence founded",
# #            "Where was Alan Turing born?"]
 
# # query_embeddings = bge_m3_ef.encode_queries(queries)
 
# # # Print embeddings
# # print("Embeddings:", query_embeddings)
# # # Print dimension of dense embeddings
# # print("Dense query dim:", bge_m3_ef.dim["dense"], query_embeddings["dense"][0].shape)
# # # Since the sparse embeddings are in a 2D csr_array format, we convert them to a list for easier manipulation.
# # #print("Sparse query dim:", bge_m3_ef.dim["sparse"], list(query_embeddings["sparse"])[0].shape)


