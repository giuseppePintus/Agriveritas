#!/bin/bash

cd /home/jp
pip install jupyter
# python3 b .py
jupyter notebook --ip=0.0.0.0 --allow-root --no-browser --port=8501

# python3 agriveritasApp.py #2> errtry.txt 1> try.txt # smallFlask.py  
# #python3 f.py #1> try.txt 2> errtry.txt