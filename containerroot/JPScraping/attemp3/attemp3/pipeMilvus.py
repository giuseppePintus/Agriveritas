from pathlib import Path
import os
import scrapy
from scrapy.pipelines.files import FilesPipeline
from attemp3.pipeInterface import PipeInterface
import re
from attemp3.spiders.motherSpider import BaseSpider
from attemp3.items import WebDownloadedElement
import hashlib
import random
from itertools import chain
import json
import time 
import csv

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import numpy as np

from pymilvus import connections, Collection, utility, FieldSchema, DataType, CollectionSchema, MilvusClient

#from langchain_community.document_loaders import PyPDFLoader
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pymilvus.model.hybrid import BGEM3EmbeddingFunction
# from langchain_community.document_loaders
#from transformers import AutoModel; import torch

import docker

import random
from itertools import chain


class PipeMilvus(PipeInterface):

    logFile = "myLogMilvusPipeline"
    pdLogFile = ""
    savedRegion = ""
    
    milvusClient : MilvusClient
    # risorsa_collection : Collection
    # chunk_collection : Collection

    csvFileName = "results"
    file = ""

    bge_m3_ef = BGEM3EmbeddingFunction(
            model_name='BAAI/bge-m3',
            device='cuda', #!ATTENZIONE! The device to use, with cpu for the CPU and cuda:n for the nth GPU device. !ATTENZIONE!
            use_fp16=True
        )

    # embedder = "BAAI/bge-m3"
    # bge_emb = AutoModel.from_pretrained(embedder)
    # bge_tokenizer = AutoTokenizer.from_pretrained(embedder)

    
    resCollectionName = "risorsa"
    chunckCollectionName = "chunk"

    def generateRandomEmbedding(self, amount):
        v = [[random.uniform(0.0, 1.0)] * amount]
        return list(chain.from_iterable(v))  # Flatten the 2D list

    def create_collectionAndPartition_resource(self):
        risorsa_schema = CollectionSchema(
            fields=[
                FieldSchema(name="ID_univoco", dtype=DataType.VARCHAR, max_length=16, 
                            is_primary=True, auto_id=False,
                            description="cod_regione and ID_counter concat to indentify a resource"),
                
                FieldSchema(name="cod_regione", dtype=DataType.VARCHAR, max_length=6,
                            description="reg code ! that field create partitions",
                            is_partition_key = True),
                            
                FieldSchema(name="ID_counter", dtype=DataType.INT32,
                            description="identify a res giving a cod_regione",),

                FieldSchema(name="url_from", dtype=DataType.VARCHAR, max_length=2000,
                            description="map online url to reach that resource online"),

                FieldSchema(name="HTTP_status", dtype=DataType.INT16,
                            description="save if that resource was downloaded successfully"),

                FieldSchema(name="hash_code", dtype=DataType.VARCHAR, max_length=64,
                            description="help to understand if this res is older that actual liked twin"),


                FieldSchema(name="file_name", dtype=DataType.VARCHAR, max_length=100,
                            description="the name of the file that store raw version of the file"),

                FieldSchema(name="file_dir", dtype=DataType.VARCHAR, max_length=300,
                            description="the name of logical position starting by downloaded rout setted away"),

                FieldSchema(name="timestamp_download", dtype=DataType.INT64,
                            description="timestamp on when this resources is downloaded"),

                FieldSchema(name="timestamp_mod_author", dtype=DataType.INT64,
                            description="timestamp on when propretary of website upload this resource"),
                
                FieldSchema(name="embed_risorsa", dtype=DataType.FLOAT_VECTOR, dim=1024,
                            description="each collection have to save at least one vector. So this is embedding of all resources"),

                FieldSchema(name="is_training", dtype=DataType.BOOL,
                            description="using this resource eventually to make some training of any model? save a result of a predicate"),
                
                FieldSchema(name="fined_text", dtype=DataType.JSON,
                            description="JSON file with a single field: fined_text")
            ],
            description="RISORSA collection",
            partition_key_field = "cod_regione"
        )

        # Create the RISORSA collection
        #risorsa_collection = Collection(name="RISORSA", schema=risorsa_schema)

        index_params = MilvusClient.prepare_index_params()

        index_params.add_index(
            field_name="ID_univoco", # Name of the scalar field to be indexed
            index_type="Trie", # Type of index to be created
            index_name="ID_univoco_index" # Name of the index to be created
        )
        # # Create an index on the primary key field "ID_univoco"
        # risorsa_collection.create_index(
        #     field_name="ID_univoco",
        #     index_params={"index_type": "Trie"}
        # )

        # 4.2. Add an index on the vector field.
        index_params.add_index(
            field_name="embed_risorsa",
            metric_type="COSINE",
            index_type="IVF_FLAT",
            index_name="embed_risorsa_index",
            params={"nlist": 1024}
        )

        # # Create an index on the vector field "embed_risorsa"
        # risorsa_collection.create_index(
        #     field_name="embed_risorsa",
        #     index_params={
        #         "index_type": "FLAT", 
        #         "metric_type": "COSINE"
        #         }
        # )

        index_params.add_index(
            field_name="cod_regione", # Name of the scalar field to be indexed
            index_type="Trie", # Type of index to be created
            index_name="cod_regione_index" # Name of the index to be created
        )
        # # Create an index on the "cod_regione" field
        # risorsa_collection.create_index(
        #     field_name="cod_regione",
        #     index_params={"index_type": "Trie"}
        # )


        my_collection_name = self.resCollectionName #"RISORSA"

        # 4.3. Create an index file
        self.milvusClient.create_collection(
            collection_name = my_collection_name, # "RISORSA",#str,
            #dimension: int, ### ignorato avendo uno scheme
            #primary_field_name: str = "id", ### ignorato avendo uno scheme
            #id_type: str = DataType, ### ignorato avendo uno scheme
            #vector_field_name: str = "vector", ### ignorato avendo uno scheme
            #metric_type: str = "COSINE", ### ignorato avendo uno scheme
            #auto_id: bool = False, ### ignorato avendo uno scheme
            #timeout: Optional[float] = None, ### non mi interessa fissare un timer
            schema = risorsa_schema,    #: Optional[CollectionSchema] = None,
            index_params = index_params   #Optional[IndexParams] = None,
            ### **kwargs,
        )


        toRet = self.milvusClient.has_collection(
            collection_name = my_collection_name,
        )

        return toRet

    def create_collectionAndPartition_chunck(self):
        chunk_schema = CollectionSchema(
            fields=[
                FieldSchema(name="ID_chunck", dtype=DataType.VARCHAR, max_length=26, 
                            is_primary=True, auto_id=False,
                            description="cod_regione and ID_counter concat to indentify a resource"),

                FieldSchema(name="ID_univoco_risorsa", dtype=DataType.VARCHAR,  max_length=16,
                            description="Foreing Key of \"RISORSA\" collection"),
                
                #FieldSchema(name="ID_counter", dtype=DataType.VARCHAR, max_length=10),                
                FieldSchema(name="ID_counter", dtype=DataType.INT32,
                            description="index of a chunk by a resource"),

                FieldSchema(name="cod_regione", dtype=DataType.VARCHAR, max_length=6,
                            description="reg code ! that field create partitions",
                            is_partition_key = True),
                
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1024,
                            description="embedding of chunked text"), #un chuck era lungo 1005),
                
                FieldSchema(name="relative_text", dtype=DataType.VARCHAR, max_length=1200,
                            description="raw transcription of embedded text") #un chuck era lungo 1005

            ],
            description="CHUNK collection"
        )

        index_params = MilvusClient.prepare_index_params() #index_params = self.milvusClient.create_index_params() #  Prepare an IndexParams object
        # Create the CHUNK collection
        #chunk_collection = Collection(name="CHUNK", schema=chunk_schema)

        index_params.add_index(
            field_name="ID_chunck", # Name of the scalar field to be indexed
            index_type="Trie", # Type of index to be created
            index_name="ID_chunck_index" # Name of the index to be created
        )

        # # Create an index on the primary key field "ID_chunk"
        # chunk_collection.create_index(
        #     field_name="ID_chunck",
        #     index_params={"index_type": "Trie"}
        # )

        index_params.add_index(
                    field_name="embedding", # Name of the scalar field to be indexed
                    metric_type="COSINE",
                    index_type="IVF_FLAT",
                    index_name="embedding_index",
                    params={"nlist": 1024}
                )

        # Create an index on the vector field "embedding"
        # chunk_collection.create_index(
        #     field_name="embedding",
        #     index_params={"index_type": "IVF_FLAT", "metric_type": "L2", "params": {"nlist": 2048}}
        # )
        # --> "params": {"nlist": 2048}} <-- potrebbe essere interessante gestire questo parametro?



        self.milvusClient.create_collection(
            collection_name = self.chunckCollectionName, # "RISORSA",#str,
            #dimension: int, ### ignorato avendo uno scheme
            #primary_field_name: str = "id", ### ignorato avendo uno scheme
            #id_type: str = DataType, ### ignorato avendo uno scheme
            #vector_field_name: str = "vector", ### ignorato avendo uno scheme
            #metric_type: str = "COSINE", ### ignorato avendo uno scheme
            #auto_id: bool = False, ### ignorato avendo uno scheme
            #timeout: Optional[float] = None, ### non mi interessa fissare un timer
            schema = chunk_schema,    #: Optional[CollectionSchema] = None,
            index_params = index_params   #Optional[IndexParams] = None,
            ### **kwargs,
        )

        toRet = self.milvusClient.has_collection(
            collection_name = self.chunckCollectionName,
        )

        return toRet


        # return chunk_collection

    # def create_collections(self):
    #     return [self.create_collectionAndPartition_resource(), self.create_collectionAndPartition_chunck()]

    def open_spider(self, spider):
        super().open_spider(spider)
        
        self.milvusClient = MilvusClient(uri="http://milvus-standalone:19530")
        #self.milvusClient = MilvusClient(uri="http://localhost:19530")
        # connections.connect("default", host="milvus-standalone", port="19530")   #host="milvus-standalone"
        region = spider.code_region
        self.savedRegion = region
        

        existRis = self.milvusClient.has_collection(
            collection_name = self.resCollectionName,
        )
        existChunck = self.milvusClient.has_collection(
            collection_name = self.chunckCollectionName,
        )

        if not existRis:
            self.create_collectionAndPartition_resource()
        if not existChunck:
            self.create_collectionAndPartition_chunck()

        # Drop the existing collections (if any)
        res = self.milvusClient.has_partition(
            collection_name = self.resCollectionName,
            partition_name=region
        )

        if res:
            self.milvusClient.release_partitions(collection_name = self.resCollectionName, partition_names=[region] )
            self.milvusClient.release_partitions(collection_name = self.chunckCollectionName, partition_names=[region])

            #query per eliminare tutti i chuck
            self.milvusClient.drop_partition(
                collection_name = self.chunckCollectionName,
                partition_name = region
            )

            self.milvusClient.drop_partition(
                collection_name = self.resCollectionName,
                partition_name = region
            )
        
        # 7. Load the collection
        self.milvusClient.load_collection(
            collection_name=self.resCollectionName,
            replica_number=1 # Number of replicas to create on query nodes. Max value is 1 for Milvus Standalone, and no greater than `queryNode.replicas` for Milvus Cluster.
        )

        res = self.milvusClient.get_load_state(
            collection_name=self.resCollectionName,
        )

        self.log(f"CARICATO RES: {str(res)}" )

         # 7. Load the collection
        self.milvusClient.load_collection(
            collection_name=self.chunckCollectionName,
            replica_number=1 # Number of replicas to create on query nodes. Max value is 1 for Milvus Standalone, and no greater than `queryNode.replicas` for Milvus Cluster.
        )

        res = self.milvusClient.get_load_state(
            collection_name=self.chunckCollectionName
        )

        self.log(f"CARICATO CHUCK: {str(res)}" )

        a = time.time()
        self.csvFileName += f"_{time.strftime('%m_%d_%H_%M', time.gmtime(a))}_{spider.code_region}_CHUNK.csv"
        
        self.file = open(self.csvFileName, 'w', newline='')
        self.exporter = csv.DictWriter(self.file, fieldnames=[
            'raw_text', 'embedding'
        ])
        self.exporter.writeheader()  # <--- Print the header


        # collections = self.create_collections()
        # self.risorsa_collection = collections[0]
        # self.chunk_collection = collections[1]

    def close_spider(self, spider):
        self.log("FINE")
        self.milvusClient.release_partitions(collection_name = self.resCollectionName, partition_names=[self.savedRegion] )
        self.milvusClient.release_partitions(collection_name = self.chunckCollectionName, partition_names=[self.savedRegion])
        self.exporter.finish_exporting()
        self.file.close()
        #self.milvusClient.closeConn... non c'è niente del genere?

    def process_item(self, item : WebDownloadedElement, spider):
        self.log("")
        self.log(" ### INIZIO NUOVO FILE -> " + str(item.tableRow["ID_univoco"]))
    
        resp = item['response']
        doms = item["domains"]
        tabR = item.tableRow
        settings = item.settingPart

        fName = tabR["file_downloaded_name"]
        extentionFName = fName.split(".")[-1]
        if (extentionFName == "html"):
            self.log("Caricando un html!")
            self.manageHTML(tabR)
        else:
            if (extentionFName == "pdf"):
                self.log("Caricando un pdf!")
                self.managePDF(tabR)
            else:
                self.log(f"NON riesco a caricarlo! -> {tabR['file_downloaded_name']} / {tabR['url_from']}")
        self.log(aCapo=4)
        return item
    
    def manageHTML(self, tabR):
        fName = tabR["file_downloaded_name"][:-4] + "txt"
        filename= os.path.join(tabR["file_downloaded_dir"],fName)

        txtContent = ""
        with open(filename, 'r', encoding="UTF-8") as file:
            txtContent = file.read()

        try:
            tabR["embed_risorsa"] = self.bge_m3_ef.encode_documents([txtContent])['dense'][0]
        except:
            tabR["embed_risorsa"] = self.generateRandomEmbedding(1024)

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_text(txtContent) #texts = text_splitter.split_documents([txtContent]) #documents

        self.log("## HTML EMBED ########################################################")
        counter = 0
        for d in texts:
            self.log(str(counter))
            counter = counter + 1
            self.log(str(d))

        # finChunks = [t.page_content for t in texts]
        self.embedResult(tabR=tabR, arrayToEmbed=texts, fileContent=txtContent)

    def managePDF(self, tabR):
        filename= os.path.join(tabR["file_downloaded_dir"],tabR["file_downloaded_name"])

        # Create array of pages
        loader = PyPDFLoader(filename)
        pages = loader.load_and_split()
        # Check number of pages
        self.log(f"Number of pages in a new array: {len(pages)}")
        self.log(f"Content of 1st page: {pages[0]}")

        all_text = ""
        for page_text in pages:
            all_text += page_text.page_content
        
        try:
            tabR["embed_risorsa"] = self.bge_m3_ef.encode_documents([all_text])['dense'][0]
        except:
            tabR["embed_risorsa"] = self.generateRandomEmbedding(1024)



        #splitting the text into
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(pages) #documents

        self.log("##########################################################")
        counter = 0
        for d in texts:
            self.log(f"{counter}", aCapo=1)
            counter = counter + 1
            self.log(str(d.page_content))

        finChunks = [t.page_content for t in texts]

        self.embedResult(tabR, finChunks, fileContent=all_text)

    def embedResult(self, tabR, arrayToEmbed, fileContent):
        
        docs_embeddings = self.bge_m3_ef.encode_documents(arrayToEmbed)
        
        # self.log("Embeddings:", docs_embeddings)
        # self.log("Dense document dim:", bge_m3_ef.dim["dense"], docs_embeddings["dense"][0].shape)

        self.log("\n\n\n")
        # # print(pe(finChunks))
        # print(docs_embeddings.keys())
        # print(len(docs_embeddings["dense"]))
        # # print(len(docs_embeddings["sparse"]))
        self.log("embed da caricare: " + str(len(arrayToEmbed)))
        # print(len(docs_embeddings["dense"]))

        self.log("\n\n\n\n\n\n\n\n\n\n\n\n")
        self.pushingResults(docs_embeddings, tabR, arrayToEmbed, allFileText=fileContent)
        # ####################################

    # def concat_int_fields(self, ID_univoco_risorsa, ID_chunck):
    #     return f"{ID_univoco_risorsa}_{ID_chunck}"[:255]

    def pushingResults(self, embeddings, tabR, arrayToEmbed, allFileText):
        self.log("\n @@@@@@ A @@@@@@ \n")


        ### motherSpider ### ID_univoco = scrapy.Field()
        ### ragnoFiglio ### cod_reg = scrapy.Field()
        ### motherSpider ### ID_counter = scrapy.Field()
        ### motherSpider ### url_from = scrapy.Field()
        ### motherSpider ### HTTP_status = scrapy.Field()
        ### motherSpider ### hash_code = scrapy.Field()
        
        ### downloadPipe ### file_downloaded_name = scrapy.Field()
        ### downloadPipe ### file_downloaded_dir = scrapy.Field()
        ### motherSpider ### timestamp_download = scrapy.Field()
        ### downloadPipe ###timestamp_mod_author = scrapy.Field()

        ### qui ###embed_risorsa = scrapy.Field()
        ### motherSpider ### is_training = scrapy.Field()
        
        ID_univoco = tabR["ID_univoco"]
        cod_regione = tabR["cod_reg"]
        ID_counter = int(tabR["ID_counter"])
        url_from = tabR["url_from"]
        HTTP_status = tabR["HTTP_status"]
        hashCode = tabR["hash_code"]

        myFilename = tabR["file_downloaded_name"]
        myPath = tabR["file_downloaded_dir"]
        timestamp_download = int(tabR["timestamp_download"])
        timestamp_mod_author = tabR["timestamp_mod_author"]

        embed_risorsa = [a for a in tabR["embed_risorsa"]]
        is_training = tabR["is_training"]

        fined_text = json.dumps({"fined_text": allFileText[:10000]})


        if (type(timestamp_mod_author) != type(int)):
            timestamp_mod_author = 0
        else:
            if (timestamp_mod_author < 0):
                timestamp_mod_author = 0
            else:
                timestamp_mod_author = int(timestamp_mod_author)
        
        self.log("\n @@@@@@ B @@@@@@ \n")
        self.log(f"""\n $ ID_univoco = {ID_univoco} - {type(ID_univoco)}
                    \n $ cod_reg = {cod_regione} - {type(cod_regione)}   
                    \n $ ID_counter = {ID_counter} - {type(ID_counter)}
                    \n $ url_from = {url_from} - {type(url_from)}
                    \n $ HTTP_status = {HTTP_status} - {type(HTTP_status)}
                    \n $ hashCode = {hashCode} - {type(hashCode)}

                    \n $ file_name = {myFilename} - {type(myFilename)}
                    \n $ file_dir = {myPath} - {type(myPath)}
                    \n $ timestamp_download = {timestamp_download} - {type(timestamp_download)}
                    \n $ timestamp_mod_author = {timestamp_mod_author} - {type(timestamp_mod_author)}

                    \n $ embed_risorsa = {embed_risorsa} - {len(embed_risorsa)} - {type(embed_risorsa)}
                    \n $ is_training = {is_training} - {type(is_training)}

                    \n $ fined_text [eventually truncked] = {str(fined_text)} - {type(fined_text)} """)


        self.log("\n @@@@@@ C @@@@@@ \n")


        amountPage = 1 #5 
        amountChunck = len(embeddings["dense"]) #5


        warning = ("faq" in allFileText) or ("domande frequenti" in allFileText)

        for i in range(0, amountPage):
            dataR = [{
                "ID_univoco": ID_univoco,
                "cod_regione": cod_regione,
                "ID_counter": ID_counter,
                "url_from": url_from,
                "HTTP_status" : HTTP_status,
                "hash_code" : hashCode,

                "file_name" : myFilename,
                "file_dir" : myPath,
                # FieldSchema(name="original_content", dtype=DataType.BINARY, max_length=1),
                # FieldSchema(name="parsed_content", dtype=DataType.BINARY, max_length=1),
                "timestamp_download" : timestamp_download,
                "timestamp_mod_author" : timestamp_mod_author,
                
                "embed_risorsa" : embed_risorsa, #self.generateRandomEmbedding(1024),
                "is_training" : is_training,

                "fined_text" : fined_text
            }]

            self.log("Data to be inserted:")
            self.log(str(dataR))

            a = self.milvusClient.insert(
                collection_name = self.resCollectionName,
                #partition_name = cod_regione,
                data = dataR,
            )
            self.log(f"RES RES: {str(a)}")
            #self.risorsa_collection.insert(dataR)

            for j in range(0, amountChunck):
                ID_chunck = f"{ID_univoco}_{j}"
                ID_univoco_risorsa = ID_univoco
                ID_counter = j
                
                embedding = np.asarray(embeddings["dense"][j], dtype=np.float32)#embeddings["dense"][j] #[j]["dense"], #generateRandomEmbedding(1024)#
                relative_text = arrayToEmbed[j] 

                self.log(f"""
                    \n $ID_chunck -> {ID_chunck} - {type(ID_chunck)}
                    \n $ID_univoco_risorsa -> {ID_univoco_risorsa} - {type(ID_univoco_risorsa)}
                    \n $ID_counter -> {ID_counter} - {type(ID_counter)}
                    \n $embedding -> {len(embedding)} - {embedding} - {type(embedding)}
                    \n $relative_text -> {relative_text} - {type(relative_text)}
                    """)
                
                dataC = [{
                    "ID_chunck" : ID_chunck,
                    "ID_univoco_risorsa" : ID_univoco_risorsa,
                    "ID_counter" : ID_counter,
                    "cod_regione" : cod_regione,
                    "embedding" : embedding,
                    "relative_text" : relative_text
                    # FieldSchema(name="ID_chunck", dtype=DataType.VARCHAR, max_length=26, is_primary=True),
                    # FieldSchema(name="ID_univoco_risorsa", dtype=DataType.VARCHAR,  max_length=16),
                    # FieldSchema(name="ID_counter", dtype=DataType.VARCHAR, max_length=10),
                    # FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1024),
                    # FieldSchema(name="relative_text", dtype=DataType.VARCHAR, max_length=1000)  
                }]

                if warning :
                    row = {
                        'raw_text' : relative_text,
                        'embedding' : embedding
                    }
                    self.exporter.writerow(row)

                #self.chunk_collection.insert(dataC)
                b = self.milvusClient.insert(
                    collection_name = self.chunckCollectionName,
                #    partition_name = cod_regione,
                    data = dataC,
                )
                self.log(f"RES CHUCK {j}: {str(b)}")

        self.log("\n @@@@@@ F @@@@@@ \n")

        

    def behaviour_skipped(self, item : WebDownloadedElement, spider):
        self.log("Skipped element")

