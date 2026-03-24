from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

model_name = "/root/.cache/modelscope/hub/models/Qwen/Qwen3-32B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    load_in_8bit=True,          # 启用 8-bit 量化
    device_map="auto"
)

# 保存量化后的模型（仅保存配置和权重引用，实际量化在加载时进行）
model.save_pretrained("/home/tsk/LLaMA-Factory/output/qwen3_32b_8bit")
tokenizer.save_pretrained("/home/tsk/LLaMA-Factory/output/qwen3_32b_8bit")