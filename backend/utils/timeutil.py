"""
 @Author: jiran
 @Email: jiran214@qq.com
 @FileName: timeutil.py
 @DateTime: 2023/4/9 18:25
 @SoftWare: PyCharm
"""
import time


class TimeRecord:
    def __init__(self, key):
        self._t = time.time()

    def mark(self):
        tmp = self._t
        now = time.time()
        self._t = now
        return now - tmp
