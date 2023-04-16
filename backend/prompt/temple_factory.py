"""
 @Author: jiran
 @Email: jiran214@qq.com
 @FileName: temple.py
 @DateTime: 2023/4/8 14:19
 @SoftWare: PyCharm
"""

# 参考：https://github.com/SkywalkerDarren/chatWeb.git
from typing import List

from prompt.base import PromptFactory
from prompt.schema import SummaryConfig
from schema import Document
from prompt.temples import *


class SummaryPromptFactory(PromptFactory):

    temple = BibiGPT_summary_temple

    def get_system_content_2(self, documents):
        text = "\n".join(f"{index}. {document.content}" for index, document in enumerate(documents))
        return chatWeb_summary_temple['system'].format(transcript=text)

    def get_system_content(self, sentence_count=10, language='Chinese'):
        prompt = self.temple['system'].format(
            language=language,
            sentence_count=sentence_count
        )
        return prompt

    def get_user_content(
            self, title, documents: List[Document], config: SummaryConfig, desc='',
    ):
        if config.emoji_show:
            emoji_template_text = '[Emoji] '
            outline_template_text = 'Choose an appropriate emoji for each bullet point. '
        else:
            emoji_template_text, outline_template_text = '', ''

        transcript = '\n'.join([d.content for d in documents])

        user_prompt = self.temple['user_prompt'].format(
            emoji_template_text=emoji_template_text,
            outline_template_text=outline_template_text,
            sentence_count=config.sentence_count,
            words_count=config.words_count,
            title=title,
            desc=desc,
            transcript=transcript,
            language=config.language,
        )

        prompt = self.temple['user'].format(
            video_title=title,
            video_transcript=transcript,
            prompt=user_prompt,
        )
        return prompt


class ChatPromptFactory(PromptFactory):

    temple = embedding_chat_temple

    def get_system_content(self):
        return self.temple['system']

    def get_user_content(self, question, documents: List[Document]):
        text_list = [f"{n + 1}.{d.content}" for n, d in enumerate(documents)]
        text = '\n'.join(text_list)
        temple = self.temple['user'].format(question=question)
        return temple + text


class CommentPromptFactory(PromptFactory):

    temple = embedding_chat_temple

    def get_system_content(self):
        return self.temple['system']

    def get_user_content(self, summary, comments, extra_prompt=None, reply_num=5):
        temple = self.temple['user'].format(
            summary=summary,
            comments=comments,
            reply_num=reply_num,
            # extra_prompt
        )
        return temple


if __name__ == '__main__':
    # print(get_bili_summary_user_content(title='123', transcript='123'))
    # print(get_bili_summary_system())
    ...