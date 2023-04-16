"""
 @Author: jiran
 @Email: jiran214@qq.com
 @FileName: content.py
 @DateTime: 2023/4/7 14:49
 @SoftWare: PyCharm
"""

import aiofiles

from log import crawler_logger

logger = crawler_logger


async def parse_content_to_file(resp, path):
    with open(path, 'wb') as f:
        while True:
            chunk = await resp.content.read(1024)
            if not chunk:
                logger.info(f'not chunk，文件{path}写入完成')
                break
            f.write(chunk)
        return path


async def async_parse_content_to_file(resp, path):
    # https://blog.csdn.net/sunt2018/article/details/107716615
    async with aiofiles.open(path, mode="wb") as fp:
        while True:
            chunk = await resp.content.read(1024)
            if not chunk:
                logger.info(f'not chunk，文件{path}写入完成')
                break
            await fp.write(chunk)
        return path
