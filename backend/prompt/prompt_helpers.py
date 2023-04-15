"""
 @Author: jiran
 @Email: jiran214@qq.com
 @FileName: prompt.py
 @DateTime: 2023/4/7 15:22
 @SoftWare: PyCharm
"""
import tiktoken

from prompt import temple


class TokenMixin:

    model = None
    max_tk = None

    def __init__(self):
        self._encoder = tiktoken.encoding_for_model(self.model)
        self._encoder_tk = 0
        self._tk_list = []

    def calc_encoder_tk(self, content: str):
        """计算tk，当刚好大于max_tk的时候，准备请求"""
        num_tk = len(self._encoder.encode(content))
        self._encoder_tk += num_tk
        return num_tk

    @property
    def encoder_tk(self):
        return self._encoder_tk

    @property
    def tk(self):
        if not self._tk_list:
            raise '还未请求'
        return self._tk_list[-1]

    @tk.setter
    def tk(self, tk):
        self._tk_list.append(tk)

    @property
    def total_tk(self):
        """累计token消耗"""
        return sum(self._tk_list)


class GPT3dot5PromptHelper(TokenMixin):

    model = 'gpt-3.5-turbo'
    max_tk = 4096 - 1024

    def __init__(self):
        super().__init__()
        self._messages = []

    def initialize_message_system_content(self, system_content: str):
        self.add_message(
            {'role': 'system',
             'content': system_content},
        )

    def add_message_user_content(self, user_content: str):
        if self.calc_encoder_tk(user_content) > self.max_tk:
            raise '超过tk限制'
        self.add_message(
            {'role': 'user',
             'content': user_content},
        )

    def add_message(self, msg):
        self._messages.append(msg)

    @property
    def messages(self):
        return self._messages

    @property
    def user_content(self):
        """最新用户提问"""
        new_msg_dict = self._messages[-1]
        if new_msg_dict['role'] != 'user':
            raise '还未提问'
        return new_msg_dict['content']

    @property
    def assistant_content(self):
        new_msg_dict = self._messages[-1]
        if new_msg_dict['role'] != 'assistant':
            raise '还未请求'
        return new_msg_dict['content']
