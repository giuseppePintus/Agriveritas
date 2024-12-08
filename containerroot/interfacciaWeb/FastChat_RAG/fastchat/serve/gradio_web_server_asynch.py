"""
The gradio demo server for chatting with a single model.
"""

import argparse
from collections import defaultdict
import datetime
import hashlib
import json
import os
import random
import time
import uuid
import markdown

import gradio as gr
import requests

# Constanst (e.g. log file)
from fastchat.constants import (
    LOGDIR,
    WORKER_API_TIMEOUT,
    ErrorCode,
    MODERATION_MSG,
    CONVERSATION_LIMIT_MSG,
    RATE_LIMIT_MSG,
    SERVER_ERROR_MSG,
    INPUT_CHAR_LEN_LIMIT,
    CONVERSATION_TURN_LIMIT,
    SESSION_EXPIRATION_TIME,
)
# Chat template for models
from fastchat.model.model_adapter import (
    get_conversation_template,
)

# CSS style
from style.css.general_css import block_css

# infos about each model (e.g. link to github repo)
from fastchat.model.model_registry import get_model_info, model_info
# for logging data to remote machin
from fastchat.serve.remote_logger import get_remote_logger

# general utils
from fastchat.utils import (
    build_logger,
    get_window_url_params_js,
    get_window_url_params_with_tos_js,
    moderation_filter,
    parse_gradio_auth_creds,
)



# >> Templates for RAG cards
from jinja2 import Environment, FileSystemLoader
# Set up the template environment with the templates directory
env = Environment(loader=FileSystemLoader('style/templates'))
context_html_template = env.get_template('fancy_context_html_template.j2')
# Configurations for the RAG architecture
logger = build_logger("gradio_web_server", "logs/ui/gradio_web_server.log")



# --------------------------------------------------
# >> RETRIEVAL
# >>> LangChain
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import Milvus
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from milvus import default_server
from pymilvus import connections, utility, Collection

from FlagEmbedding import FlagReranker

global_query = ""
global_context = ""
reranker_model = None
reranked_documents = []

import numpy as np
from fastchat.rag_constants import *

usr_template = """
Informazioni e Articoli di riferimento:
-------------------
{context}
-------------------

Rispondi ora alla seguente domanda:
{question}
"""

'''
format_src_data = """
**********
Articolo: {art_tile}
Fonte: {src}
Anno: {year}

{txt}
**********
"""
'''

#Link riferimento: {ref_link}
agriveritas_format_src_data = """
**********
Fonte: {src}

{txt}
**********
"""

'''
examples = [
    "Quali sono le implicazioni pratiche della scelta tra affidamento diretto e procedura negoziata senza bando per lavori di importo inferiore a 1 milione di euro?",
    "Come si possono individuare e selezionare gli operatori economici per le procedure negoziate senza bando previste dall'articolo 50, in modo da garantire la massima trasparenza e correttezza?",
    "In quali casi il progettista può formulare prezzi aggiuntivi rispetto a quelli contemplati nel prezzario di riferimento?",
    "Quali documenti deve trasmettere l'affidatario alla stazione appaltante almeno venti giorni prima della data di effettivo inizio dell'esecuzione delle prestazioni in subappalto?",
    "Qual è l'obiettivo dell'attività di rilevazione dei costi dei singoli prodotti e delle attrezzature e come viene ottenuto il valore rappresentativo del prezzo finale?",
    "In quali casi l'ANAC trasmette gli atti e i propri rilievi agli organi di controllo e alle Procure della Repubblica?",
    "Quali elementi deve contenere la proposta presentata dagli operatori economici agli enti concedenti per la realizzazione in concessione di lavori o servizi?",
    "Con quale provvedimento e da parte di quali soggetti possono essere individuate eventuali ulteriori categorie di indici o specificazioni tipologiche o merceologiche rispetto a quelle previste dal codice?",
    "Come devono essere definiti nei documenti di gara il regime applicabile ai diritti di proprietà intellettuale e il trattamento delle informazioni riservate nel caso di partenariato per l'innovazione con più operatori economici?",
    "Quali indicazioni deve contenere il bando di gara riguardo alla società di scopo da costituire per l'affidamento di una concessione nella forma della finanza di progetto?",
    "In quale fase del processo di progettazione deve essere redatto e approvato il documento di indirizzo alla progettazione (DIP) e quali sono le differenze tra il caso di progettazione interna ed esterna alla stazione appaltante?",
    "Come procede la stazione appaltante per verificare le dichiarazioni sostitutive degli operatori economici sul possesso dei requisiti?",
	"Nel caso in cui si debba procedere ad attività espropriative sulla base del progetto di fattibilità tecnica ed economica,con quali documenti deve essere integrato il progetto stesso?",
	"Quali operatori economici possono essere selezionati come offerenti in una procedura ristretta o come partecipanti in una procedura negoziata quando è indetta una gara con un avviso sull'esistenza di un sistema di qualificazione?",
	"Come procede la stazione appaltante per verificare le dichiarazioni sostitutive degli operatori economici sul possesso dei requisiti?"
]
'''

name_to_model_dict = {
    "AgriVeritas-AI-PRO" : "Meta-Llama-3-8B-Instruct",
    "AgriVeritas-AI-Junior" : "gemma-2b-it"
}

model_to_name_dict = {
    "Meta-Llama-3-8B-Instruct" : "AgriVeritas-AI-PRO",
    "gemma-2b-it" : "AgriVeritas-AI-Junior"
}


region_to_code = {
    "Emilia Romagna - solo risorse PSR" : "ER1PSR",
    "Veneto" : "V"
}

code_to_region = {
    "ER1PSR" : "Emilia Romagna - solo risorse PSR",
    "V" : "Veneto"
}



# Encoder commont to everybody
# TODO: make access parallels using a controller
logger.info("Loading retrieval models")
embedder = HuggingFaceEmbeddings(model_name=EMBED_NAME, model_kwargs={"device" : ENCODER_DEVICE})
reranker_model = FlagReranker(RERANKER_NAME, use_fp16=True, device=RANKER_DEVICE)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP,separators=["\n\n"," ",".",","])


'''
# > init connection
logger.info("Establishing connection with Milvus DB")
try:
    connections.connect("default", host="0.0.0.0")
except:
    logger.info("Starting the server at 0.0.0.0")
    default_server.start()
    connections.connect("default", host="0.0.0.0")

collection = Collection("CodiceAppalti2023")
logger.info(f'collection: {collection.name} has {collection.num_entities} entities')
'''

# # # # from langchain_community.vectorstores import Milvus
# # # # from pymilvus import connections, Collection  # Import necessary Milvus components

# # # # connections.connect(**{"host": "milvus-standalone", "port": "19530"})

