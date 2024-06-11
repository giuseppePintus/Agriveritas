# # Llama3 w/ vLLM
# # Python

from flask import Flask, request, render_template
from flask.json import jsonify

app = Flask(__name__)


# Set the Flask environment to development
app.config['ENV'] = 'development'
app.config['DEBUG'] = True

# "/" è la home page
@app.route("/")
def home():
    return render_template("agriveritas.html")

import datetime

@app.route("/initInfo")
def get_init_info():
    current_date = datetime.date.today()
    print(type(current_date))
    last_update_date = current_date.strftime("%Y/%m/%d")

    return jsonify({"last_update_date": last_update_date})


@app.route("/IAresponse/<regione>")
def IAResponse(regione="noRegionSelected"):
    response_status = 0
    
    # Get the 'qt' query parameter
    query_text = request.args.get('qt')
    
    # If the 'qt' parameter is not provided, use the default query
    if not query_text:
        query_text = "Cosa deve fare un Imprenditore Agricolo?"
    
    asked, response_text = manageSmartResponse(query_text)

    if(regione == "noRegionSelected"):
        response_status = 1
        response_text = "Seleziona prima una regione, altrimenti non riesco ad aiutarti al meglio!"
    
    response_data = {"status" : response_status, "message" : response_text, "prompt": asked}

    # current_date = datetime.date.today()
    # print(type(current_date))

    return jsonify(response_data)


from myModels import BGE, LLM


# from langchain_community.llms import VLLM
# from transformers import AutoTokenizer
# import os

# from vllm import LLM, SamplingParams

# from pymilvus.model.hybrid import BGEM3EmbeddingFunction

# from huggingface_hub import login, snapshot_download
# from pymilvus.model.hybrid import BGEM3EmbeddingFunction

from pymilvus import connections, Collection, utility, FieldSchema, DataType, CollectionSchema

import random
from itertools import chain

def generateRandomEmbedding(amount):
    return [random.uniform(0.0, 1.0) for _ in range(amount)]


def getBGE():
    return None #BGE
    # snapshot_download(repo_id='BAAI/bge-m3',local_dir="bge-m3")
    # bge_m3_ef = BGEM3EmbeddingFunction(
    #     model_name='BAAI/bge-m3',
    #     device='cuda',
    #     use_fp16=True
    # )
    # return bge_m3_ef

def getLLM():
    return None #LLM
    # HF_TOKEN = "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"
    # model_id = "meta-llama/Meta-Llama-3-8B-Instruct"
    # login(token=HF_TOKEN)
    # tokenizer = AutoTokenizer.from_pretrained(model_id)
    # terminators = [
    #     tokenizer.eos_token_id,
    #     tokenizer.convert_tokens_to_ids("<|eot_id|>")
    # ]

    # # Decrease gpu_memory_utilization
    # gpu_memory_utilization = 0.7  # Try a lower value, e.g., 0.6

    # # Enforce eager mode
    # os.environ["TF_ENABLE_EAGER_EXECUTION"] = "1"

    # # Reduce max_num_seqs
    # max_num_seqs = 16  # Try a lower value, e.g., 8

    # llm = VLLM(
    #     model=model_id,
    #     trust_remote_code=True,  # mandatory for hf models
    #     max_new_tokens=512,
    #     temperature=0.9,
    #     gpu_memory_utilization=gpu_memory_utilization,
    #     top_p=1.0,
    #     top_k=10,
    #     download_dir="./models",
    #     use_beam_search=False,
    #     dtype="auto",
    #     stop=terminators,
    #     vllm_kwargs={"enforce_eager": True}, #, "quantization": "awq", "max_model_len": 4096
    # )
    # return llm

# ...

def manageSmartResponse(query):
    # # # # https://github.com/LazaUK/AOAI-LangChain-Milvus/blob/main/AOAI_langchain_Milvus.ipynb
    
    connections.connect("default", host="milvus-standalone", port="19530")   #host="milvus-standalone"

    # Load the existing collections
    risorsa_collection = Collection("RISORSA")
    chunk_collection = Collection("CHUNK")

    # # Load the collection
    risorsa_collection.load()
    chunk_collection.load()

    query_text = query

    embedded = getBGE().encode_documents([query_text])['dense'][0]

    searchingChunk = embedded.tolist() # generateRandomEmbedding(1024)
    
    # print("--> " + str(searchingChunk))
    # print(f"Vector dimension of searchingChunk: {len(searchingChunk)}")
    # print(f"Vector dimension of embedded: {embedded.shape}")
    # collection_info = chunk_collection.describe()
    #print(f"Vector dimension of the 'embedding' field: {collection_info.fields['embedding'].dim}")

    results = chunk_collection.search(
        data = [searchingChunk], 
        anns_field = "embedding", 
        limit=2, 
        param={
            "metric_type": "L2", 
            "params": {
                "nprobe": 10,
                },
            "topk": 5
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

    domanda = query_text #"METTI QUI LA DOMANDA"

    regione = "Emilia Romagna"
    initLog = f"""Sei un esperto funzionario della AgEA dell' {regione} e il tuo compito è assistere delle persone che ti pongono delle domande
    Di seguito quindi avrai un quesito e delle possibili risposte che possono risolvere il dubbio
    Domanda: {domanda}
    Possibili risposte: 
    {risposta}
    È di fondamentale importanza che tu risponda in italiano e usando il più possibile il lessico tecnico agronomico
    """

    print(initLog)


    query = initLog
    # input_ids = tokenizer.encode([query], return_tensors="pt")
    result = getLLM().generate(prompts=[query])
    print(result)

    return initLog, result


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8501, debug=True)