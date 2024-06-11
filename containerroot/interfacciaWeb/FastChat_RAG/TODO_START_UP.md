# Start Gradio 

![server arch](assets/server_arch.png)

```
docker run --name rag_gradio_container -p 19530:19530 -p 37338:7860 --gpus=all --ipc=host -v ~/FastChat_RAG:/FastChat_RAG -v ~/useful_cmd:/useful_cmd -it rag_chatbot_image /bin/bash
```

We must start the controller for handling the requests and the model worker that is responsible for the inference mode.

__1__ Launch the controller
```
python3 -m fastchat.serve.controller
````
This controller manages the distributed workers. By default, it will run at http://localhost:21001


__2__ Launch the model worker(s)
```
python3 -m fastchat.serve.model_worker --model-path lmsys/vicuna-7b-v1.5
```
Wait until the process finishes loading the model and you see "Uvicorn running on ...". The model worker will register itself to the controller.


Launch the Gradio web server
```
python3 -m fastchat.serve.gradio_web_server
```
This is the user interface that users will interact with.


### (Optional): Advanced Features, Scalability, Third Party UI
You can
- register multiple model workers to a single controller, which can be used for serving a single model with higher throughput
- serving multiple models at the same time. When doing so, allocate different GPUs and ports for different model workers as shown below
```
# worker 0
CUDA_VISIBLE_DEVICES=0 python3 -m fastchat.serve.model_worker --model-path lmsys/vicuna-7b-v1.5 --controller http://localhost:21001 --port 31000 --worker http://localhost:31000

# worker 1
CUDA_VISIBLE_DEVICES=1 python3 -m fastchat.serve.model_worker --model-path lmsys/fastchat-t5-3b-v1.0 --controller http://localhost:21001 --port 31001 --worker http://localhost:31001
```

## Multi-Tab Chat

You can also launch a multi-tab gradio server, which includes the Chatbot Arena tabs.
```
python3 -m fastchat.serve.gradio_web_server_multi
```
The default model worker based on huggingface/transformers has great compatibility but can be slow. If you want high-throughput batched serving, you can try vLLM integration.


## vLLM Serving
When you launch a model worker, replace the normal worker (`fastchat.serve.model_worker`) with the vLLM worker (`fastchat.serve.vllm_worker`). All other commands such as controller and gradio web server are kept the same.
```
python3 -m fastchat.serve.vllm_worker --model-path lmsys/vicuna-7b-v1.5
```

If you see tokenizer errors, try
```
python3 -m fastchat.serve.vllm_worker --model-path lmsys/vicuna-7b-v1.5 --tokenizer hf-internal-testing/llama-tokenizer
```

If you use an AWQ quantized model, try
```
python3 -m fastchat.serve.vllm_worker --model-path TheBloke/vicuna-7B-v1.5-AWQ --quantization awq
```


## Low-bit Model

If you do not have enough memory, you can enable 8-bit compression by adding `--load-8bit` to commands above. This can reduce memory usage by around half with slightly degraded model quality. It is compatible with the CPU, GPU, and Metal backend.

Vicuna-13B with 8-bit compression can run on a single GPU with 16 GB of VRAM, like an Nvidia RTX 3090, RTX 4080, T4, V100 (16GB), or an AMD RX 6800 XT.
```
python3 -m fastchat.serve.cli --model-path lmsys/vicuna-7b-v1.5 --load-8bit
```
In addition to that, you can add --cpu-offloading to commands above to offload weights that don't fit on your GPU onto the CPU memory. This requires 8-bit compression to be enabled and the bitsandbytes package to be installed, which is only available on linux operating systems.

### Our script
```
python3 -m fastchat.serve.cli --model-path meta-llama/Meta-Llama-3-8B-Instruct --load-8bit

python3 -m fastchat.serve.cli --model-path microsoft/Phi-3-mini-4k-instruct
```