"""
 @Author: jiran
 @Email: jiran214@qq.com
 @FileName: bilibili.py
 @DateTime: 2023/4/2 23:00
 @SoftWare: PyCharm
"""
import asyncio
import os

import aiohttp

import config
from parse.content import async_parse_content_to_file
from requestor.schemas import BiliAudioDownloadHrefParams, BiliNote
from log import crawler_logger
from utils.path import get_absolute_file_path
from utils.video_id_transform import bv2aid

logger = crawler_logger

headers: dict = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.41',
    'Cookie': config.cookie,
    'Referer': 'https://www.bilibili.com',
    # 'range': 'bytes=1-8000'
}


async def request_note_cc(session, subtitle_url):
    async with session.request("GET", url=subtitle_url) as resp:
        logger.info(f'请求状态:{resp.status}-subtitle_url:{subtitle_url}')
        json_data = await resp.json()
        return json_data


async def request_note_audio(session, params: BiliAudioDownloadHrefParams):
    if params.avid or params.bvid:
        audio_id = str(params.avid) or bv2aid(params.bvid)
    else:
        raise Exception('avid、bvid必填一个')

    audio_filepath = get_absolute_file_path(f'static', 'note', f'{audio_id}.mp3')

    if os.path.exists(audio_filepath):
        logger.info(f'mp3文件已存在:{audio_filepath}')
        return audio_filepath

    url = "https://api.bilibili.com/x/player/playurl"
    async with session.get(
            url=url,
            headers=headers,
            params=params.dict(exclude_none=True)
    ) as resp:
        logger.info(f'状态:{resp.status}-{url}-{params}')
        json_data = await resp.json()

        # 解析数据
        video_url = json_data['data']['dash']['video'][0]['baseUrl']
        audio_url = json_data['data']['dash']['audio'][0]['baseUrl']

    # 暂时只获取音频
    async with session.get(url=audio_url, headers=headers) as resp:
        logger.info(f'状态:{resp.status}-{audio_url}')
        if resp.status not in (200, 206):
            logger.exception('获取音频失败')
        return await async_parse_content_to_file(resp, audio_filepath)


async def request_note_detail(session, aid: int = None, bvid: str = None) -> BiliNote:
    params = {}
    if aid:
        params['aid'] = aid
    elif bvid:
        params['bvid'] = bvid
    else:
        raise 'avid、bvid必填一个'

    url = "https://api.bilibili.com/x/web-interface/view/detail"
    params = params

    async with session.get(
            url=url,
            params=params,
            headers=headers,
    ) as resp:
        logger.info(f'请求状态:{resp.status}-{url}-{str(params)}')
        json_data = await resp.json()
        return json_data


# async def get_kol_note_list(session, params: BiliKolNoteListParams) -> (int, List[int]):
#     url = "https://api.bilibili.com/x/space/wbi/arc/search"
#     async with session.get(
#             url=url,
#             params=params.dict(exclude_none=True),
#             headers=headers,
#     ) as resp:
#         logger.info(f'请求状态:{resp.status}-{url}-{str(params)}')
#         json_data = await resp.json()
#         data = check_json(json_data)['data']
#         aid_list = [note['aid'] for note in data['list']['vlist']]
#         aid_count = data['page']['count']
#         return aid_count, aid_list


async def aio_test():
    s = aiohttp.ClientSession()
    [await request_note_cc(s, 'https://www.baidu.com') for _ in range(10)]


if __name__ == '__main__':
    asyncio.run(aio_test())
