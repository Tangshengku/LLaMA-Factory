export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
FORCE_TORCHRUN=1 llamafactory-cli train examples/train_lora/qwen3_lora_sft.yaml