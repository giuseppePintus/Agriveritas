# # # # https://github.com/LazaUK/AOAI-LangChain-Milvus/blob/main/AOAI_langchain_Milvus.ipynb
import time

from pymilvus import connections, Collection, utility, FieldSchema, DataType, CollectionSchema

connections.connect("default", host="milvus-standalone", port="19530")   #host="milvus-standalone"

# def create_collections():
#     risorsa_schema = CollectionSchema(
#         fields=[
#             FieldSchema(name="ID_univoco", dtype=DataType.INT64, is_primary=True),
#             FieldSchema(name="cod_regione", dtype=DataType.VARCHAR, max_length=2),
#             FieldSchema(name="url", dtype=DataType.VARCHAR, max_length=300),
#             FieldSchema(name="HTTP_status", dtype=DataType.INT16),
#             FieldSchema(name="hash_code", dtype=DataType.VARCHAR, max_length=64),
#             FieldSchema(name="file_name", dtype=DataType.VARCHAR, max_length=100),
#             FieldSchema(name="file_dir", dtype=DataType.VARCHAR, max_length=300),
#             FieldSchema(name="timestamp_download", dtype=DataType.INT32),
#             FieldSchema(name="timestamp_mod_author", dtype=DataType.INT32),
#             FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=128)  # Add a vector field
#         ],
#         description="RISORSA collection"
#     )

#     chunk_schema = CollectionSchema(
#         fields=[
#             FieldSchema(name="ID", dtype=DataType.VARCHAR, max_length=255, is_primary=True),
#             FieldSchema(name="ID_univoco_risorsa", dtype=DataType.INT64),
#             FieldSchema(name="ID_chunk", dtype=DataType.INT64),
#             FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1024)
#         ],
#         description="CHUNK collection"
#     )

#     # Create the RISORSA collection
#     risorsa_collection = Collection(name="RISORSA", schema=risorsa_schema)

#     # Create an index on the primary key field "ID_univoco" for the RISORSA collection
#     risorsa_collection.create_index(
#         field_name="ID_univoco",
#         index_params={"index_type": "STL_SORT"}
#     )

#     # Create an index on the vector field "vector" for the RISORSA collection
#     risorsa_collection.create_index(
#         field_name="vector",
#         index_params={"index_type": "FLAT", "metric_type": "L2"}
#     )

#     # Create the CHUNK collection
#     chunk_collection = Collection(name="CHUNK", schema=chunk_schema)

#     # Create an index on the primary key field "ID" for the CHUNK collection
#     chunk_collection.create_index(
#         field_name="ID",
#         index_params={"index_type": "Trie"}
#     )

#     # Create an index on the vector field "embedding" for the CHUNK collection
#     chunk_collection.create_index(
#         field_name="embedding",
#         index_params={"index_type": "FLAT", "metric_type": "L2"}
#     )

#     return [risorsa_collection, chunk_collection]


import random
from itertools import chain

def generateRandomEmbedding(amount):
    return [random.uniform(0.0, 1.0) for _ in range(amount)]

# risorsa_collection, chunk_collection = create_collections()

# Load the existing collections
risorsa_collection = Collection("RISORSA")
chunk_collection = Collection("CHUNK")

# # Load the collection
risorsa_collection.load()
chunk_collection.load()



searchingChunk = generateRandomEmbedding(1024)
print("--> " + str(searchingChunk))
# Search the collection for vectors that are similar to [1]*128
results = chunk_collection.search(
    data = [searchingChunk], 
    anns_field = "embedding", 
    limit=3, 
    param={
        "metric_type": "L2", 
        "params": {
            "nprobe": 10,
            "topk": 5
            }
        },
    output_fields=["ID_univoco_risorsa", "ID_chunk"]
    )

print("\n\n\n")
print(results)
print(type(results))
print("\n\n\n")


# # # Disconnect from the Milvus service
connections.disconnect("default")


