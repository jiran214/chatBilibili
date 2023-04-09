"""
 @Author: jiran
 @Email: jiran214@qq.com
 @FileName: json.py
 @DateTime: 2023/4/7 14:49
 @SoftWare: PyCharm
"""
from log import crawler_logger
from requestor.schemas import BiliNote

logger = crawler_logger


def check_json(resp):
    if resp['code'] != 0:
        logger.error(f"返回json异常，错误信息:{resp}")
    return resp


def get_note_cc_content(json_data):
    content_list = [body['content'] for body in json_data['body']]
    return content_list


def get_note_detail(json_data):
    data = check_json(json_data)['data']
    return BiliNote(**data)


def get_note_detail_subtitle(json_data) -> (str, BiliNote):
    note_schema = get_note_detail(json_data)
    if subtitle := note_schema.View.subtitle['list']:
        return subtitle[0]['subtitle_url'], note_schema
    else:
        return None, note_schema
