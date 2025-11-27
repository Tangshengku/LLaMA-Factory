export CUDA_VISIBLE_DEVICES=4,5,6,7
export TRANSFORMERS_CACHE=/nfs/scistore19/alistgrp/huggingface/hub

llamafactory-cli chat examples/inference/qwen3_14B_lora_sft.yaml
# llamafactory-cli chat examples/inference/qwen3_lora_sft.yaml