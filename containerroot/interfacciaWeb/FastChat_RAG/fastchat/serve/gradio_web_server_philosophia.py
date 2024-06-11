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
context_html_template = env.get_template('fancy_context_html_template_philosophia.j2')
# Configurations for the RAG architecture
logger = build_logger("gradio_web_server", "logs/ui/gradio_web_server_philosophia.log")



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
Sei un chatbot che supporta gli studenti nello studio di vari filosofi. Rispondi in italiano ed in maniera
corretta alla domanda posta facendo riferimento al contesto fornito di seguito. Rispondi in maniera esaustiva.
Scrivi più di 4-5 frasi. Genera solamente la risposta alla domanda. 

Informazioni di riferimento:
-------------------
{context}
-------------------

Rispondi ora alla seguente domanda:
{question}

Risposta:
"""

format_src_data = """
**********
Autore: {author}
Fonte: {src}

{txt}
**********
"""

logger.info("Loading retrieval models")

EMBED_NAME = "BAAI/bge-m3"
RERANKER_NAME = "BAAI/bge-reranker-base"
CHUNK_SIZE=512
CHUNK_OVERLAP=0
TOP_K_SHOW_CARDS=3

embedder = HuggingFaceEmbeddings(model_name=EMBED_NAME, model_kwargs={"device" : ENCODER_DEVICE})
reranker_model = FlagReranker(RERANKER_NAME, use_fp16=True, device=RANKER_DEVICE)

text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP,separators=["\n\n"," ",".",","])

# > init connection
logger.info("Establishing connection with Milvus DB")
try:
    connections.connect("default", host="0.0.0.0")
except:
    logger.info("Starting the server at 0.0.0.0")
    default_server.start()
    connections.connect("default", host="0.0.0.0")

collection = Collection("PhilosophIA")
logger.info(f'collection: {collection.name} has {collection.num_entities} entities')


# > handler methods
def format_docs(docs):
    ctx = []
    for d in docs:
        txt = d.page_content
        meta = d.metadata
        this_src = format_src_data.format(author=meta['author'], src=meta['source'], txt=txt)
        ctx.append(this_src)

    return "\n".join(ctx)

def rerank_docs(docs):
    global global_query, global_context, reranker_model
    pairs = [list((global_query, d.page_content)) for d in docs]
    scores = reranker_model.compute_score(pairs)
    permutation = np.argsort(scores)[::-1]
    docs = [docs[i] for i in permutation]
    global_context = [
        {
            "content": d.page_content,
            "metadata": d.metadata
        } for d in docs
    ]
    docs = docs[:TOP_K_RERANK]
    return docs

def process_docs(docs):
    global reranked_documents
    docs = rerank_docs(docs)
    reranked_documents = docs

    return format_docs(docs)


def handle_parsing(file_name):
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


def format_docs_for_cards(doc):
    txt = doc.page_content
    MIN_LEN = 200
    if len(txt) < MIN_LEN: return None
    
    metadata = doc.metadata

    logger.info(metadata['file_name'])
    whole_article = handle_parsing(metadata['file_name'])

    txt = whole_article.replace(txt, f'<span>{txt}</span>')

    start_pos = txt.rfind(doc.page_content)
    end = start_pos + len(doc.page_content)
    DELTA=500
    _s = max(start_pos-DELTA, 0)
    txt = txt[_s:end+DELTA]

    out = {
        'source' : metadata['source'],
        'author' : metadata['author'],
        'content' : txt
    }

    if len(txt) < MIN_LEN: return None

    return out

def retrieve_documents(question):
    """
    Return the prompt with the question and supporting facts
    """
    global global_query
    gr.Info("Ricerco informazioni utili")
    global_query = question
    logger.info(f">>> QUESTION: {global_query}")
    input_prompt = chain.invoke(question)
    context_augmented_prompt = input_prompt.messages[0].content

    return context_augmented_prompt


# > define rag pipeline
prompt = ChatPromptTemplate.from_template(usr_template)
vector_db = Milvus(
    embedder,
    connection_args={"host": "127.0.0.1", "port": "19530"},
    collection_name="PhilosophIA",
    auto_id=True,
)
retriever = vector_db.as_retriever(search_kwargs={"k": TOP_K_RANK})

base_chain = {"context": retriever | process_docs, "question": RunnablePassthrough()}

chain = (
    base_chain
    | prompt
)



# --------------------------------------------------

class State:
    """
    Handler class for customizing configurations according to the chosen model.
    """
    def __init__(self, 
                 model_name,
                 is_vision = False):

        self.conv = get_conversation_template(model_name)
        self.conv_wo_context = get_conversation_template(model_name)
        self.conv_id = uuid.uuid4().hex
        self.skip_next = False
        self.model_name = model_name
        self.oai_thread_id = None
        self.is_vision = is_vision

        self.regen_support = True
        if "browsing" in model_name:
            self.regen_support = False
        self.init_system_prompt(self.conv)

    def init_system_prompt(self, conv):
        """
        Initialize the system prompt
        """

        system_prompt = conv.get_system_message()
        if len(system_prompt) == 0:
            return
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        system_prompt = system_prompt.replace("{{currentDateTime}}", current_date)
        conv.set_system_message(system_prompt)

    def to_gradio_chatbot(self):
        return self.conv.to_gradio_chatbot()

    def to_gradio_chatbot_wo_context(self):
        return self.conv_wo_context.to_gradio_chatbot()

    def dict(self):
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
    Set the global env variables
    """
    global controller_url, enable_moderation, use_remote_storage
    controller_url = controller_url_
    enable_moderation = enable_moderation_
    use_remote_storage = use_remote_storage_


