import asyncio
import aiohttp
import json
from datetime import datetime
import time
import requests

# 替换为你的API密钥和端点
API_KEY = ''
# API_URL = 'https://api.yourservice.com/v1/chat/completions'
API_URL = 'http://localhost:8000/v1/chat/completions'

HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {API_KEY}',
    # 'media_type': "text/event-stream"
}

# 示例请求体，可以根据实际情况修改
REQUEST_BODY = {
    'model': 'glm4',
    'messages': [{'role': 'user', 'content': '写一段1千字的作文'}],
    'max_tokens': 1200,
    'stream': True
}



async def fetch(session, payload, semaphore, idx):
    async with semaphore:
        request_start_time = time.time()
        # async with session.post(API_URL, json=payload, headers=HEADERS) as response:
        async with requests.post(API_URL, headers=HEADERS, json=payload, stream=True) as response:
            # end_time = datetime.now()
            time_end = time.time()
            total_data = []
            for chunk in await response.iter_lines(
                    chunk_size=20,
                    decode_unicode=False,
                    delimiter=b"\0"):
                if chunk:
                    data = json.loads(chunk.decdoe("utf-8"))
                    total_data.append(data)
                    
            return total_data
            
            
            # if response.status == 200:
            #     result = await response.json()
            #     # time_start = result['created']
            #     usage = result['usage']
            #     prompt_tokens = usage['prompt_tokens']
            #     total_tokens = usage['total_tokens']
            #     spend = time_end - request_start_time
            #     print("spend:", spend)
            #     print("speed:", total_tokens / spend)
                
                
            #     print(f"Response {idx + 1}: {json.dumps(result, ensure_ascii=False, indent=2)}")
            #     return result
            # else:
            #     error_message = {'error': response.status, 'message': await response.text()}
            #     print(f"Response {idx + 1} Error: {json.dumps(error_message, ensure_ascii=False, indent=2)}")
            #     return error_message

async def main():
    semaphore = asyncio.Semaphore(2)  # 限制并发量为20
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(4):  # 创建500个请求
            tasks.append(fetch(session, REQUEST_BODY, semaphore, i))
        responses = await asyncio.gather(*tasks)
        return responses

if __name__ == '__main__':
    asyncio.run(main())

