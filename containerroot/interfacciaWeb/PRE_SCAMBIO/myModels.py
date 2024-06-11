# b.py
import time
from langchain_community.llms import VLLM
from transformers import AutoTokenizer
import os
from pymilvus.model.hybrid import BGEM3EmbeddingFunction
from huggingface_hub import login, snapshot_download

class myModels:
    LLM = None
    BGE = None

    def __init__(self):
        # Initialize the LLM
        HF_TOKEN = "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"
        model_id = "meta-llama/Meta-Llama-3-8B-Instruct" # "meta-llama/Meta-Llama-1-3B-Instruct" 
        login(token=HF_TOKEN)
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        terminators = [
            tokenizer.eos_token_id,
            tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]

        gpu_memory_utilization = 0.5
        max_num_seqs = 8

        self.LLM = VLLM(
            model=model_id,
            trust_remote_code=True,
            max_new_tokens=512,
            temperature=0.9,
            gpu_memory_utilization=gpu_memory_utilization,
            max_num_seqs = max_num_seqs,
            top_p=1.0,
            top_k=10,
            # download_dir="./models",
            use_beam_search=False,
            dtype="auto",
            stop=terminators,
            vllm_kwargs={"enforce_eager": True},
        )

        # Initialize the BGE
        # snapshot_download(repo_id='BAAI/bge-m3', local_dir="bge-m3")
        self.BGE = BGEM3EmbeddingFunction(
            #cache_dir = "bge-m3",
            model_name='BAAI/bge-m3',
            device='cuda',
            use_fp16=True
        )
        time.sleep(10)

    def getLLM(self):
        return self.LLM

    def getBGE(self):
        return self.BGE