def get_conv_log_filename():
    """
    Return the log output file name
    """
    t = datetime.datetime.now()
    conv_log_filename = f"logs/conversations/{t.year}-{t.month:02d}-{t.day:02d}-conv.json"
    name = os.path.join(LOGDIR, conv_log_filename)

    return name


def get_model_list(controller_url, 
                  register_api_endpoint_file):
    """
    Register model to controller and return non-anonymous models
    """

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
    selected_model = models[0] if len(models) > 0 else ""
    if "model" in url_params:
        model = url_params["model"]
        if model in models:
            selected_model = model

    dropdown_update = gr.Dropdown(choices=models, value=selected_model, visible=True)
    state = None
    return state, dropdown_update

def handle_parsing(file_name):
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


def upload_document(upload_files, doc_src, doc_title, doc_year, request: gr.Request):
    gr.Info('Caricamento dei dati nel sistema')
    file_paths = [file.name for file in upload_files]

    global vector_db, retriever, base_chain, text_splitter

    logger.info(f"Loading new data with metadata for {get_ip(request)}: 'src': {doc_src} | 'year' : {doc_year} | 'title' : {doc_title}")

    gr.Info("Conversione dei dati in corso")
    new_data = []
    for file in file_paths:
        raw_data = handle_parsing(file)

        set_name = "Uploaded_data"
        metadata = {
            "source" : doc_src,
            "file_name" : file,
            "set" : set_name,
            "year" : doc_year,
            "art_title" : doc_title,
            "art_n" : '-'
        }
        new_data.append(Document(page_content=raw_data, metadata=metadata))
    
    gr.Info("Caricamento dei dati nel database")
    logger.info("Creating chunks")
    new_docs = text_splitter.split_documents(new_data)

    logger.info("Adding new instances to DB")
    ids = vector_db.upsert(documents=new_docs)
    logger.info(f">>> {ids}")
    logger.info("Completed with success")


    retriever = vector_db.as_retriever(search_kwargs={"k": TOP_K_RANK})

    base_chain = {"context": retriever | process_docs, "question": RunnablePassthrough()}

    chain = (
        base_chain
        | prompt
    )

    return ("", "", "", disable_btn)


def log_upload(upload_files, request: gr.Request):
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
    ip = get_ip(request)
    logger.info(f"upvote. ip: {ip}")
    vote_last_response(state, "upvote", model_selector, request)
    return ("",) + (disable_btn,) * 3


def downvote_last_response(state, model_selector, request: gr.Request):
    """
    Log the downvote for the last response to remote log file
    """
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
    ip = get_ip(request)
    logger.info(f"clear_history. ip: {ip}")
    state = None
    return (state, [], "", None, ) + (disable_btn,) * 5 + (disable_radio, disable_btn)