# # # # collection_name = "newChunk"

# # # # if Collection(collection_name).exists():
# # # #     print(f"Connecting to existing collection: {collection_name}")
# # # # else:
# # # #     print(f"Creating new collection: {collection_name}")

# # # # vector_db = Milvus(
# # # #     embedder,
# # # #     connection_args={"host": "milvus-standalone", "port": "19530"},
# # # #     collection_name=collection_name,
# # # #     # auto_id=True, 
# # # # )

# # from pymilvus import connections, Collection, MilvusException

# # connections.connect(**{"host": "milvus-standalone", "port": "19530"})
# # collection_name = "newChunk"

# # try:
# #     # Attempt to load the collection
# #     Collection(collection_name).load()
# #     print(f"Connecting to existing collection: {collection_name}")
# # except MilvusException:
# #     print(f"Creating new collection: {collection_name}")
# #     # ... your logic for creating a new collection ... 

# # vector_db = Milvus(
# #     embedder,
# #     connection_args={"host": "milvus-standalone", "port": "19530"},
# #     collection_name=collection_name,
# #     # auto_id=True, 
# # )

#chunkCollectionName = "newRisorsa"
risorsaCollectionName = "risorsa"
from pymilvus import connections, Collection, utility, FieldSchema, DataType, CollectionSchema, MilvusClient
milvusClient = MilvusClient(uri="http://milvus-standalone:19530")

milvusClient.load_collection(
    collection_name= risorsaCollectionName, # self.resCollectionName,
    #replica_number=1 # Number of replicas to create on query nodes. Max value is 1 for Milvus Standalone, and no greater than `queryNode.replicas` for Milvus Cluster.
)

res = milvusClient.get_load_state(
    collection_name=risorsaCollectionName,#resCollectionName,
)

logger.info(f"CARICATO RISORSA: {str(res)}")

# > handler methods
def format_docs(docs):
    logger.info(f"JP1: format_docs")
    logger.info(f"JP5: {docs}")
    ctx = []
    for d in docs:
        txt = d.page_content
        meta = d.metadata
        this_src = agriveritas_format_src_data.format(
                                        #art_tile=meta['art_title'], 
                                        src=meta['ID_chunck'],
                                          
                                        #year=meta['year'], 
                                        txt=txt)
        ctx.append(this_src)

    return "\n".join(ctx)


def rerank_docs(docs, global_query):
    logger.info(f"JP1: rerank_docs")
    logger.info(f" --> {MIN_DOCS_TO_SHOW} <--")
    #global global_query
    global reranker_model
    logger.info(f" --> {str(docs)} <--")

    pairs = [(global_query, d.page_content) for d in docs]
    scores = reranker_model.compute_score(pairs)
    logger.info(f" --> {MIN_DOCS_TO_SHOW} <--")
    permutation = np.argsort(scores)[::-1]
    logger.info(f" --> {MIN_DOCS_TO_SHOW} <--")
    ranked_docs = [docs[i] for i in permutation]
    ranked_scores = [scores[i] for i in permutation]
    
    # Filter docs by score
    #filtered_docs = [doc for doc, score in zip(ranked_docs, ranked_scores) if score >= MIN_SHOW_SIM_SCORE and len(doc.page_content) >= MIN_CHUNK_LEN_THRESHOLD]
    filtered_docs = [doc for doc, score in zip(ranked_docs, ranked_scores) if len(doc.page_content) >= MIN_CHUNK_LEN_THRESHOLD]

    # Ensure at least MIN_DOCS_TO_SHOW are present
    n_filtered = len(filtered_docs)
    logger.info(f" --> {MIN_DOCS_TO_SHOW} <--")
    if n_filtered < MIN_DOCS_TO_SHOW:
        for j in range(MIN_DOCS_TO_SHOW - n_filtered):
            filtered_docs.append(ranked_docs[n_filtered+j])
    
    # Limit to TOP_K_RERANK
    filtered_docs = filtered_docs[:TOP_K_RERANK]
    
    return filtered_docs


def process_docs(docs, query):
    logger.info(f"JP1: process_docs")
    #global reranked_documents
    docs = rerank_docs(docs, query)
    #reranked_documents = docs

    return format_docs(docs), docs


def handle_parsing(file_name):
    logger.info(f"JP1: handle_parsing")
    # Check type
    if '.pdf' in file_name:
        logger.info("Parsing PDF")
        loader = PyPDFLoader(file_name)
        pages = loader.load_and_split()
        data = "\n".join([p.page_content for p in pages])
    elif '.docx' in file_name:
        logger.info("Parsing Word Document")
        loader = Docx2txtLoader(file_name)
        pages = loader.load()
        data = "\n".join([p.page_content for p in pages])
    else:
        # .txt
        with open(file_name, 'r') as f_in:
            data = f_in.read()

    return data

class ResPayload():
    def __init__(self, id_res, title, href):
        self.id_res = id_res
        self.title = title
        self.href = href
    

dummy_cache_link = {}
def by_code_to_payload(id_res): 
    to_ret = ResPayload("","","")

    if id_res not in dummy_cache_link:
        tmpRes = milvusClient.get(
                    collection_name=risorsaCollectionName,
                    ids=[f"{id_res}"]
                )
        logger.info(f"JP7 : {str(tmpRes[0])}")
        to_ret = ResPayload(
            id_res = id_res, 
            title = tmpRes[0]["file_name"], 
            href = tmpRes[0]["url_from"])
        dummy_cache_link[id_res] = to_ret
    else:
        to_ret = dummy_cache_link[id_res]
    
    #logger.info(f"{id_res}")
    return to_ret


def format_docs_for_cards(doc):

    logger.info(f"JP1: format_docs_for_cards")

    txt = doc.page_content
    metadata = doc.metadata

    logger.info(metadata['ID_chunck'])
    logger.info(f"JP6: {doc}")
    #whole_article = ""#handle_parsing(metadata["ID_chunck"])#metadata['file_name'])

    # if metadata['source'] == 'Codice Appalti D.Lgs. 36/2023':
    #     # Remove titles and go directly to the first comma
    #     comma_separators = ['\n1.', ' 1.']
    #     for cs in comma_separators:
    #         if cs in whole_article:
    #             whole_article = '1. ' + whole_article.split(cs, 1)[1].strip()

    #         if cs in txt:
    #             txt = '1. ' + txt.split(cs, 1)[1].strip()
        
    #txt = whole_article.replace(txt, f'<span>{txt}</span>')

    logger.info("Parsed retrieved articles for cards")
    
    more_info = by_code_to_payload(metadata["ID_univoco_risorsa"])
    # title=metadata['art_title']
    # if ')' in title:
    #     title = title.split(')',1)[0]+')'

    out = {
        'source' : more_info.href,
        'title' : f"{more_info.title}", #f"{more_info.title} {more_info.id_res}"
        # 'year' : metadata['year'],
        # 'title' : title,
        'content' : txt
    }

    return out


