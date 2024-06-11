from flask import Flask, render_template, request, jsonify


from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

from myModels import myModels

# tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
# model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
mmm = myModels()

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('chat.html')


@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    input = msg
    return get_Chat_response(input)

from pymilvus import connections, Collection, utility, FieldSchema, DataType, CollectionSchema

def get_Chat_response(text):
# # # # https://github.com/LazaUK/AOAI-LangChain-Milvus/blob/main/AOAI_langchain_Milvus.ipynb
    

    connections.connect("default", host="milvus-standalone", port="19530")   #host="milvus-standalone"

    # Load the existing collections
    risorsa_collection = Collection("RISORSA")
    chunk_collection = Collection("CHUNK")

    # # Load the collection
    risorsa_collection.load()
    chunk_collection.load()

    query_text = query

    embedded = mmm.getBGE().encode_documents([query_text])['dense'][0]

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
    result = mmm.getLLM().generate(prompts=[query])
    print(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8501, debug=True)