def get_ip(request: gr.Request):
    """
    Get user IP
    """
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
    logger.info(f">>> USER INPUT: {text}")
    text = text[:INPUT_CHAR_LEN_LIMIT]  # Hard cut-off

    # Retrieval
    prompt_w_context = retrieve_documents(text)
    # ---------


    logger.info(f"Text after cut-off: {text}")

    # Format data with roles (w/ context for model inference)
    state.conv.append_message(state.conv.roles[0], prompt_w_context)
    state.conv.append_message(state.conv.roles[1], None)

    # (w/o context for chat GUI)
    state.conv_wo_context.append_message(state.conv.roles[0], text)
    state.conv_wo_context.append_message(state.conv.roles[1], None)

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
    logger.info(f">>> PROMPT TO THE MODEL: {prompt}")

    # Make requests
    gen_params = {
        "model": model_name,
        "prompt": prompt,
        "temperature": temperature,
        "repetition_penalty": repetition_penalty,
        "top_p": top_p,
        "max_new_tokens": max_new_tokens,
        "min_new_tokens" : 64,
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
        use_recommended_config=False,
    ):
    """
    Handle generation parameters and launch the generation. Then update the conversation state and handle errors. At the end, log.
    """

    ip = get_ip(request)
    logger.info(f"bot_response. ip: {ip}")
    start_tstamp = time.time()

    documents_html = [{"source" : "", "year" : "", "title" : "", "content" : "..."}]
    context_html = context_html_template.render(documents=documents_html)

    if state.skip_next:
        # This generate call is skipped due to invalid inputs
        state.skip_next = False
        yield (state, state.to_gradio_chatbot_wo_context(), context_html) + (no_change_btn,) * 5 + (no_change_radio, no_change_btn)
        return


    conv, model_name = state.conv, state.model_name
    conv_wo_context = state.conv_wo_context

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
    global reranked_documents

    documents = []
    d_id = 0
    for d in reranked_documents:
        if d_id < TOP_K_SHOW_CARDS:
            retr_card = format_docs_for_cards(d)
            if retr_card != None:
                documents.append(retr_card)
                d_id += 1

    context_html = context_html_template.render(documents=documents)


    # ------------------------

    # Construct prompt.
    # We need to call it here, so it will not be affected by "▌".
    prompt = conv.get_prompt()
    logger.info(f"Final prompt: {prompt}")

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
### Terms of Service

This are same warnings...
"""

# TODO

api_endpoint_info = {}


temperature = 0.4
top_p = TOP_P
max_new_tokens = 300
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
    state = gr.State()

    title_markdown = '# Philosoph<span style="color:orange">I</span><span style="color:blue">A</span>'
    gr.Markdown(title_markdown, elem_id="notice_markdown")

    # Group is a layout element within Blocks which groups together children so that they do not have any padding or margin between them.
    with gr.Blocks(elem_id="main_block"):
        with gr.Row(elem_id="left_right_disposiion"):
            with gr.Column(elem_id="share-region-named", scale=2):
                
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
                                            'assets/Socrate.png'), # agent
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

                        # ------------------------------------------------------------------------
                        # >>> Voting System
                        gr.Markdown("## Valutazione della Risposta")

                        with gr.Row() as button_row:
                            upvote_btn = gr.Button(value="👍 Like", interactive=False)
                            downvote_btn = gr.Button(value="👎 Dislike", interactive=False)
                            flag_btn = gr.Button(value="⚠️  Contenuto Inappropriato", interactive=False)
                            regenerate_btn = gr.Button(value="🔄  Rigenera risposta", interactive=False)
                            clear_btn = gr.Button(value="🗑️  Cancella chat", interactive=False)

                        # ------------------------------------------------------------------------
                        # >>> Scoring System
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
                        

            with gr.Column(elem_id="retrieval_cards_frame", scale=1):
                context_html = gr.HTML()

    #overflow-y: auto; /* Add a vertical scrollbar if content exceeds container height */    

    # Register listeners
    imagebox = gr.State(None)

    # Quality Score
    quality_button.click(
        log_quality,
        [state, quality_value, model_selector],
        [quality_value, quality_button]
    )

    btn_list = [upvote_btn, downvote_btn, flag_btn, regenerate_btn, clear_btn]
    score_list = [quality_value, quality_button]
    
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
    # Callback REGEN
    regenerate_btn.click(
        regenerate, state, [state, chatbot, textbox, imagebox] + btn_list + score_list
    ).then(
        bot_response,
        [state],
        [state, chatbot, context_html] + btn_list + score_list,
    )
    # Callback CLEAR
    clear_btn.click(clear_history, None, [state, chatbot, textbox, imagebox] + btn_list + score_list)

    # When a new model is selected (event), clear history
    model_selector.change(
        clear_history, None, [state, chatbot, textbox, imagebox] + btn_list + score_list
    )


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

    return [state, model_selector]


def build_demo(models):
    with gr.Blocks(
        title="Assistente Filosofico",
        theme='Ama434/neutral-barlow', #gr.themes.Default(),
        css=block_css,
    ) as demo:
        # display arbitrary JSON output prettily
        url_params = gr.JSON(visible=False)

        state, model_selector = build_single_model_ui(models)

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
