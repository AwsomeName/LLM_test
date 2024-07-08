import asyncio
import aiohttp
import json
import math
from datetime import datetime
import time
import random
from typing import Tuple

# 替换为你的API密钥和端点
API_KEY = ''
# API_URL = 'https://api.yourservice.com/v1/chat/completions'
API_URL = 'http://localhost:8000/v1/chat/completions'

max_req = 400  # 创建的请求数量
max_multi = 256 # 并发量
mean_input_tokens = 1000
# stddev_input_tokens = 10
num_output_tokens = 200
max_token = 1300
# max_token = mean_input_tokens + num_output_tokens
    
HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {API_KEY}',
}

prompts = []


def randomly_sample_sonnet_lines_prompt(
    prompt_tokens_mean: int = 550,
    expect_output_tokens: int = 150,
):
    sonnet_path = "./sonnet.txt"
    with open(sonnet_path, "r") as f:
        sonnet_lines = f.readlines()
    
    prompt = (
        "Randomly stream lines from the following text "
        f"with {expect_output_tokens} output tokens. "
        "Don't generate eos tokens:\n\n"
    )
    
    remaining_prompt_tokens = prompt_tokens_mean - len(prompt)
    sampling_lines = True
    while sampling_lines:
        for line in sonnet_lines:
            line_to_add = line
            if remaining_prompt_tokens - len(line_to_add) < 0:
                # This will cut off a line in the middle of a word, but that's ok since an
                # llm should be able to handle that.
                line_to_add = line_to_add[: int(math.ceil(remaining_prompt_tokens))]
                sampling_lines = False
                prompt += line_to_add
                break
            prompt += line_to_add
            remaining_prompt_tokens -= len(line_to_add)
    return prompt
       
# REQS = []

for i in range(max_req):
    prompt = randomly_sample_sonnet_lines_prompt(
        prompt_tokens_mean=mean_input_tokens,
        expect_output_tokens=num_output_tokens,
    )
    prompts.append(prompt)
 


# 示例请求体，可以根据实际情况修改
# REQUEST_BODY = {
#     'model': 'glm4',
#     'messages': [{'role': 'user', 'content': '写一段100字的作文'}],
#     'max_tokens': 200,
#     'stream': True
# }

total_res = {}
        
async def fetch(session, payload, semaphore, idx):
    
    async with semaphore:
        print("idx: ", idx)
        request_start_time = time.time()
        total_res[idx]['req_start'] = request_start_time
        async with session.post(API_URL, json=payload, headers=HEADERS) as response:
                
            total_tokens = 0
            res = ""
            if response.status == 200:
                while True:
                    rec_time = time.time()
                    if "ttft" not in total_res[idx]:
                        total_res[idx]['ttft'] = rec_time - request_start_time
                    chunk = await response.content.readany()
                    # print("raw chunk:", chunk)
                    lines = chunk.split(b"\n\n")
                    for line in lines:
                        if line:
                            # tokens = max(0, len(line) - 199)
                            # total_tokens += tokens
                            
                            # print("len:line:", len(line))
                            line = line.strip()[6:].decode('utf-8')
                            if line == "[DONE]":
                                continue
                            data = json.loads(line)
                            # print(data['choices'][0]['delta'])
                            try:
                                res += data['choices'][0]['delta']['content']
                                # print(idx, "len_data:", len(line), len(data['choices'][0]['delta']['content']), data['choices'][0]['delta']['content'])
                            except:
                                pass
                            # print(idx, "~data:", data)
                    if not chunk:
                        # total_res[idx]['tokens'] = total_tokens
                        total_res[idx]['spend'] = rec_time - request_start_time
                        total_res[idx]["gen_tokens"] = res
                        return
                    


async def main():
    
    semaphore = asyncio.Semaphore(max_multi)  # 限制并发量为20
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(max_req):  # 创建500个请求
            total_res[i] = {}
            prompt = prompts[i]
            total_res[i]["pmpt_len"] = len(prompt)
            REQUEST_BODY = {
                'model': 'glm4',
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': max_token,
                'stream': True
            }
            # print("req:", REQUEST_BODY)
            tasks.append(fetch(session, REQUEST_BODY, semaphore, i))
        responses = await asyncio.gather(*tasks)
        return responses

if __name__ == '__main__':
    asyncio.run(main())
    # print(total_res)
    list_ttft = []
    list_tpot = []
    list_speed = []
    
    
    for idx in total_res:
        print(idx, total_res[idx])
        print(idx, len(total_res[idx]['gen_tokens']))
        
        spend = total_res[idx]['spend']
        tokens = len(total_res[idx]['gen_tokens']) + 1
        tpot = spend / tokens
        speed = tokens / spend
        
        list_ttft.append(total_res[idx]['ttft'])
        list_tpot.append(tpot)
        list_speed.append(speed)
        
        
        # print(idx, total_res[idx]['gen_tokens'])
        # print(prompts[i])
        # print(len(prompts[i]))
        
    list_speed = sorted(list_speed, reverse=False)
    list_ttft = sorted(list_ttft)
    list_tpot = sorted(list_tpot)
    p80_idx = int(len(total_res) * 0.8)
    print("speed_p80:", list_speed, list_speed[p80_idx])
    print("ttft_p80:", list_ttft, list_ttft[p80_idx])
    print("tpot_p80", list_tpot, list_tpot[p80_idx])
