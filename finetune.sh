export CUDA_VISIBLE_DEVICES=2,6
FORCE_TORCHRUN=1 llamafactory-cli train examples/train_lora/qwen3_lora_sft.yaml