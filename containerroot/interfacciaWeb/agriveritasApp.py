# # Llama3 w/ vLLM
# # Python

from vllm import LLM, SamplingParams

from huggingface_hub import notebook_login

import transformers



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
    last_update_date = current_date.strftime("%Y/%m/%d")
    return jsonify({"last_update_date": last_update_date})


@app.route("/IAresponse/<regione>")
def IAResponse(regione="noRegionSelected"):
    response_status = 0
    query = "Make a nice greetings message"
    response_text = manageSmartResponse(query)
    
    if(regione == "noRegionSelected"):
        response_status = 1
        response_text = "Seleziona prima una regione, altrimenti non riesco ad aiutarti al meglio!"
    
    response_data = {"status" : response_status, "message" : response_text}

    return jsonify(response_data)


llm = None

def manageSmartResponse(query):
    sampling_params = SamplingParams(temperature=0.8, top_p=0.95)
    
    prompts = [
        query
    ]
    prompt_template="[INST] {prompt} [/INST]"
    prompts = [prompt_template.format(prompt=prompt) for prompt in prompts]
    outputs = llm.generate(prompts, sampling_params)
    # Print the outputs.
    for output in outputs:
        prompt = output.prompt
        generated_text = output.outputs[0].text
        print(f"Prompt: {prompt!r}, Generated text: {generated_text}")
    
    return outputs[0].outputs[0].text



# "/" è la home page
# @app.route("/<name>")
# def home(name):
#     return render_template("agriveritas.html", name=name)

# @app.route("/subpage/<int:page>")



if __name__ == '__main__':

    transformers.logging.set_verbosity(transformers.logging.INFO)

    username = "JPIdeas"
    password = "#Agriveritas2024"

    # Authenticate using transformers-cli
    # result = transformers-cli login --username={username} --password={password}
    # if result != "Login successful":
    #     print("Failed to authenticate. Please check your credentials.")
    #     exit(1)

    llm = LLM(model="meta-llama/Meta-Llama-3-8B", dtype="auto")
    app.run(host='0.0.0.0', port=8501)
    # transformers.logging.set_verbosity(transformers.logging.INFO)

    # username = "JPIdeas"
    # password = "#Agriveritas2024"

    # transformers.login(username, password)
    # llm = LLM(model="meta-llama/Meta-Llama-3-8B", dtype="auto")
    # app.run(host='0.0.0.0', port=8501)
    

