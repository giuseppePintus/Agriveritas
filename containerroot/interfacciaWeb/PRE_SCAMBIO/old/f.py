

from vllm import LLM, SamplingParams

from huggingface_hub import notebook_login

import transformers
import sys


from flask import Flask, request, render_template
from flask.json import jsonify

from huggingface_hub import login
from pymilvus.model.hybrid import BGEM3EmbeddingFunction

from pymilvus import connections, Collection, utility, FieldSchema, DataType, CollectionSchema



HF_TOKEN = "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"
login(token=HF_TOKEN)
llm = LLM(model="meta-llama/Meta-Llama-3-8B-Instruct", dtype="auto") #meta-llama/Meta-Llama-3-8B
