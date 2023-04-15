"""
 @Author: jiran
 @Email: jiran214@qq.com
 @FileName: schema.py
 @DateTime: 2023/4/7 14:46
 @SoftWare: PyCharm
"""
from typing import List, Dict, Union

from pydantic import BaseModel


class GPT35Params(BaseModel):
    model: str = "gpt-3.5-turbo"
    # model: str = Field(..., description="This field is required")  # 模型 ID，只支持 gpt-3.5-turbo 和 gpt-3.5-turbo-0301
    messages: List  # 聊天格式的输入消息列表
    temperature: float = 1.0  # 采样温度，0~2 范围内的浮点数。较大的值会使输出更随机，较小的值会使输出更确定
    top_p: float = 1.0  # 替代采样温度的另一种方式，称为 nucleus 采样，只考虑概率质量排名前 top_p 的 token。范围在 0~1 之间
    n: int = 1  # 每个输入消息要生成的聊天完成选项数量，默认为 1
    stream: bool = False  # 是否启用流式输出
    stop: Union[str, List[str], None] = None  # 最多 4 个序列，当 API 生成的 token 包含任意一个序列时停止生成
    max_tokens: int = None  # 默认inf   # 生成的答案中允许的最大 token 数量，默认为 (4096 - prompt tokens)
    presence_penalty: float = None  # 0.0   # -2.0 到 2.0 之间的数字，用于基于新 token 是否出现在已有文本中惩罚模型。正数值会增加模型谈论新话题的可能性
    frequency_penalty: float = None  # 0.0   # -2.0 到 2.0 之间的数字，用于基于新 token 是否在已有文本中的频率惩罚模型。正数值会降低模型直接重复相同文本的可能性
    logit_bias: Dict[str, float] = None  # 一个将 token ID 映射到关联偏差值（-100 到 100）的 JSON 对象，用于修改指定 token 出现在完成中的可能性
    user: str = None  # 表示最终用户的唯一标识符，可帮助 OpenAI 监视和检测滥用


class BiliAudioDownloadHrefParams(BaseModel):
    # 稿件 avid
    avid: int = None
    # 稿件 bvid
    bvid: str = None
    cid: int = None
    # 视频清晰度选择 未登录默认 32（480P），登录后默认 64（720P） DASH 格式时无效
    qn: int = 0
    # 视频流格式标识：
    # 1	    MP4 格式	    仅 H.264 编码 与 FLV、DASH 格式互斥
    # 16    DASH 格式	与 MP4、FLV 格式互斥
    fnval: int = 16
    # fnver: int = 0
    # 是否允许 4K 视频
    # fourk: int = 1


class BiliNoteTag(BaseModel):
    # tag_id
    tag_id: int
    # TAG名称
    tag_name: str


class BiliNoteStat(BaseModel):
    # 稿件avid
    aid: int
    # 播放数
    view: int
    # 弹幕数
    danmaku: int
    # 评论数
    reply: int
    # 收藏数
    favorite: int
    # 投币数
    coin: int
    # 分享数
    share: int
    # 当前排名
    now_rank: int
    # 历史最高排行
    his_rank: int
    # 获赞数
    like: int


class BiliNoteView(BaseModel):
    # 稿件bvid
    bvid: str
    # 稿件avid
    aid: int
    # 稿件分P总数 默认为1
    videos: int
    # 分区tid
    tid: int  # 子分区名称
    tname: str  # 视频类型 1：原创 2：转载
    copyright: int
    # 稿件封面图片url
    pic: str
    # 稿件标题
    title: str  # 稿件发布时间 秒级时间戳
    pubdate: int
    # 用户投稿时间 秒级时间戳
    ctime: int
    # 视频简介
    desc: str  # 稿件总时长(所有分P) 单位为秒
    duration: int
    # 视频同步发布的的动态的文字内容
    dynamic: str
    # 视频1P cid
    cid: int
    # 视频状态数
    stat: BiliNoteStat
    # 视频UP主信息 # 包含mid、face、up name
    owner: dict
    # 视频CC字幕信息
    subtitle: dict = {}


class BiliNote(BaseModel):
    # 视频基本信息
    View: BiliNoteView
    # 视频TAG信息
    Tags: List[BiliNoteTag]
    # 推荐视频信息
    # Related: List[BiliNoteView]


class BiliCommentParams(BaseModel):
    # 评论区类型代码
    type: int = 1
    # 目标评论区id
    oid: int
    # 排序方式 默认为3 0 3：仅按热度 1：按热度 + 按时间 2：仅按时间
    mode: int = 1
    # 评论页选择 按热度时：热度顺序页码（0 为第一页） 按时间时：时间倒序楼层号 默认为 0
    next: int = 0
    # 每页项数 默认为 20 定义域：1 - 30
    ps: int = 20