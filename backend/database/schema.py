"""
 @Author: jiran
 @Email: jiran214@qq.com
 @FileName: schema.py
 @DateTime: 2023/4/8 16:31
 @SoftWare: PyCharm
"""
from typing import List

from requestor.schemas import BiliNoteView
from schema import Document


class BiliNoteForMongo(BiliNoteView):
    documents: List[Document]
    summary_response: dict = None
    create_time: int
