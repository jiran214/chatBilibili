"""
 @Author: jiran
 @Email: jiran214@qq.com
 @FileName: session.py
 @DateTime: 2023/4/7 23:29
 @SoftWare: PyCharm
"""
from contextlib import asynccontextmanager

import aiohttp


@asynccontextmanager
async def _make_session():
    async with aiohttp.ClientSession() as s:
        yield s