def unify_chunks_from_same_doc(docs):
    """
    Unify chunk selection if they come from the same source document
    """
    logger.info(f"JP1: unify_chunks_from_same_doc")
    logger.info(f"JP1: docs -> {docs}")
    unified_docs = {}

    for doc in docs:
        source = doc['source']
        if source not in unified_docs:
            unified_docs[source] = doc
        else:
            # Combine the highlighted text while keeping the spans separate
            current_content = unified_docs[source]['content']
            if "<span>" in doc['content']:
                new_content = doc['content'].split("<span>")[1].split("</span>")[0].strip()
            else:
                new_content = doc['content'].strip()
            combined_content = current_content.replace(new_content, f"<span>{new_content}</span>")

            unified_docs[source]['content'] = combined_content
    
    for src in unified_docs:
        ctx = unified_docs[src]['content']
        if "<span>" not in ctx:
            unified_docs[src]['content'] = f"<span>{ctx}</span>"

    list_of_docs = list(unified_docs.values())

    return list_of_docs


def retrieve_documents(state, question):
    """
    Return the prompt with the question and supporting facts
    """
    logger.info(f"JP1: retrieve_documents")
    gr.Info("Ricerco informazioni utili nella giurisprudenza")
    logger.info(f"JP2: {question}")
    input_prompt, reranked_docs = state.invoke_chain(question)
    context_augmented_prompt = input_prompt.messages[0].content

    return context_augmented_prompt, reranked_docs


# --------------------------------------------------

class State:
    """
    Handler class for customizing configurations according to the chosen model.
    """
    def __init__(self, 
                 model_name,
                 is_vision = False):

        # [CHANGE MODEL NAME]
        model_name = name_to_model_dict[model_name]

        self.conv = get_conversation_template(model_name)
        self.conv_wo_context = get_conversation_template(model_name)
        self.conv_id = uuid.uuid4().hex
        self.skip_next = False
        self.model_name = model_name
        self.oai_thread_id = None
        self.is_vision = is_vision

        self.reranked_docs = []

        self.regen_support = True
        if "browsing" in model_name:
            self.regen_support = False
        self.init_system_prompt(self.conv)


        # > define rag pipeline
        logger.info("Initializing Vector DB and Retrieval system")
        self.prompt = ChatPromptTemplate.from_template(usr_template)
        logger.info("Initializing Milvus")
        self.vector_db = Milvus(
            embedder,
            connection_args={"host": "milvus-standalone", "port": "19530"},
            collection_name="newChunk",#CodiceAppalti2023",
            vector_field="embedding",
            text_field="relative_text"
            #auto_id=True,
        )
        self.retriever = self.vector_db.as_retriever(search_kwargs={"k": TOP_K_RANK})
        logger.info(f"Done initilaization retriever --> {self.vector_db}")
        self.chain = None
    
    def invoke_chain(self, question):
        """
        Build a chain and invoke it:
        - retrieval of contexts based on question
        - 
        """
        logger.info(f"JP1: STATE.invoke_chain")
        logger.info("Invoking chain for retrieval")

        def reranker_fun(x):
            logger.info(f"JP3: {str(x)} - {x}")
            #global _reranked_docs
            formatted_doc, _rd = process_docs(x,question)
            self._reranked_docs=_rd
            logger.info(f">> INNER: {len(self._reranked_docs)}")
            return formatted_doc
        
        base_chain = {"context": self.retriever | reranker_fun, "question": RunnablePassthrough()}
        
        chain = (
            base_chain
            | self.prompt
        ) 
        logger.info(f"JP4: question -> {question}")
        out = chain.invoke(question)
        logger.info(f"OUTER: {len(self._reranked_docs)}")

        return out, self._reranked_docs
    
    def reinit_retriever(self, user_iid):
        """
        When adding new documents to DB
        """
        logger.info(f"JP1: STATE.reinit_retriever")
        pass

    def init_system_prompt(self, conv):
        """
        Initialize the system prompt
        """
        logger.info(f"JP1: STATE.init_system_prompt")
        system_prompt = conv.get_system_message()
        if len(system_prompt) == 0:
            return
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        system_prompt = system_prompt.replace("{{currentDateTime}}", current_date)
        conv.set_system_message(system_prompt)

    def to_gradio_chatbot(self):
        logger.info(f"JP1: STATE.to_gradio_chatbot")
        return self.conv.to_gradio_chatbot()

    def to_gradio_chatbot_wo_context(self):
        logger.info(f"JP1: STATE.to_gradio_chatbot_wo_context")
        return self.conv_wo_context.to_gradio_chatbot()

    def dict(self):
        logger.info(f"JP1: STATE.dict")
        base = self.conv.dict()
        base.update(
            {
                "conv_id": self.conv_id,
                "model_name": self.model_name,
            }
        )
        return base


def set_global_vars(controller_url_, 
                    enable_moderation_, 
                    use_remote_storage_):
    """
    Set the global env variables (most of them are not used)
    """
    logger.info(f"JP1: set_global_vars")
    global controller_url, enable_moderation, use_remote_storage
    controller_url = controller_url_
    enable_moderation = enable_moderation_
    use_remote_storage = use_remote_storage_


def get_conv_log_filename():
    """
    Return the log output file name
    """
    logger.info(f"JP1: get_conv_log_filename")
    t = datetime.datetime.now()
    conv_log_filename = f"logs/conversations/{t.year}-{t.month:02d}-{t.day:02d}-conv.json"
    name = os.path.join(LOGDIR, conv_log_filename)

    return name


def get_model_list(controller_url, 
                  register_api_endpoint_file):
    """
    Register model to controller and return non-anonymous models
    """
    logger.info(f"JP1: get_model_list")
    global api_endpoint_info

    # Add models from the controller
    if controller_url:
        ret = requests.post(controller_url + "/refresh_all_workers")
        assert ret.status_code == 200

        ret = requests.post(controller_url + "/list_language_models")
        models = ret.json()["models"]
    else:
        models = []

    # Add models from the API providers
    if register_api_endpoint_file:
        api_endpoint_info = json.load(open(register_api_endpoint_file))
        for mdl, mdl_dict in api_endpoint_info.items():
            mdl_text = mdl_dict.get("text-arena", True)
            if mdl_text:
                models.append(mdl)

    # Remove anonymous models
    models = list(set(models))
    visible_models = models.copy()
    for mdl in models:
        if mdl not in api_endpoint_info:
            continue
        mdl_dict = api_endpoint_info[mdl]
        if mdl_dict["anony_only"]:
            visible_models.remove(mdl)

    # Sort models and add descriptions
    priority = {k: f"___{i:03d}" for i, k in enumerate(model_info)}
    models.sort(key=lambda x: priority.get(x, x))
    visible_models.sort(key=lambda x: priority.get(x, x))
    logger.info(f"All models: {models}")
    logger.info(f"Visible models: {visible_models}")
    return visible_models, models


