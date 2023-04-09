"""
 @Author: jiran
 @Email: jiran214@qq.com
 @FileName: audio2text.py
 @DateTime: 2023/4/7 22:07
 @SoftWare: PyCharm
"""
from log import crawler_logger
from parse.bcut_asr import BcutASR, ResultStateEnum

logger = crawler_logger


def get_audio_text(file_path):
    asr = BcutASR(file_path)
    asr.upload()  # 上传文件
    asr.create_task()  # 创建任务

    # 轮询检查结果
    while True:
        result = asr.result()
        # 判断识别成功
        if result.state == ResultStateEnum.COMPLETE:
            break

    # 解析字幕内容
    subtitle = result.parse()
    # 判断是否存在字幕
    if subtitle.has_data():
        # 输出srt格式
        logger.info(f"获取必剪字幕成功-file_path:{file_path}")
        return [s.transcript for s in subtitle.utterances]
        # r = [s.transcript for s in subtitle.utterances]
        # return r
    return None