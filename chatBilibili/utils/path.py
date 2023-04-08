"""
 @Author: jiran
 @Email: jiran214@qq.com
 @FileName: path.py
 @DateTime: 2023/3/31 1:07
 @SoftWare: PyCharm
"""
import os
from functools import lru_cache


@lru_cache
def root_path():
    current_file_path = os.path.abspath(__file__)
    project_root_path = os.path.dirname(os.path.dirname(current_file_path))
    return project_root_path


def get_absolute_dir_path(relative_path):
    """
    获取相对文件夹路径
    :param relative_path:
    :return:
    """
    path = os.path.join(root_path(), relative_path)
    if not os.path.exists(path):
        raise FileExistsError('文件夹不存在')
    return path


def get_absolute_file_path(*relative_path):
    """
    获取某个文件绝对路径
    :param relative_path:
    :return:
    """
    return os.path.join(root_path(), *relative_path)


if __name__ == '__main__':
    print(get_absolute_file_path('static', 'note', '519195234.mp3'))
