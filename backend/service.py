"""
 @Author: jiran
 @Email: jiran214@qq.com
 @FileName: service.py
 @DateTime: 2023/4/7 16:30
 @SoftWare: PyCharm
"""
import asyncio
import json
from contextlib import asynccontextmanager
from typing import List, Union

import aiohttp
import numpy as np

from log import service_logger
from parse.audio2text import get_audio_text
from parse.content import async_parse_content_to_file
from parse.json import get_note_detail_subtitle, get_note_cc_content, get_first_page_comment
from parse.text import get_real_time_content
from prompt.prompt_helpers import GPT3dot5PromptHelper
from prompt.schema import SummaryConfig
from prompt.temple_factory import SummaryPromptFactory, ChatPromptFactory, CommentPromptFactory
from requestor.bilibili import request_note_detail, request_note_audio, request_note_cc, request_note_comment, request_note_danmu
from requestor.opanAi import chat_with_3dot5, async_get_embedding, async_get_embedding_with_documents, get_embedding
from requestor.schemas import BiliNote, BiliAudioDownloadHrefParams, BiliNoteView, BiliCommentParams
from schema import Document, Vector
from utils.embedding import num_tokens_and_cost_from_string, distances_from_embeddings
from utils.session import _make_session


logger = service_logger


class EmbeddingService:
    model = 'text-embedding-ada-002'

    def __init__(self):
        ...

    def get_embedding(self, document_without_embedding: Document) -> (Document, int):
        """获取文本向量"""
        embedding, tk = get_embedding([document_without_embedding.content])
        document_without_embedding.embedding = embedding
        return document_without_embedding, tk

    async def get_embedding_list(self, documents_without_embedding: List[Document]):
        """加载长文本向量"""

        tasks = []
        waiting_documents = []
        embedding_total_tk = 0
        total_cost = 0
        current_tk = 0
        limit_tk = 8192 - 1024

        # 限制每次请求的tk长度
        for document in documents_without_embedding:
            tk, cost = num_tokens_and_cost_from_string(document.content, model=self.model)
            current_tk += tk

            embedding_total_tk += tk
            total_cost += cost
            if current_tk >= limit_tk:
                tasks.append(async_get_embedding_with_documents(waiting_documents))
                waiting_documents = []
                current_tk = 0
            else:
                waiting_documents.append(document)

        if waiting_documents:
            tasks.append(async_get_embedding_with_documents(waiting_documents))

        # 并发请求
        res = await asyncio.gather(
            *tasks
        )
        new_documents = []
        for tmp_documents in res:
            new_documents.extend(tmp_documents)
        # service_logger.info(f"共花费token{embedding_total_tk},{total_cost}美元")

        return new_documents, embedding_total_tk

    def get_reference_vector(self, documents: List[Document], option='title') -> Vector:
        if option == 'title':
            for d in documents:
                if d.filed == option:
                    return d.embedding
        elif option == 'avg':
            """计算向量列表中的平均向量"""
            # 创建嵌入矩阵
            embedding_matrix = np.array([d.embedding for d in documents])
            # 计算所有向量的和，并除以向量数量，得到平均向量
            mean_embedding = np.mean(embedding_matrix, axis=0)
            return mean_embedding.data
        else:
            raise f'option:{option}不存在'

    def search_top_n_with_vector_from_documents(
            self, search_vector: Vector, documents: List[Document], top, distance_metric='cosine'
    ):
        """
        默认余弦相似度方式，从向量列表中搜索相似度top n的列表
        :param search_vector:
        :param documents:
        :param top:
        :param distance_metric: cosine L1 L2 Linf
        :return:
        """
        embeddings = [d.embedding for d in documents]
        distances = distances_from_embeddings(embeddings=embeddings, query_embedding=search_vector, distance_metric=distance_metric)
        top_n_indices = np.argsort(distances)[:top]
        return [documents[index] for index in top_n_indices]

    def search_top_n_with_vector_from_documents_euclidean(
            self, embedding: Vector, documents: List[Document], top
    ) -> List[Document]:
        """欧几里得方式，从向量列表中搜索相似度top n的列表"""
        # 生成向量矩阵
        embedding_matrix = np.array([d.embedding for d in documents])
        # 计算每个向量与平均向量的距离，并排序，得到最接近的前n个向量
        distances = np.linalg.norm(embedding_matrix - embedding, axis=1)
        top_n_indices = np.argsort(distances)[:top]
        return [documents[index] for index in top_n_indices]


