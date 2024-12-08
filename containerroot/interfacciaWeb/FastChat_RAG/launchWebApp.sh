# #!/bin/bash
# MODEL_NAME="microsoft/Phi-3-mini-4k-instruct"
# #MODEL_NAME="meta-llama/Meta-Llama-3-8B-Instruct"

# # Start controller
# python3 -m fastchat.serve.controller 1>/dev/null 2>&1 &

# # Start worker
# CUDA_VISIBLE_DEVICES=1 python3 -m fastchat.serve.model_worker --model-path $MODEL_NAME 1>/dev/null 2>&1 &

# echo "----------------------------------------------------------------"
# echo "Testing everything is fine"
# CUDA_VISIBLE_DEVICES=1  python3 -m fastchat.serve.test_message --model-name $MODEL_NAME
# echo "----------------------------------------------------------------"





# # Multiple models
# # Phi3
# #CUDA_VISIBLE_DEVICES=0 python3 -m fastchat.serve.model_worker --model-path microsoft/Phi-3-mini-4k-instruct --controller http://localhost:21001 --port 31000 --worker http://localhost:31000 >logs/worker_phi_logs 2>&1 &

# #CUDA_VISIBLE_DEVICES=1 python3 -m fastchat.serve.model_worker --model-path microsoft/Phi-3-mini-4k-instruct --controller http://localhost:21001 --port 31001 --worker http://localhost:31001 >logs/worker_phi_logs 2>&1 &

# # Gemma
# #CUDA_VISIBLE_DEVICES=1 python3 -m fastchat.serve.model_worker --model-path google/gemma-2b-it --controller http://localhost:21001 --port 31001 --worker http://localhost:31001 >logs/worker_gemma_logs 2>&1 &

# #CUDA_VISIBLE_DEVICES=0 python3 -m fastchat.serve.model_worker --model-path google/gemma-2b-it --controller http://localhost:21001 --port 31000 --worker http://localhost:31000 >logs/worker_gemma_logs 2>&1 &




# #CUDA_VISIBLE_DEVICES=0 python3 -m fastchat.serve.model_worker --model-path google/gemma-2b-it --controller http://localhost:21001 --port 31000 --worker http://localhost:31000 1>/dev/null 2>&1 &



# #gradio_web_server_asynch

# -----------------------------------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------------------------------

# # #MODEL_NAME="microsoft/Phi-3-mini-4k-instruct"
# # MODEL_NAME="meta-llama/Meta-Llama-3-8B-Instruct"

# # if [[ -z $1 ]] ;
# # then echo "A"
# #     echo "B"
    
# #     # python3 -m fastchat.serve.controller --host 127.0.0.1 --port 21001 1>/dev/null 2>&1 &

# #     # #CUDA_VISIBLE_DEVICES=1 python3 -m fastchat.serve.model_worker --model-path google/gemma-2b-it --controller http://127.0.0.1:21001 --host 127.0.0.1 --port 31000 --worker http://127.0.0.1:31000 >logs/worker_gemma_logs 2>&1 &
# #     # #logs/worker_gemma_logs
# #     # CUDA_VISIBLE_DEVICES=2 python3 -m fastchat.serve.model_worker --model-path ${MODEL_NAME} --controller http://127.0.0.1:21001 --host 127.0.0.1 --port 31001 --worker http://127.0.0.1:31001 > /dev/null 2>&1 &
# # fi


# # # # ---------------------------------
# # # echo "Launching web server"

# # # python3 -m fastchat.serve.gradio_web_server_asynch #fastchat.serve.gradio_web_server_philosophia



# ---------------------------------
# ---------------------------------
# ---------------------------------


MODEL_NAME="meta-llama/Meta-Llama-3-8B-Instruct"
#MODEL_NAME="microsoft/Phi-3-mini-4k-instruct"

if [[ ! -z $1 ]]; then
  echo "Launch controller"
  # Start the FastChat controller in the background
  python3 -m fastchat.serve.controller --host 127.0.0.1 --port 21001 1>/dev/null 2>&1 &

  echo "Launch worker"
  # Start the FastChat model worker for Meta-Llama in the background
  CUDA_VISIBLE_DEVICES=2 python3 -m fastchat.serve.model_worker --model-path ${MODEL_NAME} --controller http://127.0.0.1:21001 --host 127.0.0.1 --port 31001 --worker http://127.0.0.1:31001 1> /FastChat_RAG/logs/worker40.txt 2>&1 &
fi

ps
sleep 1

# ---------------------------------
echo "Launching web server"

# Start the FastChat Gradio web server
python3 -m fastchat.serve.gradio_web_server_asynch 
# Or use the Philosophia variant if desired:
# python3 -m fastchat.serve.gradio_web_server_philosophia