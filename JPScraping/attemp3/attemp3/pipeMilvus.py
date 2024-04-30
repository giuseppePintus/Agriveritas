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

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


from pymilvus import connections, Collection, utility, FieldSchema, DataType, CollectionSchema

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pymilvus.model.hybrid import BGEM3EmbeddingFunction

import docker

import random
from itertools import chain


class PipeMilvus(PipeInterface):

    logFile = "myLogMilvusPipeline"
    pdLogFile = ""
    # connection = ""
    risorsa_collection : Collection
    chunk_collection : Collection

    bge_m3_ef = BGEM3EmbeddingFunction(
            model_name='BAAI/bge-m3',
            device='cuda',
            use_fp16=True
        )

    def generateRandomEmbedding(self, amount):
        v = [[random.uniform(0.0, 1.0)] * amount]
        return list(chain.from_iterable(v))  # Flatten the 2D list



    def create_collection_resource(self):
        risorsa_schema = CollectionSchema(
            fields=[
                FieldSchema(name="ID_univoco", dtype=DataType.INT64, is_primary=True),
                FieldSchema(name="cod_regione", dtype=DataType.VARCHAR, max_length=2),
                FieldSchema(name="url", dtype=DataType.VARCHAR, max_length=1000),
                FieldSchema(name="HTTP_status", dtype=DataType.INT16),
                FieldSchema(name="hash_code", dtype=DataType.VARCHAR, max_length=64),
                FieldSchema(name="file_name", dtype=DataType.VARCHAR, max_length=100),
                FieldSchema(name="file_dir", dtype=DataType.VARCHAR, max_length=300),
                # FieldSchema(name="original_content", dtype=DataType.BINARY, max_length=1),
                # FieldSchema(name="parsed_content", dtype=DataType.BINARY, max_length=1),
                FieldSchema(name="timestamp_download", dtype=DataType.INT64),
                FieldSchema(name="timestamp_mod_author", dtype=DataType.INT64),
                FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=128)  # Add a vector field
            ],
            description="RISORSA collection"
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

        return risorsa_collection

    def create_collection_chunck(self):
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
        return chunk_collection

    def create_collections(self):
        return [self.create_collection_resource(), self.create_collection_chunck()]

    def open_spider(self, spider):
        super().open_spider(spider)
        connections.connect("default", host="milvus-standalone", port="19530")   #host="milvus-standalone"
        # risorsa_collection, chunk_collection = self.create_collections()
        
        # Drop the existing collections (if any)
        if utility.has_collection("RISORSA"):
            risorsa_collection = Collection("RISORSA")
            risorsa_collection.drop()

        if utility.has_collection("CHUNK"):
            chunk_collection = Collection("CHUNK")
            chunk_collection.drop()


        collections = self.create_collections()
        self.risorsa_collection = collections[0]
        self.chunk_collection = collections[1]

    def close_spider(self, spider):
        #super().close_spider(spider)
        connections.disconnect("default")


    def process_item(self, item : WebDownloadedElement, spider):
        self.log("")
        self.log(" ### INIZIO NUOVO FILE -> " + str(item.tableRow["IDuni"]))
    
        resp = item['response']
        doms = item["domains"]
        tabR = item.tableRow
        settings = item.settingPart

        fName = tabR["file_downloaded_name"]
        eFName = fName.split(".")[-1]
        if (eFName == "html"):
            self.log("Caricando un html!")
            self.manageHTML(tabR)
        else:
            if (eFName == "pdf"):
                self.log("Caricando un pdf!")
                self.managePDF(tabR)
            else:
                self.log("NON riesco a caricarlo!")
        self.log(aCapo=4)
        return item
    
    def manageHTML(self, tabR):
        fName = tabR["file_downloaded_name"][:-4] + "txt"
        filename= os.path.join(tabR["file_downloaded_dir"],fName)

        txtContent = ""
        with open(filename, 'r', encoding="UTF-8") as file:
            txtContent = file.read()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_text(txtContent) #texts = text_splitter.split_documents([txtContent]) #documents

        self.log("## HTML EMBED ########################################################")
        counter = 0
        for d in texts:
            self.log(str(counter))
            counter = counter + 1
            self.log(str(d))

        # finChunks = [t.page_content for t in texts]
        self.embedResult(tabR=tabR, arrayToEmbed=texts)

    def managePDF(self, tabR):
        filename= os.path.join(tabR["file_downloaded_dir"],tabR["file_downloaded_name"])

        # Create array of pages
        loader = PyPDFLoader(filename)
        pages = loader.load_and_split()
        # Check number of pages
        self.log(f"Number of pages in a new array: {len(pages)}")
        self.log(f"Content of 1st page: {pages[0]}")

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

        self.embedResult(tabR, finChunks)

    def embedResult(self, tabR, arrayToEmbed):
        

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
        self.pushingResults(docs_embeddings, tabR)
        # ####################################

    def concat_int_fields(self, ID_univoco_risorsa, ID_chunk):
        return f"{ID_univoco_risorsa}_{ID_chunk}"[:255]

    def pushingResults(self, embeddings, tabR):
        self.log("\n @@@@@@ A @@@@@@ \n")

        # IDuni = scrapy.Field()
        # cod_reg = scrapy.Field()
        # url_from = scrapy.Field()
        # HTTPStatus = scrapy.Field()
        # hash_code = scrapy.Field()
        
        # file_downloaded_name = scrapy.Field()
        # file_downloaded_dir = scrapy.Field()
        # timestamp_download = scrapy.Field()
        # timestamp_mod_author = scrapy.Field()
        
        idRes = tabR["IDuni"]
        cod_regione = tabR["cod_reg"]
        url = tabR["url_from"]
        httpStatus = tabR["HTTPStatus"]
        hashCode = tabR["hash_code"]
        myFilename = tabR["file_downloaded_name"]
        myPath = tabR["file_downloaded_dir"]
        timestamp_download = int(tabR["timestamp_download"])
        timestamp_mod_author = tabR["timestamp_mod_author"]
        if (type(timestamp_mod_author) != type(int)):
            timestamp_mod_author = 0
        else:
            if (timestamp_mod_author < 0):
                timestamp_mod_author = 0
            else:
                timestamp_mod_author = int(timestamp_mod_author)
        

        self.log("\n @@@@@@ B @@@@@@ \n")
        self.log(f"""\n ${idRes} - {type(idRes)}
                    \n ${cod_regione} - {type(cod_regione)}
                    \n ${url} - {type(url)}
                    \n${httpStatus} - {type(httpStatus)}
                    \n${hashCode} - {type(hashCode)}
                    \n${myFilename} - {type(myFilename)}
                    \n${myPath} - {type(myPath)}
                    \n${timestamp_download} - {type(timestamp_download)}
                    \n${timestamp_mod_author} - {type(timestamp_mod_author)}""")


        self.log("\n @@@@@@ C @@@@@@ \n")


        amountPage = 1 #5 
        amountChunck = len(embeddings["dense"]) #5
        for i in range(0,amountPage):
            dataR = [{
                "ID_univoco": idRes,
                "cod_regione": cod_regione,
                "url": url,
                "HTTP_status" : httpStatus,
                "hash_code" : hashCode,
                "file_name" : myFilename,
                "file_dir" : myPath,
                # FieldSchema(name="original_content", dtype=DataType.BINARY, max_length=1),
                # FieldSchema(name="parsed_content", dtype=DataType.BINARY, max_length=1),
                "timestamp_download" : timestamp_download,
                "timestamp_mod_author" : timestamp_mod_author,
                "vector" : self.generateRandomEmbedding(128) # [1.0 * 128.0]  # Add a vector field
            }]
            self.risorsa_collection.insert(dataR)
            for j in range(0, amountChunck):
                dataC = [{
                    "ID" : self.concat_int_fields(idRes,j),
                    "ID_univoco_risorsa" : idRes,
                    "ID_chunk" : j,
                    "embedding" : embeddings["dense"][j] #generateRandomEmbedding(1024)#
                }]
                self.chunk_collection.insert(dataC)

        self.log("\n @@@@@@ F @@@@@@ \n")

        

    def behaviour_skipped(self, item : WebDownloadedElement, spider):
        self.log("Skipped element")