def load_demo_single(models,
                     url_params):
    """
    Load the dropdown menu with model names
    """
    logger.info(f"JP1: load_demo_single")
    selected_model = models[-1] if len(models) > 0 else ""
    if "model" in url_params:
        model = url_params["model"]
        if model in models:
            selected_model = model

    
    # [CHANGE MODEL NAME]
    models = [model_to_name_dict[x] for x in models]
    selected_model = model_to_name_dict[selected_model]
    
    dropdown_update = gr.Dropdown(choices=models, value=selected_model, visible=True)
    
    #state = gr.State()
    state = None #State("Legal-AI-PRO")#None
    return state, dropdown_update

def handle_parsing(file_name):
    logger.info(f"JP1: handle_parsing")
    # Check type
    if '.pdf' in file_name:
        logger.info("Parsing PDF")
        loader = PyPDFLoader(file_name)
        pages = loader.load_and_split()
        data = "\n".join([p.page_content for p in pages])
    elif '.docx' in file_name:
        logger.info("Parsing Word Document")
        loader = Docx2txtLoader(file_name)
        pages = loader.load()
        data = "\n".join([p.page_content for p in pages])
    else:
        # .txt
        with open(file_name, 'r') as f_in:
            data = f_in.read()

    return data


def upload_document(state, upload_files, doc_src, doc_title, doc_year, request: gr.Request):
    logger.info(f"JP1: upload_document")
    gr.Info('Caricamento dei dati nel sistema')
    file_paths = [file.name for file in upload_files]

    vector_db = state.vector_db
    retriever = state.retriever

    global text_splitter

    logger.info(f"Loading new data with metadata for {get_ip(request)}: 'src': {doc_src} | 'year' : {doc_year} | 'title' : {doc_title}")

    gr.Info("Conversione dei dati in corso")
    new_data = []
    for file in file_paths:
        raw_data = handle_parsing(file)

        ip_user = -1
        try:
            ip_user = int(get_ip(request).replace(".", ""))
        except:
            ip_user = 0

        set_name = "Uploaded_data"
        metadata = {
            "source" : doc_src,
            "user" :  ip_user,
            "file_name" : file,
            "set" : set_name,
            "year" : doc_year,
            "art_title" : doc_title if '"' in doc_title else f'"{doc_title}"',
            "art_n" : '-'
        }
        new_data.append(Document(page_content=raw_data, metadata=metadata))
    
    gr.Info("Caricamento dei dati nel database")
    logger.info("Creating chunks")
    new_docs = text_splitter.split_documents(new_data)

    logger.info("Adding new instances to DB")
    ids = vector_db.upsert(documents=new_docs)
    logger.info("Completed with success")

    # Re-init vector retriever
    # logger.info("Reinitialization of the retriever vector index")
    # state.retriever = vector_db.as_retriever(search_kwargs={"k": TOP_K_RANK})

    # base_chain = {"context": state.retriever | process_docs, "question": RunnablePassthrough()}

    # stete.chain = (
    #     base_chain
    #     | prompt
    # )
    # TODO: Re-init retriever

    return ("", "", "", disable_btn)


def log_upload(upload_files, request: gr.Request):
    logger.info(f"JP1: log_upload")
    n_files = len(upload_files)
    gr.Info(f'Hai caricato {n_files} files. Clicca su "Carica" per inserirli nel database.')
    logger.info(f"The user {get_ip(request)} uploaded {n_files}")
    return (enable_btn)

# gr.Request
# A Gradio request object that can be used to access the request headers, cookies, query parameters and other information about the request from within the prediction function. 
# The class is a thin wrapper around the fastapi.Request class. Attributes of this class include: headers, client, query_params, session_hash, and path_params. 
# If auth is enabled, the username attribute can be used to get the logged in user.

def load_demo(url_params, 
              request: gr.Request):
    """
    Load chat page and register IP infos
    """
    logger.info(f"JP1: load_demo")
    global models

    ip = get_ip(request)
    logger.info(f"load_demo. ip: {ip}. params: {url_params}")

    if args.model_list_mode == "reload":
        models, all_models = get_model_list(
            controller_url, args.register_api_endpoint_file
        )

    return load_demo_single(models, url_params)


def vote_last_response(state, 
                      vote_type, 
                      model_selector, 
                      request: gr.Request):
    """
    Log vote to external log file
    """
    logger.info(f"JP1: vote_last_response")
    filename = get_conv_log_filename()

    with open(filename, "a") as fout:
        data = {
            "tstamp": round(time.time(), 4),
            "type": vote_type,
            "model": model_selector,
            "state": state.dict(),
            "ip": get_ip(request),
        }
        fout.write(json.dumps(data) + "\n")
    get_remote_logger().log(data)

def log_quality(state, quality_value, model_selector, request: gr.Request):
    """
    Log the quality of the answer
    """
    logger.info(f"JP1: log_quality")
    if quality_value:
        # if user selected a quality value (!= None)
        ip = get_ip(request)
        logger.info(f"quality score. ip: {ip} --> {quality_value}")
        vote_last_response(state, quality_value, model_selector, request)

        return (disable_radio, disable_btn)

    #return (gr.update(value=None), )
    return (no_change_radio, no_change_btn)

def upvote_last_response(state, model_selector, request: gr.Request):
    """
    Log the upvote for the last response to remote log file
    """
    logger.info(f"JP1: upvote_last_response")
    ip = get_ip(request)
    logger.info(f"upvote. ip: {ip}")
    vote_last_response(state, "upvote", model_selector, request)
    return ("",) + (disable_btn,) * 3

def downvote_last_response(state, model_selector, request: gr.Request):
    """
    Log the downvote for the last response to remote log file
    """
    logger.info(f"JP1: downvote_last_response")
    ip = get_ip(request)
    logger.info(f"downvote. ip: {ip}")
    vote_last_response(state, "downvote", model_selector, request)
    return ("",) + (disable_btn,) * 3


def flag_last_response(state, model_selector, request: gr.Request):
    """
    Log the flag for the last response to remote log file
    """
    ip = get_ip(request)
    logger.info(f"flag. ip: {ip}")
    vote_last_response(state, "flag", model_selector, request)
    return ("",) + (disable_btn,) * 3


