from openai import OpenAI
client = OpenAI(api_key="0",base_url="http://0.0.0.0:8000/v1")
messages = [{"role": "user", "content": "我想问一些和化工安全相关的问题"}]
result = client.chat.completions.create(messages=messages, 
                                        model="/home/tsk/LLaMA-Factory/ckpt/qwen3-4B-ins",
                                        )
print(result.choices[0].message)

# repetition_penalty=1.1,
# presence_penalty=1.1
