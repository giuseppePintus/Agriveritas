from flask import Flask, request, render_template
from flask.json import jsonify
import datetime


app = Flask(__name__)

# Set the Flask environment to development
app.config['ENV'] = 'development'
app.config['DEBUG'] = True

# "/" è la home page
@app.route("/")
def home():
    return render_template("agriveritas.html")

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
    # asked = query_text
    # response_text = "CIAO"

    if(regione == "noRegionSelected"):
        response_status = 1
        response_text = "Seleziona prima una regione, altrimenti non riesco ad aiutarti al meglio!"
    
    response_data = {"status" : response_status, "message" : response_text, "prompt": asked}

    # current_date = datetime.date.today()
    # print(type(current_date))

    return jsonify(response_data)



from myModels import myModels

myModelsC = None

@app.before_first_request
def initialize_app():
    global myModelsC
    myModelsC = myModels()    

from pymilvus import connections, Collection, utility, FieldSchema, DataType, CollectionSchema

import random
from itertools import chain

def generateRandomEmbedding(amount):
    return [random.uniform(0.0, 1.0) for _ in range(amount)]


def getBGE():
    return myModelsC.getBGE()

def getLLM():
    return myModelsC.getLLM()


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
    Di seguito quindi avrai un quesito e delle possibili fonti che possono aiutare a risolvere il dubbio
    Domanda: {domanda}
    Possibili fonti: 
    {risposta}
    È di fondamentale importanza che tu risponda in italiano e usando il più possibile il lessico tecnico agronomico
    """

    print(initLog)


    query = initLog
    # input_ids = tokenizer.encode([query], return_tensors="pt")ù
    response_text = ""
    try:
        result = getLLM().generate(prompts=[query])
        if result and result.generations:
            response_text = result.generations[0][0].text
    except Exception as e:
        response_text = "Apologies, I encountered an error and was unable to generate a response."
        print(f"Error in manageSmartResponse: {e}")
    #result = getLLM().generate(prompts=[query])[0].text()
    print(response_text)

    return query, response_text


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8501, debug=True)