def regenerate(state, request: gr.Request):
    """
    Regenerate last response and update the last message (in order to align for future logs)
    """
    logger.info(f"JP1: regenerate")
    ip = get_ip(request)
    logger.info(f"regenerate. ip: {ip}")
    if not state.regen_support:
        state.skip_next = True
        return (state, state.to_gradio_chatbot(), "", None) + (no_change_btn,) * 5 + (no_change_radio, no_change_btn)

    state.conv.update_last_message(None)
    state.conv_wo_context.update_last_message(None)
    return (state, state.to_gradio_chatbot(), "", None) + (disable_btn,) * 5 + (disable_radio, disable_btn)


def clear_history(request: gr.Request):
    """
    Clear the state history
    """
    logger.info(f"JP1: clear_history")
    ip = get_ip(request)
    logger.info(f"clear_history. ip: {ip}")
    state = None
    return (state, [], "", None, "") + (disable_btn,) * 5 + (disable_radio, disable_btn)


def get_ip(request: gr.Request):
    """
    Get user IP
    """
    logger.info(f"JP1: get_ip")
    if "cf-connecting-ip" in request.headers:
        ip = request.headers["cf-connecting-ip"]
    elif "x-forwarded-for" in request.headers:
        ip = request.headers["x-forwarded-for"]
    else:
        ip = request.client.host
    return ip



def add_text(state, 
             model_selector, 
             text, 
             image, 
             request: gr.Request):
    """
    Handle conversation turn limits, flags and append text to the coversation state
    """
    logger.info(f"JP1: add_text")

    # Get user IP
    ip = get_ip(request)
    logger.info(f"add_text. ip: {ip}. len: {len(text)}")

    # Eventually set state
    if state is None:
        state = State(model_selector)

    # Handle empty input data
    if len(text) <= 0:
        state.skip_next = True
        return (state, state.to_gradio_chatbot_wo_context(), "", None) + (no_change_btn,) * 5 + (no_change_radio, no_change_btn)


    all_conv_text = state.conv.get_prompt()
    all_conv_text = all_conv_text[-2000:] + "\nuser: " + text
    flagged = moderation_filter(all_conv_text, [state.model_name])
    # flagged = moderation_filter(text, [state.model_name])
    if flagged:
        logger.info(f"violate moderation. ip: {ip}. text: {text}")
        # overwrite the original text
        text = MODERATION_MSG


    if (len(state.conv.messages) - state.conv.offset) // 2 >= CONVERSATION_TURN_LIMIT:
        logger.info(f"conversation turn limit. ip: {ip}. text: {text}")
        state.skip_next = True
        return (state, state.to_gradio_chatbot_wo_context(), CONVERSATION_LIMIT_MSG, None) + (
            no_change_btn,
        ) * 5 + (no_change_radio, no_change_btn)

    # Text contains the user input
    # ---------
    text = text[:INPUT_CHAR_LEN_LIMIT]  # Hard cut-off

    # Retrieval
    prompt_w_context, reranked_docs = retrieve_documents(state, text)
    logger.info(f">>>> NRD: {len(reranked_docs)}")
    # ---------

    # Format data with roles (w/ context for model inference)
    state.conv.append_message(state.conv.roles[0], prompt_w_context)
    state.conv.append_message(state.conv.roles[1], None)

    # (w/o context for chat GUI)
    state.conv_wo_context.append_message(state.conv.roles[0], text)
    state.conv_wo_context.append_message(state.conv.roles[1], None)

    state.reranked_docs = reranked_docs

    return (state, state.to_gradio_chatbot_wo_context(), "", None) + (disable_btn,) * 5 + (disable_radio, disable_btn)


def model_worker_stream_iter(
        conv,
        model_name,
        worker_addr,
        prompt
    ):
    """
    Launch generation with streaming output
    """
    logger.info(f"JP1: model_worker_stream_iter")
    # Make requests
    gen_params = {
        "model": model_name,
        "prompt": prompt,
        "temperature": temperature,
        "repetition_penalty": repetition_penalty,
        "top_p": top_p,
        "max_new_tokens": max_new_tokens,
        "stop": conv.stop_str,
        "stop_token_ids": conv.stop_token_ids,
        "echo": False,
    }

    logger.info(f"==== request ====\n{gen_params}")

    # Stream output
    response = requests.post(
        worker_addr + "/worker_generate_stream",
        headers=headers,
        json=gen_params,
        stream=True,
        timeout=WORKER_API_TIMEOUT,
    )
    for chunk in response.iter_lines(decode_unicode=False, delimiter=b"\0"):
        if chunk:
            data = json.loads(chunk.decode())
            yield data


