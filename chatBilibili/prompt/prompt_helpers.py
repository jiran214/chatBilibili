"""
 @Author: jiran
 @Email: jiran214@qq.com
 @FileName: prompt.py
 @DateTime: 2023/4/7 15:22
 @SoftWare: PyCharm
"""
import tiktoken

from prompt import temple


class PromptHelper:

    model = None

    def __init__(self):
        self.encoder = tiktoken.encoding_for_model(self.model)

    @property
    def total_token(self):
        """累计token消耗"""
        return 10


class GPT3dot5PromptHelper(PromptHelper):

    model = 'gpt-3.5-turbo'

    def __init__(self):
        super().__init__()
        self.messages = []

    def initialize_message_system_content(self, system_content: str):
        self.messages.append(
            {'role': 'system',
             'content': system_content},
        )

    def add_message_user_content(self, user_content: str):
        self.messages.append(
            {'role': 'user',
             'content': user_content},
        )

    @property
    def user_content(self):
        """最新用户提问"""
        return ''

    @property
    def answer(self):
        return ''
