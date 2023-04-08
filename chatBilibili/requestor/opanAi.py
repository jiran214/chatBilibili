"""
 @Author: jiran
 @Email: jiran214@qq.com
 @FileName: opanAi.py
 @DateTime: 2023/4/7 15:21
 @SoftWare: PyCharm
"""
import asyncio
import time
from contextlib import asynccontextmanager
from typing import AsyncIterator, List

import aiohttp
import openai
from aiohttp import TCPConnector
from openai import api_requestor

from contextvars import ContextVar

import requests.adapters
import urllib3

import config
from log import crawler_logger
from prompt.prompt_helpers import PromptHelper, GPT3dot5PromptHelper
from requestor.schemas import GPT35Params
from schema import Document

if config.proxy:
    openai.proxy = f'http://{config.proxy}/'

openai.api_key = config.api_key

logger = crawler_logger

s = requests.Session()


def make_session() -> requests.Session:
    s.verify = False
    s.proxies = {
        'http': f'http://{config.proxy}/',
        'https': f'http://{config.proxy}/'
    }
    urllib3.disable_warnings()
    s.trust_env = False
    # s.mount(
    #     "https://",
    #     requests.adapters.HTTPAdapter(max_retries=2),
    # )
    return s


@asynccontextmanager
async def aiohttp_session() -> AsyncIterator[aiohttp.ClientSession]:
    async with aiohttp.ClientSession(connector=TCPConnector(ssl=False)) as session:
        yield session

# 猴子补丁
if config.proxy:
    api_requestor._make_session = make_session
    api_requestor.aiohttp_session = aiohttp_session


def get_embedding(text_list: list, model="text-embedding-ada-002"):
    res = openai.Embedding.create(input=text_list, model=model)
    return res['data'][0]['embedding'], res['usage']['total_tokens']


def simple_get_embedding(text: str, model="text-embedding-ada-002"):
    res = openai.Embedding.create(input=[text], model=model)
    return res['data'][0]['embedding'], res['usage']['total_tokens']


async def async_get_embedding(text_list: list, model="text-embedding-ada-002"):
    res = await openai.Embedding.acreate(input=text_list, model=model)
    return res


async def async_get_embedding_with_documents(
        documents: List[Document], model="text-embedding-ada-002"
):
    resp = await openai.Embedding.acreate(input=[d.content for d in documents], model=model)
    for n, embedding in enumerate(resp['data']):
        documents[n].embedding = embedding['embedding']
    return documents


system_prompt_summary = '以下内容为多个句子组成的B站视频文案(空格分隔)，你是这个视频的作者名叫老蒋，请代入老蒋总结该文案的内容和观点\n'


def get_summary(text: str, model="gpt-3.5-turbo"):
    response = openai.ChatCompletion.create(**GPT35Params(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt_summary},
            {"role": "user", "content": text}
        ],
        temperature=1,
        # max_tokens
    ).dict(exclude_defaults=False, exclude_none=True))
    return response['choices'][0]['message']['content'], response['usage']['total_tokens']


def chat_with_3dot5(prompt_helper: GPT3dot5PromptHelper):
    response = openai.ChatCompletion.create(**GPT35Params(
        model=prompt_helper.model,
        # messages=prompt_helper.messages,
        messages=prompt_helper.messages,
        temperature=1,
        # max_tokens
    ).dict(exclude_defaults=False, exclude_none=True))
    return response['choices'][0]['message']['content'], response['usage']['total_tokens']


async def aio_test():
    # await asyncio.gather(
    #     *[async_get_embedding('你好世界') for _ in range(50)]
    # )
    [simple_get_embedding('你好世界') for _ in range(50)]

if __name__ == '__main__':
    t1 = time.time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(aio_test())
    print(time.time()-t1)