def bot_response(
        state,
        request: gr.Request,
        already_retrieved_context_html=None
    ):
    """
    Handle generation parameters and launch the generation. Then update the conversation state and handle errors. At the end, log.
    """
    logger.info(f"JP1: bot_response")
    ip = get_ip(request)
    logger.info(f"bot_response. ip: {ip}")
    start_tstamp = time.time()

    if not already_retrieved_context_html:
        documents_html = [{"source" : "", "year" : "", "title" : "", "content" : "..."}]
        context_html = context_html_template.render(documents=documents_html)
    else:
        context_html = already_retrieved_context_html

    logger.info(f"JPLOG: {str(state)}")

    if state.skip_next:
        # This generate call is skipped due to invalid inputs
        state.skip_next = False
        yield (state, state.to_gradio_chatbot_wo_context(), context_html) + (no_change_btn,) * 5 + (no_change_radio, no_change_btn)
        return


    conv, model_name = state.conv, state.model_name
    conv_wo_context = state.conv_wo_context
    reranked_documents = state.reranked_docs
    logger.info(f"N RERANKED DOCS: {len(reranked_documents)}")

    model_api_dict = (
        api_endpoint_info[model_name] if model_name in api_endpoint_info else None
    )

    # Query worker address
    ret = requests.post(
        controller_url + "/get_worker_address", json={"model": model_name}
    )
    worker_addr = ret.json()["address"]
    logger.info(f"model_name: {model_name}, worker_addr: {worker_addr}")

    # No available worker
    if worker_addr == "":
        conv.update_last_message(SERVER_ERROR_MSG)
        conv_wo_context.update_last_message(SERVER_ERROR_MSG)
        yield (
            state,
            state.to_gradio_chatbot_wo_context(),
            context_html,
            disable_btn,
            disable_btn,
            disable_btn,
            enable_btn,
            enable_btn,
            disable_radio,
            disable_btn
        )
        return


    # -------------------------
    # Update retrieval cards
    if not already_retrieved_context_html:
        documents = []
        n_cards = 0
        for d_id, d in enumerate(reranked_documents):
            if n_cards < TOP_K_SHOW_CARDS:
                d_txt = d.page_content
                if len(d_txt) >= MIN_CHUNK_LEN_THRESHOLD:
                    retr_card = format_docs_for_cards(d)
                    documents.append(retr_card)
                    n_cards += 1

        # eventually aggregate chunks from the same document
        logger.info(f"chunks: {len(documents)}")
        documents = unify_chunks_from_same_doc(documents)
        context_html = context_html_template.render(documents=documents)


    # ------------------------

    # Construct prompt.
    # We need to call it here, so it will not be affected by "▌".
    prompt = conv.get_prompt()
    # Set repetition_penalty
    if "t5" in model_name:
        repetition_penalty = 1.2
    else:
        repetition_penalty = 1.0

    stream_iter = model_worker_stream_iter(
        conv,
        model_name,
        worker_addr,
        prompt
    )
    

    html_code = ' <span class="cursor"></span> '

    # >>> Update last message in history
    # conv.update_last_message("▌")
    conv.update_last_message(html_code)
    conv_wo_context.update_last_message(html_code)

    yield (state, state.to_gradio_chatbot_wo_context(), context_html) + (disable_btn,) * 5 + (disable_radio, disable_btn)

    try:
        data = {"text": ""}
        for i, data in enumerate(stream_iter):
            if data["error_code"] == 0:
                output = data["text"].strip()
                
                conv.update_last_message(output + html_code)
                conv_wo_context.update_last_message(output + html_code)
                yield (state, state.to_gradio_chatbot_wo_context(), context_html) + (disable_btn,) * 5 + (disable_radio, disable_btn)
            else:
                output = data["text"] + f"\n\n(error_code: {data['error_code']})"
                conv.update_last_message(output)
                conv_wo_context.update_last_message(output)
                yield (state, state.to_gradio_chatbot_wo_context(), context_html) + (
                    disable_btn,
                    disable_btn,
                    disable_btn,
                    enable_btn,
                    enable_btn,
                    disable_radio,
                    disable_btn
                )
                return
        output = data["text"].strip()
        conv.update_last_message(output)
        
        conv_wo_context.update_last_message(output)

        # overwrite last user message and remove prompt with context resources
        conv.overwrite_last_message(state.conv.roles[0], conv_wo_context.get_last_message_by_role(state.conv.roles[0]))

        yield (state, state.to_gradio_chatbot_wo_context(), context_html) + (enable_btn,) * 5 + (enable_radio, enable_btn)

    except requests.exceptions.RequestException as e:
        conv.update_last_message(
            f"{SERVER_ERROR_MSG}\n\n"
            f"(error_code: {ErrorCode.GRADIO_REQUEST_ERROR}, {e})"
        )
        conv_wo_context.update_last_message(
            f"{SERVER_ERROR_MSG}\n\n"
            f"(error_code: {ErrorCode.GRADIO_REQUEST_ERROR}, {e})"
        )
        yield (state, state.to_gradio_chatbot_wo_context(), context_html) + (
            disable_btn,
            disable_btn,
            disable_btn,
            enable_btn,
            enable_btn,
            disable_radio,
            disable_btn
        )
        return
    except Exception as e:
        conv.update_last_message(
            f"{SERVER_ERROR_MSG}\n\n"
            f"(error_code: {ErrorCode.GRADIO_STREAM_UNKNOWN_ERROR}, {e})"
        )
        conv_wo_context.update_last_message(
            f"{SERVER_ERROR_MSG}\n\n"
            f"(error_code: {ErrorCode.GRADIO_STREAM_UNKNOWN_ERROR}, {e})"
        )
        yield (state, state.to_gradio_chatbot_wo_context(), context_html) + (
            disable_btn,
            disable_btn,
            disable_btn,
            enable_btn,
            enable_btn,
            disable_radio,
            disable_btn
        )
        return

    finish_tstamp = time.time()
    logger.info(f"{output}")

    # conv.save_new_images(use_remote_storage=use_remote_storage)

    filename = get_conv_log_filename()

    with open(filename, "a") as fout:
        data = {
            "tstamp": round(finish_tstamp, 4),
            "type": "chat",
            "model": model_name,
            "gen_params": {
                "temperature": temperature,
                "top_p": top_p,
                "max_new_tokens": max_new_tokens,
            },
            "start": round(start_tstamp, 4),
            "finish": round(finish_tstamp, 4),
            "state": state.dict(),
            "ip": get_ip(request),
        }
        fout.write(json.dumps(data) + "\n")
    get_remote_logger().log(data)


# ******************************************************************************************
# >>>>> CHAT INTERFACE

# Site header
headers = {"User-Agent": "FastChat Client"}

# List of buttons as globoal vars
no_change_btn = gr.Button()
no_change_radio = gr.Radio()
enable_radio = gr.Radio(interactive=True, visible=True)
enable_btn = gr.Button(interactive=True, visible=True)
disable_btn = gr.Button(interactive=False)
disable_radio = gr.Radio(interactive=False)
invisible_btn = gr.Button(interactive=False, visible=False)
invisible_html = gr.HTML()

controller_url = None
enable_moderation = False
use_remote_storage = False

acknowledgment_md = """
### Note di servizio

Questo sistema di chat basato su AI è una versione in fase di sviluppo. Le risposte fornite potrebbero
contenere informazioni errate o offensive. Verifica sempre le informazioni sui testi di riferimento
e/o con personale qualificato.
"""

js_code = f"""
<script>
    document.addEventListener('DOMContentLoaded', function() {{
        var warningMessage = "{acknowledgment_md}";
        alert(warningMessage);
    }});
</script>
"""

api_endpoint_info = {}


temperature = TEMPERATURE
top_p = TOP_P
max_new_tokens = MAX_NEW_TOKENS
repetition_penalty = REP_PENALTY

