#!/bin/bash
cd /home/jp/milvusAttemp
python3 connectMilvus.py 2>&1 | tee stdout.txt | tee stderr.txt