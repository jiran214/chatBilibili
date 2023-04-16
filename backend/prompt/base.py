"""
 @Author: jiran
 @Email: jiran214@qq.com
 @FileName: base.py
 @DateTime: 2023/4/16 13:42
 @SoftWare: PyCharm
"""


class PromptFactory:

    temple = None

    def get_system_content(self, *args, **kwargs):
        ...

    def get_user_content(self, *args, **kwargs):
        ...