def build_single_model_ui(models, add_promotion_links=False):
    """ 
    Create the interface to chat with a single model. It consists of:
        - model_selector drowpdown menu
        - chatbot (output) panel
        - textual input field
        - voting and util buttons

    """
    # State: A base class for defining methods that all input/output components should have
    logger.info("Creating state")
    state = gr.State()
    logger.info(f"DJPLOG: {str(state)}")
    logger.info("Done")

    ## OLD ## title_markdown = '# <span style="color:orange">A</span>ss<span style="color:orange">i</span>stente <span style="color:blue">x</span> Codice degli Appalti D.Lgs. 36/2023 ( <span style="color:red">BETA</span>)'
    title_markdown = '# Agriveritas: chatbot per le AgEA, gli imprenditori agricoli, il territorio'
    gr.Markdown(title_markdown, elem_id="notice_markdown")



    # Group is a layout element within Blocks which groups together children so that they do not have any padding or margin between them.
    with gr.Blocks(elem_id="main_block"):
        with gr.Row(elem_id="left_right_disposiion"):
            with gr.Column(elem_id="share-region-named", scale=2):
                
                gr.Markdown(acknowledgment_md, elem_id="ack_markdown")

                chose_model_txt = "Scegli con quale modello dialogare."
                gr.Markdown(chose_model_txt, elem_id="choose_markdown")

                # ------------------------------------------------------------------------
                # >>> Model Selector
                with gr.Row(elem_id="model_selector_row"):

                    # Drop down menu to selec the model the user want to interact with

                    model_selector = gr.Dropdown(
                        choices=models,
                        value=models[0] if len(models) > 0 else "",
                        interactive=True,
                        show_label=False,
                        container=False,
                    )
                
                # ------------------------------------------------------------------------
                # >>> Main Pane:
                # - chat text (left)
                # - retrieval pane (right)
                # - submit text (bottom)
                with gr.Row(elem_id="main_frame_box"):

                    with gr.Column("main_frame_inner_box"):
                        # ---------------------------------
                        # Chat output panel
                        chatbot = gr.Chatbot(
                            elem_id="chatbot",
                            label="Assistente Chatbot",
                            height=550,
                            show_copy_button=True,
                            avatar_images=('assets/user_avatar.png', # user
                                            'assets/assistant_icon.png'), # agent
                            bubble_full_width=False
                        )

                        with gr.Row():
                            # Input field
                            textbox = gr.Textbox(
                                show_label=False,
                                placeholder="La tua domanda ...",
                                elem_id="input_box"
                            )
                            # Submit button
                            # 'primary' for main call-to-action, 'secondary' for a more subdued style, 'stop' for a stop button.
                            send_btn = gr.Button(value="💬 Invia", variant="primary", scale=0)

                        # Examples
                        gr.Markdown("Inserisci una domanda nel campo di testo qui sopra!", elem_id="ack_markdown")
                        '''
                        gr.Examples(examples, textbox, label="Esempi di domande sul Codice degli Appalti")
                        '''
                        # ------------------------------------------------------------------------
                        gr.Markdown("## Carica tue risorse!")
                        
                        # # # ### Aggiornamento della giurisprudenza
                        # # # Per mantenere il sistema al passo con i recenti sviluppi della giurisprudenza in ambito Codice degli Appalti è possibile inserire nuove informazioni nel database 
                        # # # e utilizzare subito il loro contenuto per rispondere alle domande degli utenti.

                        # # # I documenti possono essere allegati con un file in formato .txt, .docx o .pdf nel box sottostante. Per facilitare la referenziazione delle fonti,
                        # # # è possibile indicare nei rispettivi campi il titolo, l'anno di pubblicazione e l'autore del documento allegato. 

                        # # # ### Istruzioni
                        # # # Per caricare il/i documento/i cliccare il pulsante "Allega". Per inserirli correttamente nel sistema, premere infine "Carica". E' possibile selezionare e caricare più di un documento alla volta.
                        
                        info_upload = """
                        Permettiamo di caricare dei tuoi file al fine di avvicinare la risposta alla tua realtà, e di confrontarla con le informazioni note!
                        
                        I documenti possono essere allegati con un file in formato .txt, .docx o .pdf

                        ### Istruzioni
                        Per caricare il/i documento/i cliccare il pulsante "Allega". Per inserirli correttamente nel sistema, premere infine "Carica". E' possibile selezionare e caricare più di un documento alla volta.
                        
                        """
                        gr.Markdown(info_upload, elem_id="upload_info_markdown")
                        # >>> Data Upload
                        with gr.Column():
                            '''
                            with gr.Row():
                                doc_src = gr.Textbox(
                                    show_label=False,
                                    placeholder="Fonte Giuridica",
                                    elem_id="upload_src"
                                )
                                
                                doc_year = gr.Textbox(
                                    show_label=False,
                                    placeholder="Anno di emanazione",
                                    elem_id="upload_year"
                                )

                                doc_title = gr.Textbox(
                                    show_label=False,
                                    placeholder="Titolo",
                                    elem_id="upload_title"
                                )
                            '''

                            # Upload document
                            with gr.Row():
                                upload_button = gr.UploadButton(label="📎 Allega", file_types=[".pdf",".docx", ".txt"], file_count="multiple")
                                load_button = gr.Button(value="📤 Carica", interactive=False)


                        '''
                        # ------------------------------------------------------------------------
                        # >>> Voting System
                        gr.Markdown("## Valutazione della Risposta")
                        valutazione_infos = """
                        ### Preferenza
                        L'utente può fornire un feedback positivo/negativo sulla qualità della risposta ottenuta con i pulsanti "Like"/"Dislike". Questo sistema è ancora in fase di sviluppo e potrebbe generare contenuto inappropriato. E' possibile segnalarlo con l'apposito bottone.

                        Per rigenerare l'ultima risposta o per cancellare i messaggi precedenti, è possibile interagire con "Rigenera risposta" e "Cancella chat".
                        """
                        gr.Markdown(valutazione_infos, elem_id="eval_info_markdown")
                        '''
                        with gr.Row() as button_row:
                            '''
                            upvote_btn = gr.Button(value="👍 Like", interactive=False)
                            downvote_btn = gr.Button(value="👎 Dislike", interactive=False)
                            flag_btn = gr.Button(value="⚠️  Contenuto Inappropriato", interactive=False)
                            '''
                            regenerate_btn = gr.Button(value="🔄  Rigenera risposta", interactive=False)
                            clear_btn = gr.Button(value="🗑️  Cancella chat", interactive=False)
                            '''
                        '''
                        '''
                        # ------------------------------------------------------------------------
                        # >>> Scoring System
                        valutazione_infos_qual = """
                        ### Qualità
                        L'utente può inoltre indicare un livello di correttezza per le informazioni generate selezionando una delle seguenti opzioni.
                        """
                        gr.Markdown(valutazione_infos_qual, elem_id="eval_info_qual_markdown")
                        with gr.Row():
                            quality_value = gr.Radio(
                                choices=[
                                    "Eccellente",
                                    "Soddisfacente",
                                    "Insufficiente"
                                ],
                                value=None,
                                label='Valutazione di qualità',
                                scale=4,
                                interactive=False
                            )
                            quality_button = gr.Button(value="📝 Valuta", variant="primary", scale=1, interactive=False)
                        '''

            with gr.Column(elem_id="retrieval_cards_frame", scale=1):
                context_html = gr.HTML()

    #overflow-y: auto; /* Add a vertical scrollbar if content exceeds container height */    

    # Register listeners
    imagebox = gr.State(None)

    # Upload PDF
    upload_button.upload(
        log_upload,
        [upload_button],
        [load_button]
    )

    '''
    load_button.click(
        upload_document,
        [state, upload_button, doc_src, doc_title, doc_year],
        [doc_src, doc_title, doc_year, load_button]
    )
    '''

    '''
    # Quality Score
    quality_button.click(
        log_quality,
        [state, quality_value, model_selector],
        [quality_value, quality_button]
    )
    '''
    
    '''
    btn_list = [upvote_btn, downvote_btn, flag_btn, regenerate_btn, clear_btn]
    score_list = [quality_value, quality_button]
    '''
    btn_list = [regenerate_btn]

    '''
    # Callback UPVOTE
    upvote_btn.click(
        upvote_last_response,
        [state, model_selector],
        [textbox, upvote_btn, downvote_btn, flag_btn],
    )
    # Callback DOWNVOTE
    downvote_btn.click(
        downvote_last_response,
        [state, model_selector],
        [textbox, upvote_btn, downvote_btn, flag_btn],
    )
    # Callback ERROR
    flag_btn.click(
        flag_last_response,
        [state, model_selector],
        [textbox, upvote_btn, downvote_btn, flag_btn],
    )
    '''
    '''
    # Callback REGEN
    regenerate_btn.click(
        regenerate, state, [state, chatbot, textbox, imagebox] + btn_list + score_list
    ).then(
        bot_response,
        [state],
        [state, chatbot, context_html] + btn_list + score_list,
    )
    # Callback CLEAR
    clear_btn.click(clear_history, None, [state, chatbot, textbox, imagebox, context_html] + btn_list + score_list)
    '''
    # Callback REGEN
    regenerate_btn.click(
        regenerate, state, [state, chatbot, textbox, imagebox] + btn_list
    ).then(
        bot_response,
        [state],
        [state, chatbot, context_html] + btn_list,
    )
    # Callback CLEAR
    clear_btn.click(clear_history, None, [state, chatbot, textbox, imagebox, context_html] + btn_list)

    '''
    # When a new model is selected (event), clear history
    model_selector.change(
        clear_history, None, [state, chatbot, textbox, imagebox, context_html] + btn_list + score_list
    )
    '''
    # When a new model is selected (event), clear history
    model_selector.change(
        clear_history, None, [state, chatbot, textbox, imagebox, context_html] + btn_list
    )
    '''
    # Callback SUBMIT MESSAGE
    # Either with enter on the text field or by clickin the submit button
    # - first add message to context and history
    # - launch stream service
    textbox.submit(
        add_text,
        [state, model_selector, textbox, imagebox],
        [state, chatbot, textbox, imagebox] + btn_list + score_list,
    ).then(
        bot_response,
        [state],
        [state, chatbot, context_html] + btn_list + score_list,
    )
    send_btn.click(
        add_text,
        [state, model_selector, textbox, imagebox],
        [state, chatbot, textbox, imagebox] + btn_list + score_list,
    ).then(
        bot_response,
        [state],
        [state, chatbot, context_html] + btn_list + score_list,
    )
    '''

    # Callback SUBMIT MESSAGE
    # Either with enter on the text field or by clickin the submit button
    # - first add message to context and history
    # - launch stream service
    textbox.submit(
        add_text,
        [state, model_selector, textbox, imagebox],
        [state, chatbot, textbox, imagebox] + btn_list,
    ).then(
        bot_response,
        [state],
        [state, chatbot, context_html] + btn_list,
    )
    send_btn.click(
        add_text,
        [state, model_selector, textbox, imagebox],
        [state, chatbot, textbox, imagebox] + btn_list,
    ).then(
        bot_response,
        [state],
        [state, chatbot, context_html] + btn_list,
    )

    return [state, model_selector]


