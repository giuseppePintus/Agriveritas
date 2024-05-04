from huggingface_hub import login

import transformers

from vllm import LLM, SamplingParams


transformers.logging.set_verbosity(transformers.logging.INFO)

username = "JPIdeas"
password = "#Agriveritas2024"

HF_TOKEN = "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"
login(token=HF_TOKEN)

# Authenticate using transformers-cli
# result = transformers-cli login --username={username} --password={password}
# if result != "Login successful":
#     print("Failed to authenticate. Please check your credentials.")
#     exit(1)

llm = LLM(model="meta-llama/Meta-Llama-3-8B-Instruct", dtype="auto") #meta-llama/Meta-Llama-3-8B
# app.run(host='0.0.0.0', port=8501)