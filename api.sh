export CUDA_VISIBLE_DEVICES=4,5,6,7
export TRANSFORMERS_CACHE=/nfs/scistore19/alistgrp/huggingface/hub

API_PORT=8000 llamafactory-cli api examples/inference/qwen3_14B_lora_sft.yaml