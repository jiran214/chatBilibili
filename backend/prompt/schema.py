"""
 @Author: jiran
 @Email: jiran214@qq.com
 @FileName: schema.py
 @DateTime: 2023/4/8 19:44
 @SoftWare: PyCharm
"""
from pydantic import BaseModel


class SummaryConfig(BaseModel):
    emoji_show: bool = False
    sentence_count: int = 7
    words_count: int = 15
    language: str = 'Chinese'
