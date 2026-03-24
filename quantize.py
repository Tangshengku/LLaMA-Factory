from awq import AutoAWQForCausalLM
from transformers import AutoTokenizer
import json

model_path = "/home/tsk/LLaMA-Factory/output/qwen3_32b_chemi"
quant_path = "/home/tsk/LLaMA-Factory/output/qwen3_32b_chemi_8bit"
quant_config = {"zero_point": True, "q_group_size": 128, "w_bit": 8}

def load_wikitext():
    with open('/home/tsk/LLaMA-Factory/data/c4_demo.jsonl', 'r') as f:
        json_list = list(f)
    datas = []
    for json_str in json_list:
        data = json.loads(json_str)
        datas.append(data)
    return [text["text"] for text in datas if text["text"].strip() != '' and len(text["text"].split(' ')) > 20]

# Load model
model = AutoAWQForCausalLM.from_pretrained(
    model_path,
    low_cpu_mem_usage=True,
    use_cache=False,
)
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

# Quantize
model.quantize(tokenizer, quant_config=quant_config, calib_data=load_wikitext())

# Save quantized model
model.save_quantized(quant_path)
tokenizer.save_pretrained(quant_path)

print(f'Model is quantized and saved at "{quant_path}"')