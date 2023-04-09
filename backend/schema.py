"""
 @Author: jiran
 @Email: jiran214@qq.com
 @FileName: schema.py
 @DateTime: 2023/4/7 17:08
 @SoftWare: PyCharm
"""
from typing import List, NewType

from pydantic import BaseModel

Vector = NewType('Vector', List[float])


class Document(BaseModel):
    hash_id: int
    content: str
    embedding: Vector = None
    filed: str = 'caption'
    # source: str
