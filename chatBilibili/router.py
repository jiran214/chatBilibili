"""
 @Author: jiran
 @Email: jiran214@qq.com
 @FileName: router.py
 @DateTime: 2023/4/7 16:30
 @SoftWare: PyCharm
"""

import openai.embeddings_utils
import time

from fastapi import APIRouter, HTTPException
# from starlette.responses import StreamingResponse
# from fastapi.responses import StreamingResponse

from database.mongo_orm import NoteColl
from database.schema import BiliNoteForMongo
from prompt.schema import SummaryConfig
from schema import Document
from service import NoteCaptionCrawlService, EmbeddingService, GPTService
from utils.video_id_transform import note_query_2_aid

embedding_router = APIRouter(
    prefix=''
)


@embedding_router.get("/summary", summary='获取视频向量，生成概要', description='', tags=['summary'])
async def caption(
        note_query: str
):
    # 初始化
    embedding_total_tk = 0

    # aid转换
    aid = note_query_2_aid(note_query)
    if not aid:
        raise HTTPException(status_code=500, detail="未找到相关资源")

    # 是否已经有向量数据
    coll = NoteColl()
    mongo_note_schema = coll.find_one(aid=int(aid))
    embedding_service = EmbeddingService()
    if not mongo_note_schema:
        # 采集视频资源
        crawl_service = NoteCaptionCrawlService(aid=aid)
        documents, note_schema = await crawl_service.get_note_caption()
        # 获取向量
        documents, embedding_total_tk = await embedding_service.get_embedding_list(documents)
        # 存储向量
        coll.save_one(
            BiliNoteForMongo(
                **note_schema.View.dict(),
                documents=documents,
                create_time=time.time()
            )
        )
        note_view_schema = note_schema.View
    else:
        # 查询向量
        note_view_schema = mongo_note_schema
        documents = mongo_note_schema.documents

    # 获取最接近中心向量的top n documents
    mean_embedding = embedding_service.calc_avg_embedding(documents)
    top_n_documents = embedding_service.search_top_n_with_vector_from_documents(mean_embedding, documents, top=20)
    # 生成概要
    gpt_service = GPTService()
    summary, summary_tk = gpt_service.get_summary_1(
        note_view_schema,
        documents=top_n_documents,
        config=SummaryConfig(
            emoji_show=True,
            sentence_count=7,
            words_count=15,
            language='Chinese'
        ))
    # summary = gpt_service.get_summary_2(documents=top_n_documents)

    return {
        '主要内容': [d.content for d in top_n_documents],
        '摘要': summary,
        '嵌入使用token': embedding_total_tk,
        '概要使用token': summary_tk
    }


@embedding_router.get("/chat", summary='和视频内容聊天', description='', tags=['chat'])
async def caption(
        note_query: str,
        question: str
):
    # aid转换
    aid = note_query_2_aid(note_query)
    if not aid:
        raise HTTPException(status_code=500, detail="未找到相关资源")

    # mongo是否有向量数据
    coll = NoteColl()
    mongo_note_schema = coll.find_one(aid=int(aid))
    if not mongo_note_schema:
        raise HTTPException(status_code=500, detail="请先获取summary")
    documents = [d for d in mongo_note_schema.documents]
    embedding_service = EmbeddingService()

    # 搜索top 相关向量
    question_document = embedding_service.get_embedding(Document(hash_id=hash(question), content=question))
    top_n_documents = embedding_service.search_top_n_with_vector_from_documents(question_document.embedding, documents, top=10)
    gpt_service = GPTService()
    answer, chat_tk = gpt_service.chat(question_document.content, documents=top_n_documents)

    return {
        '相关文本': [d.content for d in top_n_documents],
        '回答': answer,
        'chat使用token': chat_tk
    }


# todo 响应事件流
# condition = threading.Condition()
#
#
# class State:
#     def __init__(self):
#         self.messages = []
#         while 1:
#             self.update(['1', '2', '3', '4'])
#             print('1')
#             time.sleep(3)
#
#     def update(self, new_messages):
#         self.messages = new_messages
#         with condition:
#             print('3')
#             condition.notify()
#
#
# @embedding_router.get('/stream')
# def stream():
#     state = State()
#
#     def event_stream():
#         while True:
#             with condition:
#                 condition.wait()
#             print('2')
#             for message in state.messages:
#                 yield 'data: {}\n\n'.format(message)
#
#     return StreamingResponse(event_stream(), media_type="text/event-stream")