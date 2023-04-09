"""
 @Author: jiran
 @Email: jiran214@qq.com
 @FileName: text.py
 @DateTime: 2023/4/9 18:09
 @SoftWare: PyCharm
"""
from typing import List

import random

import tiktoken


def random_filter_text_list(text_list: List[str], max_tk, model):
    """
    超过限制长度后，均匀随机去除多余文本
    :return:
    """
    encoder = tiktoken.encoding_for_model(model)

    tk_list = [len(encoder.encode(content)) for content in text_list]
    if sum(tk_list) < max_tk:
        return text_list

    text_list_index_list = list(range(len(text_list)))
    random.shuffle(text_list_index_list)
    new_text_list_index_list = []
    current_tk = 0

    for index in text_list_index_list:
        if current_tk + tk_list[index] > max_tk:
            break
        else:
            current_tk += tk_list[index]
            new_text_list_index_list.append(index)

    new_text_list_index_list.sort()

    return [text_list[index] for index in new_text_list_index_list]

