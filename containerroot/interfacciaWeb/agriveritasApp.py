# # Llama3 w/ vLLM
# # Python

# from vllm import LLM, SamplingParams

# sampling_params = SamplingParams(temperature=0.8, top_p=0.95)
# llm = LLM(model="meta-llama/Meta-Llama-3-8B", dtype="auto")
# prompts = [
#     "Tell me about AI",
#     "Write a story about llamas",
#     "What is 291 - 150?",
#     "How much wood would a woodchuck chuck if a woodchuck could chuck wood?",
# ]
# prompt_template="[INST] {prompt} [/INST]"
# prompts = [prompt_template.format(prompt=prompt) for prompt in prompts]
# outputs = llm.generate(prompts, sampling_params)
# # Print the outputs.
# for output in outputs:
#     prompt = output.prompt
#     generated_text = output.outputs[0].text
#     print(f"Prompt: {prompt!r}, Generated text: {generated_text}")



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
    response_text = "Sono ancora una piccola versione puramente di prototipazione, non riesco ancora a soddisfare alcuna richiesta. Torna presto per delle novità!"
    
    if(regione == "noRegionSelected"):
        response_status = 1
        response_text = "Seleziona prima una regione, altrimenti non riesco ad aiutarti al meglio!"
    
    response_data = {"status" : response_status, "message" : response_text}

    return jsonify(response_data)


# "/" è la home page
# @app.route("/<name>")
# def home(name):
#     return render_template("agriveritas.html", name=name)

# @app.route("/subpage/<int:page>")

# # Llama3 w/ vLLM
# # Python
# from vllm import LLM, SamplingParams

# def computeIAResponse(queryAsk):
        
#     sampling_params = SamplingParams(temperature=0.8, top_p=0.95)
#     llm = LLM(model="meta-llama/Meta-Llama-3-8B", dtype="auto")
#     prompts = [
#         queryAsk
#     ]
#     prompt_template="[INST] {prompt} [/INST]"
#     prompts = [prompt_template.format(prompt=prompt) for prompt in prompts]
#     outputs = llm.generate(prompts, sampling_params)
#     lastToReturn = ""
#     # Print the outputs.
#     for output in outputs:
#         prompt = output.prompt
#         generated_text = output.outputs[0].text
#         toReturn = f"Prompt: {prompt!r}, Generated text: {generated_text}"
#         print(toReturn)
#         lastToReturn = toReturn

    
#     return lastToReturn



if __name__ == '__main__':
    app.run(port=8501)