class GPTService:
    def __init__(self):
        self.prompt_helper = GPT3dot5PromptHelper()

    def get_summary_2(self, documents: List[Document]):
        prompt_factory = SummaryPromptFactory()
        self.prompt_helper.initialize_message_system_content(prompt_factory.get_system_content_2(documents))
        chat_with_3dot5(self.prompt_helper)
        return self.prompt_helper

    def get_summary_1(self, note_schema: BiliNoteView, documents: List[Document], config: SummaryConfig):
        prompt_factory = SummaryPromptFactory()
        self.prompt_helper.initialize_message_system_content(prompt_factory.get_system_content())
        self.prompt_helper.add_message_user_content(
            prompt_factory.get_user_content(
                title=note_schema.title,
                documents=documents,
                config=config,
            )
        )
        chat_with_3dot5(self.prompt_helper)
        return self.prompt_helper

    def chat(self, question, documents: List[Document]):
        prompt_factory = ChatPromptFactory()
        self.prompt_helper.initialize_message_system_content(prompt_factory.get_system_content())
        self.prompt_helper.add_message_user_content(prompt_factory.get_user_content(question, documents))
        chat_with_3dot5(self.prompt_helper)
        return self.prompt_helper

    def get_comment(self, summary, comments):
        prompt_factory = CommentPromptFactory()
        self.prompt_helper.initialize_message_system_content(prompt_factory.get_system_content())
        self.prompt_helper.add_message_user_content(
            prompt_factory.get_user_content(
                summary, comments
        ))
        chat_with_3dot5(self.prompt_helper)
        # self.prompt_helper.assistant_content = json.loads(self.prompt_helper.assistant_content)
        return self.prompt_helper

    def get_danmu(self, danmus):
        ...


class CrawlService:
    def __init__(self, aid, bv=None, cid=None):
        self.aid = aid
        self.cid = cid

    async def get_note_caption(self, t) -> (Union[List[Document], None], BiliNote):
        """获取cc字幕，没有返回None"""
        # 借鉴openAi库的写法
        ctx = _make_session()
        session = await ctx.__aenter__()
        json_data = await request_note_detail(session, self.aid)
        subtitle_url, note_schema = get_note_detail_subtitle(json_data)
        logger.debug(f'aid:{self.aid}-获取subtitle_url完成-耗时{t()}')

        if subtitle_url:
            json_data = await request_note_cc(session, subtitle_url)
            content_list = get_note_cc_content(json_data)
            logger.debug(f'aid:{self.aid}-获取cc字幕完成-耗时{t()}')
        else:
            audio_filepath = await request_note_audio(
                session,
                BiliAudioDownloadHrefParams(
                    avid=note_schema.View.aid, cid=note_schema.View.cid
                ))
            logger.debug(f'aid:{self.aid}-下载mp3完成-耗时{t()}')
            content_list = get_audio_text(audio_filepath)
            logger.debug(f'aid:{self.aid}-获取bCut字幕完成-耗时{t()}')

        documents = [Document(hash_id=hash(content), content=content) for content in content_list]

        # documents加入除字幕以外的东西 todo View能加上都加上
        documents.extend([
            Document(hash_id=hash(note_schema.View.title), content=note_schema.View.title, filed='title')
        ])

        return documents, note_schema

    async def get_note_comment(self, limit) -> List[str]:
        ctx = _make_session()
        session = await ctx.__aenter__()
        json_data = await request_note_comment(session, BiliCommentParams(oid=self.aid))
        comment_list = get_first_page_comment(json_data)
        return comment_list[:limit]

    async def get_note_danmu(self):
        ctx = _make_session()
        session = await ctx.__aenter__()
        text_data = await request_note_danmu(session, self.cid)
        real_time_content_list = get_real_time_content(text_data)
        return real_time_content_list

# class VectorStorageService:
#     def __init__(self, storage):
#         self.storage = None
#
#     def save_documents_to_storage(self, save_key, documents: List[Document]):
#         """持久化长文本和向量"""
#         ...
#
#     def load_documents_from_storage(self, save_key) -> List[Document]:
#         """加载键对应的所有文本和向量到内存"""
#         ...
#
#     def exists_key_in_storage(self, save_key) -> bool:
#         return False
#
#     def search_top_n_from_storage(self, document: Document, save_key, top) -> List[Document]:
#         """利用数据库封装的向量搜索"""
#         ...