def build_demo(models):
    with gr.Blocks(
        title="Agriveritas", #JPMOD #Assistente AI x Codice degli Appalti",
        theme='Ama434/neutral-barlow', #gr.themes.Default(),#'Ama434/neutral-barlow', #,
        css=block_css,
    ) as demo:

        # display arbitrary JSON output prettily
        url_params = gr.JSON(visible=False)

        state, model_selector = build_single_model_ui(models)

        logger.info(f"JPLOG4: {str(state)}")
        if args.model_list_mode not in ["once", "reload"]:
            raise ValueError(f"Unknown model list mode: {args.model_list_mode}")

        if args.show_terms_of_use:
            load_js = get_window_url_params_with_tos_js
        else:
            load_js = get_window_url_params_js

        demo.load(
            load_demo,
            [url_params],
            [
                state,
                model_selector,
            ],
            js=load_js,
        )

    return demo


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int)
    parser.add_argument(
        "--share",
        action="store_true",
        help="Whether to generate a public, shareable link",
    )
    parser.add_argument(
        "--controller-url",
        type=str,
        default="http://localhost:21001",
        help="The address of the controller",
    )
    parser.add_argument(
        "--concurrency-count",
        type=int,
        default=10,
        help="The concurrency count of the gradio queue",
    )
    parser.add_argument(
        "--model-list-mode",
        type=str,
        default="once",
        choices=["once", "reload"],
        help="Whether to load the model list once or reload the model list every time",
    )
    parser.add_argument(
        "--moderate",
        action="store_true",
        help="Enable content moderation to block unsafe inputs",
    )
    parser.add_argument(
        "--show-terms-of-use",
        action="store_true",
        help="Shows term of use before loading the demo",
    )
    parser.add_argument(
        "--register-api-endpoint-file",
        type=str,
        help="Register API-based model endpoints from a JSON file",
    )
    parser.add_argument(
        "--gradio-auth-path",
        type=str,
        help='Set the gradio authentication file path. The file should contain one or more user:password pairs in this format: "u1:p1,u2:p2,u3:p3"',
    )
    parser.add_argument(
        "--gradio-root-path",
        type=str,
        help="Sets the gradio root path, eg /abc/def. Useful when running behind a reverse-proxy or at a custom URL path prefix",
    )
    parser.add_argument(
        "--use-remote-storage",
        action="store_true",
        default=False,
        help="Uploads image files to google cloud storage if set to true",
    )
    args = parser.parse_args()
    logger.info(f"args: {args}")

    # Set global variables
    set_global_vars(args.controller_url, args.moderate, args.use_remote_storage)
    models, all_models = get_model_list(
        args.controller_url, args.register_api_endpoint_file
    )

    # Set authorization credentials
    auth = None
    if args.gradio_auth_path is not None:
        auth = parse_gradio_auth_creds(args.gradio_auth_path)


    # Launch the demo
    demo = build_demo(models)
    demo.queue(
        default_concurrency_limit=args.concurrency_count,
        status_update_rate=10,
        api_open=False,
    ).launch(
        server_name=args.host,
        server_port=args.port,
        share=args.share,
        max_threads=200,
        auth=auth,
        root_path=args.gradio_root_path,
    )
