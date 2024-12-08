#!/bin/bash

cd /home/jp
pip install jupyter

jupyter notebook --ip=0.0.0.0 --allow-root --no-browser --port=8501
