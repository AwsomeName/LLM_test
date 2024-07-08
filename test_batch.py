import asyncio
import aiohttp
import json
import math
from datetime import datetime
import time
import random
from typing import Tuple

# 替换为你的API密钥和端点
API_KEY = 'Jq3pNwtTCKmybjjCzu3Od5tbjO7jL4kfcvLeuuToch4'
# API_URL = 'https://api.yourservice.com/v1/chat/completions'
# API_URL = 'http://127.0.0.1:8003/v1/chat/completions'
# API_URL = "http://218.60.52.4:8904/v1/chat/completions"
API_URL = "http://218.60.52.4:8905/v1/chat/completions"

max_req = 80  # 创建的请求数量
max_multi = 20 # 并发量
mean_input_tokens = 100
# stddev_input_tokens = 10
num_output_tokens = 200
max_token = 300
# max_token = mean_input_tokens + num_output_tokens
    
HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': f'bearer Jq3pNwtTCKmybjjCzu3Od5tbjO7jL4kfcvLeuuToch4',
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
REQUEST_BODY = {
    'model': 'chatglm2-6b',
    'messages': [{'role': 'user', 'content': """ Randomly stream lines from the following text with 1200 output tokens. Don't generate eos tokens:

Shall I compare thee to a summer's day?
Thou art more lovely and more temperate:
Rough winds do shake the darling buds of May,
And summer's lease hath all too short a date:
Sometime too hot the eye of heaven shines,
And often is his gold complexion dimm'd;
And every fair from fair sometime declines,
By chance or nature's changing course untrimm'd;
But thy eternal summer shall not fade
Nor lose possession of that fair thou owest;
Nor shall Death brag thou wander'st in his shade,
When in eternal lines to time thou growest:
So long as men can breathe or eyes can see,
So long lives this and this gives life to thee.
Then let not winter's ragged hand deface
In thee thy summer, ere thou be distill'd:
Make sweet some vial; treasure thou some place
With beauty's treasure, ere it be self-kill'd.
That use is not forbidden usury,
Which happies those that pay the willing loan;
That's for thyself to br"""}],
    # 'max_tokens': 200,
    # 'stream': True
}

total_res = {}
        
async def fetch(session, payload, semaphore, idx):
    
    async with semaphore:
        print("idx run:", idx)
        request_start_time = time.time()
        total_res[idx]['req_start'] = request_start_time
        async with session.post(API_URL, json=payload, headers=HEADERS) as response:
                
            total_tokens = 0
            res = ""
            if response.status == 200:
                result = await response.json()
                print("res:", result)
                usage = result['usage']
                prompt_tokens = usage['prompt_tokens']
                total_tokens = usage['total_tokens']
                rec_time = time.time()
                total_res[idx]['spend'] = rec_time - request_start_time
                total_res[idx]['ttft'] = 0
                total_res[idx]["gen_tokens"] = "a" * (total_tokens - prompt_tokens)
                return
            else:
                print(response)
                    


async def main():
    
    semaphore = asyncio.Semaphore(max_multi)  # 限制并发量为20
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(max_req):  # 创建500个请求
            total_res[i] = {}
            prompt = prompts[i]
            total_res[i]["pmpt_len"] = len(prompt)
            # REQUEST_BODY = {
            #     'model': 'chatglm2-6b',
            #     'messages': [{'role': 'user', 'content': prompt}],
            #     # 'max_tokens': max_token,
            #     # 'stream': True
            # }
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
        
    list_speed = sorted(list_speed, reverse=True)
    list_ttft = sorted(list_ttft)
    list_tpot = sorted(list_tpot)
    p80_idx = int(len(total_res) * 0.8)
    print("speed_p80:", list_speed, list_speed[p80_idx])
    print("ttft_p80:", list_ttft, list_ttft[p80_idx])
    print("tpot_p80", list_tpot, list_tpot[p80_idx])
