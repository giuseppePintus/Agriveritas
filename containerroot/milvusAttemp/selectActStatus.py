# # # # https://github.com/LazaUK/AOAI-LangChain-Milvus/blob/main/AOAI_langchain_Milvus.ipynb
import time

from pymilvus import connections, Collection, utility, FieldSchema, DataType, CollectionSchema

connections.connect("default", host="milvus-standalone", port="19530")   #host="milvus-standalone"

# risorsa_schema = CollectionSchema(
#             fields=[
#                 FieldSchema(name="ID_univoco", dtype=DataType.VARCHAR, max_length=16, is_primary=True),
#                 FieldSchema(name="cod_regione", dtype=DataType.VARCHAR, max_length=6),
#                 FieldSchema(name="ID_counter", dtype=DataType.VARCHAR, max_length=9),

#                 FieldSchema(name="url_from", dtype=DataType.VARCHAR, max_length=2000),
#                 FieldSchema(name="HTTP_status", dtype=DataType.INT16),
#                 FieldSchema(name="hash_code", dtype=DataType.VARCHAR, max_length=64),
#                 FieldSchema(name="file_name", dtype=DataType.VARCHAR, max_length=100),
#                 FieldSchema(name="file_dir", dtype=DataType.VARCHAR, max_length=300),
#                 FieldSchema(name="timestamp_download", dtype=DataType.INT64),
#                 FieldSchema(name="timestamp_mod_author", dtype=DataType.INT64),
                
#                 FieldSchema(name="embed_risorsa", dtype=DataType.FLOAT_VECTOR, dim=1024),
#                 FieldSchema(name="is_training", dtype=DataType.BOOL)
#             ],
#             description="RISORSA collection"
#         )

#         # Create the RISORSA collection
#         risorsa_collection = Collection(name="RISORSA", schema=risorsa_schema)

#         # Create an index on the primary key field "ID_univoco"
#         risorsa_collection.create_index(
#             field_name="ID_univoco",
#             index_params={"index_type": "Trie"}
#         )

#         # Create an index on the vector field "embed_risorsa"
#         risorsa_collection.create_index(
#             field_name="embed_risorsa",
#             index_params={"index_type": "FLAT", "metric_type": "L2"}
#         )

#         # Create an index on the "cod_regione" field
#         risorsa_collection.create_index(
#             field_name="cod_regione",
#             index_params={"index_type": "Trie"}
#         )



# def create_collection_chunck(self):
#         chunk_schema = CollectionSchema(
#             fields=[
#                 FieldSchema(name="ID_chunck", dtype=DataType.VARCHAR, max_length=26, is_primary=True),
#                 FieldSchema(name="ID_univoco_risorsa", dtype=DataType.VARCHAR,  max_length=16),
#                 FieldSchema(name="ID_counter", dtype=DataType.VARCHAR, max_length=10),
#                 FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1024),
#                 FieldSchema(name="relative_text", dtype=DataType.VARCHAR, max_length=1200) #un chuck era lungo 1005
#             ],
#             description="CHUNK collection"
#         )

#         # Create the CHUNK collection
#         chunk_collection = Collection(name="CHUNK", schema=chunk_schema)

#         # Create an index on the primary key field "ID_chunk"
#         chunk_collection.create_index(
#             field_name="ID_chunck",
#             index_params={"index_type": "Trie"}
#         )

#         # Create an index on the vector field "embedding"
#         chunk_collection.create_index(
#             field_name="embedding",
#             index_params={"index_type": "IVF_FLAT", "metric_type": "L2", "params": {"nlist": 2048}}
#         )

#         return chunk_collection




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
    limit=5, 
    param={
        "metric_type": "L2", 
        "params": {
            "nprobe": 20,
            },
        "topk": 10
        },
    output_fields=["ID_univoco_risorsa", "ID_counter", "relative_text"]
    )



risposta = ""

print("\n\n\n")
print("Search Results:")
print(type(results))
for hits in results: # GUARDA https://milvus.io/api-reference/pymilvus/v2.4.x/ORM/Collection/search.md
    for index, hit in enumerate(hits):
        print(type(hit))
        print(f"ID: {hit.id}") #.entity['ID_univoco_risorsa']} - {result.entity['ID_counter']}")
        print(f"Distance {hit.score}") 
        # print(f"Vector {hit.vector}") 
        print(f"Relative Text: {hit.get('relative_text')}")
        print("-" * 80)
        risposta = risposta + str(index) + ") " + hit.get('relative_text') + "\n"

print("\n\n\n")





# # # Disconnect from the Milvus service
connections.disconnect("default")

domanda = "METTI QUI LA DOMANDA"

regione = "Emilia Romagna"
initLog = f"""Sei un esperto funzionario della AgEA dell' {regione} e il tuo compito è assistere delle persone che ti pongono delle domande
            Di seguito quindi avrai un quesito e delle possibili risposte che possono risolvere il dubbio
            Domanda: {domanda}
            Possibili risposte: 
            {risposta}
            È di fondamentale importanza che tu risponda in italiano e usando il più possibile il lessico tecnico agronomico
            """
print(initLog)