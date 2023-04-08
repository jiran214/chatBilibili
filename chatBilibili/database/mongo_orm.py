"""
 @Author: jiran
 @Email: jiran214@qq.com
 @FileName: mongo_orm.py
 @DateTime: 2023/4/8 16:50
 @SoftWare: PyCharm
"""
from typing import List, Optional

import pymongo
from pymongo.collection import Collection

from database.mongo import DBManager
from database.schema import BiliNoteForMongo


class NoteColl:
    coll_name = 'Note'

    def __init__(self):
        self._dbm = DBManager.create(self.coll_name)
        self._coll: Collection = self._dbm.coll
        self._query: Optional[BiliNoteForMongo] = None
        self._qs: List[BiliNoteForMongo] = []

    def save_one(self, schema: BiliNoteForMongo):
        self._coll.insert_one(schema.dict())

    def find_one(self, **kwargs) -> Optional[BiliNoteForMongo]:
        res = self._coll.find_one(filter=kwargs)
        if not res:
            return None

        try:
            self._query = BiliNoteForMongo(**res)
        except Exception as e:
            raise e
        return self._query.copy()
