# Import os to set API key
import os
# Import OpenAI as main LLM service
from langchain_community.llms import VLLM
from huggingface_hub import login
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain import HuggingFacePipeline
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_core.messages import AIMessage, HumanMessage
from langchain.prompts import PromptTemplate
 
# Bring in streamlit for UI/app interface
from langchain.document_loaders import TextLoader, DirectoryLoader
import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer, AutoModelForCausalLM, TextIteratorStreamer
import transformers
import time
import torch
 
# Import PDF document loaders...there's other ones as well!
from langchain_community.document_loaders import PyPDFLoader
# Import chroma as the vector store 
from langchain_community.vectorstores import Chroma
 
from dotenv import load_dotenv
from huggingface_hub import login
 
# Load variables from the .env file
load_dotenv()
 
HF_TOKEN = os.getenv("HF_TOKEN")
login(token=HF_TOKEN)
 
@st.cache_data(show_spinner=False)
def get_memory():
    return ConversationBufferWindowMemory(
        memory_key='chat_history',
        k=5,
        return_messages=True,
        output_key='answer'
    )
@st.cache_resource(show_spinner=False)
def get_vectordb():
    print('Loading db..."')
    persist_directory = "db_3"
    encode_kwargs = {'normalize_embeddings': True} # set True to compute cosine similarity
 
    embeddings = HuggingFaceBgeEmbeddings(
        model_name='BAAI/bge-m3', #''BAAI/bge-base-en-v1.5',
        model_kwargs={'device': 'cuda'},
        #encode_kwargs=encode_kwargs
    )
 
    vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
 
    print('DONE!"')
    return vectordb
 
@st.cache_resource(show_spinner=False)
def get_tokenizer(model_id):
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    return tokenizer
 
@st.cache_resource(show_spinner=False)
def get_model(model_id):
    model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16 if "awq" in model_id.lower() else torch.bfloat16, trust_remote_code=True, device_map="auto", cache_dir="./prova", attn_implementation="flash_attention_2")
    return model
 
@st.cache_resource(show_spinner=False)
def get_vllm(model_id, stop_tokens=[]):
    llm = VLLM(
        model=model_id, #"disi-unibo-nlp/Mixtral-8x7B-Instruct-v0.1-AWQ", #"TheBloke/Mistral-7B-Instruct-v0.2-AWQ",#"", #"disi-unibo-nlp/Mixtral-8x7B-Instruct-v0.1-AWQ", #disi-unibo-nlp/Mixtral-8x7B-Instruct-v0.1-AWQ",
        trust_remote_code=True,  # mandatory for hf models
        max_new_tokens=512,
        temperature=0.9,
        gpu_memory_utilization=.9,
        top_p=1.0,
        top_k=10,
        download_dir = "./models",#"../preprocess/models",
        use_beam_search=False,
        dtype="auto",
        stop=stop_tokens,
        #vllm_kwargs={ "enforce_eager": True, "quantization": "awq", "max_model_len": 4096}, #
    )
    return llm
 
def memory2str(messages):
    memory_list = [
        f"Human: {mem.content}" if isinstance(mem, HumanMessage) \
        else f"AI: {mem.content}" for mem in messages
    ]
    memory_str = "\n".join(memory_list)
    return memory_str
 
if __name__ == "__main__":
 
    # Define Model ID
    model_id = "meta-llama/Meta-Llama-3-8B-Instruct" #"disi-unibo-nlp/Mixtral-8x7B-Instruct-v0.1-AWQ" #"TheBloke/Mistral-7B-Instruct-v0.2-AWQ"##"mistralai/Mistral-7B-Instruct-v0.2" "##"meta-llama/Llama-2-7b-chat-hf"
    tokenizer = get_tokenizer(model_id)
    terminators = [
        tokenizer.eos_token_id,
        tokenizer.convert_tokens_to_ids("<|eot_id|>")
    ]
    llm = get_vllm(model_id, terminators)
    vectordb = get_vectordb()
 
    retriever = vectordb.as_retriever(search_kwargs={"k": 5})
 
    prompt_template = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
 
Sei un assistente italiano. Rispondi sempre e solo in italiano alle domande in base al contesto dato e alla precedente storia della conversazione.<|eot_id|><|start_header_id|>user<|end_header_id|>
 
Contesto: 
{context}
 
Storia della conversazione:
{chat_history}
 
Domanda: 
{question} <|eot_id|><|start_header_id|>assistant<|end_header_id|>
 
"""
 
    prompt = PromptTemplate(
        template=prompt_template, input_variables=["context", "chat_history", "question"]
    )
 
    # conversational memory
    memory = ConversationBufferWindowMemory(
        memory_key='chat_history',
        k=5,
        return_messages=True,
        output_key='answer'
    )
    rag_pipeline = ConversationalRetrievalChain.from_llm(
        llm=llm, retriever=vectordb.as_retriever(), memory=memory,
        return_source_documents=True, 
        combine_docs_chain_kwargs={'prompt': prompt},
        rephrase_question=False
    )
 
 
    # session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            AIMessage(content="Ciao! Come posso aiutarti?"),
        ]
 
    st.title('RAG-Chat 📚')
 
    # conversation
    for message in st.session_state.chat_history:
        if isinstance(message, AIMessage):
                memory.chat_memory.add_ai_message(message.content)
        elif isinstance(message, HumanMessage):
                memory.chat_memory.add_user_message(message.content)
 
    # Create a text input box for the user
    def strem_output(out):
        for word in out.split(" "):
            yield word + " "
            time.sleep(0.05)
 
 
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Ciao! Come posso aiutarti?"}]

 
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
 
    if question := st.chat_input("Inserisci qui il tuo testo"):
        st.session_state.chat_history.append(HumanMessage(content=question))
        # Display user message in chat message container
        st.session_state.messages.append({"role": "user", "content": question})
 
        # Add user message to chat history
        st.chat_message("user").write(question)
 
        response = rag_pipeline.invoke({
            "question": question,
            "chat_history": memory2str(st.session_state.chat_history)}
        )
 
        out = response['answer'].strip()
        # check chat history
        # with open('history.txt','w') as f:
        #     #f.write(out)
        #     f.write(memory2str(st.session_state.chat_history))
        #     f.write("*"*50+'\n')
        st.session_state.chat_history.append(AIMessage(content=out))
 
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.write_stream(stream_output(out))
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": out})
        with st.sidebar:
            with st.expander('Contesti recuperati'):
                for i, el in enumerate(response['source_documents']):
                    st.write(f"### CONTESTO {i+1}\n")
                    st.write(el.page_content.strip() + '\n')