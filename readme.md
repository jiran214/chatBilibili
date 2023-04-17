# 项目名称

ChatBilibili

## 简介

基于embedding和ChatGPT3.5，实时生成B站视频概要，同时支持和视频内容聊天

## 环境

- python 3. 8
- mongo[暂时]

## 安装配置

```
git clone https://github.com/jiran214/chatBilibili.git
cd backend
pip install -r .\requirements.txt
python ./main
```

在backend目录下创建配置文件config.int模板(该项目所有配置信息都在这)

```ini
[mongo]
host = localhost
username =
password =
port = 27017
db_name = chat2Bili

[openai]
api_key = xxx

[service]
host = 127.0.0.1
port = 8080

[other]
debug = True  
proxy = 127.0.0.1:7890
bili_cookie = SESSDATA=xxxxxxxxxxxxxx
some_config = ...
```



## 功能介绍

![image-20230409211417238](https://raw.githubusercontent.com/jiran214/chatBilibili/master/public/image-20230409211417238.png)

使用fastapi的docs体验功能

![image-20230409211640365](https://raw.githubusercontent.com/jiran214/chatBilibili/master/public/image-20230409211640365.png)

note_query：BV号或者视频aid

question：聊天的问题

注：需要先调summary接口，在本地生成向量数据，才能开启聊天

### summary

示例：[【4K顶级画质60FPS】蔡徐坤《只因你太美》原版完整版现场！一晃眼6年过去了_哔哩哔哩_bilibili](https://www.bilibili.com/video/BV1ct4y1n7t9/?spm_id_from=333.337.search-card.all.click&vd_source=df965f3f6f275f55ae2075576c0f4750)

![image-20230409212218735](https://raw.githubusercontent.com/jiran214/chatBilibili/master/public/image-20230409212218735.png)

```markdown
## 摘要

蔡徐坤演唱《只因你太美》原版完整版现场，以顶尖的幕后制作保证高质量音乐和画面。

## 要点\n\n- 🎤 蔡徐坤以个人实力及原创作品展现音乐才华。
- 🎶 充满感性色彩的歌词，表达爱情的美好。
- 💃 独具匠心的编舞，为歌曲创造更动人的表演，体现音乐舞蹈的完美结合。
- 🏀 蔡徐坤不仅是唱跳偶像，还是篮球运动员。
- 📝 蔡徐坤不仅有才华，还拥有作词能力，为自己的音乐创作贡献更多。
- 🤝 这是全民制作的作品，多方参与，体现团队力量。
- 🎉 期待蔡徐坤的粉丝可以在接下来的节目中为他投票，为他加油打气。
```

### chat

问问坤坤喜欢什么？

![image-20230409213138401](https://raw.githubusercontent.com/jiran214/chatBilibili/master/public/image-20230409213138401.png)

```markdown
根据您提供的段落，我可以回答您的问题。据我了解，您是蔡徐坤粉丝或者喜欢他的音乐和表演，因为这些段落包含了一些与他相关的话题。蔡徐坤擅长的方面包括唱跳 rap、篮球、以及作曲编舞的原创作品。在他的歌曲中，\"只因你太美\" 和 \"who you\" 这两首歌深受粉丝们的喜爱，并且他还制作了很多自己的作词。如果您是蔡徐坤的粉丝，那么您应该期待他在未来的节目中的表现，并多多为他投票，以支持他的音乐事业。综上所述，蔡徐坤擅长的方面主要集中在音乐表演和篮球方面。
```

### comment

自动视频的生成评论

![image-20230409213138401](https://raw.githubusercontent.com/jiran214/chatBilibili/master/public/Snipaste_2023-04-17_16-41-23.png)


### 一些说明：

- 生成摘要时，根据标题匹配top n个向量对应的chunk，作为摘要上下文

- 支持没有cc字幕的视频（必剪接口解决），也就是任何B站视频都能chat

- 搜索邻近向量封装了方法，官方推荐用余弦相似度

- 尝试过一些向量数据库，本地知识库的应用场景需要用到，本项目数据量较小没必要用

- 长文本请求text-embedding-ada-002模型时，根据文本长度和最大token，要分批次请求

- openAi库不支持修改aiohttp和requests模块的ssl，导致开启代理会报错，通过源码阅读利用猴子补丁实现openai库的代理请求

  ```python
  # openAi.py
  
  proxies = {}
  import requests
  from openai import api_requestor
  
  def make_session() -> requests.Session:
      s = requests.Session()
      s.verify = False
      s.proxies = proxies
      urllib3.disable_warnings()
      s.trust_env = False
      s.mount(
          "https://",
          requests.adapters.HTTPAdapter(max_retries=2),
      )
      return s
  
  session = make_session()
  @asynccontextmanager
  async def aiohttp_session() -> AsyncIterator[aiohttp.ClientSession]:
      async with aiohttp.ClientSession(connector=TCPConnector(ssl=False)) as session:
          yield session
  
  # 猴子补丁
  if config.proxy:
      # api_requestor._make_session = make_session
      setattr(api_requestor._thread_context, 'session', session)
      api_requestor.aiohttp_session = aiohttp_session
  ```

## 项目结构

待更新...

## 未来计划

- [x] note_query支持各种形式的视频查询
- [ ] 前端 ...
- [ ] Event Stream
- [ ] redis缓存chat上下文
- [ ] prompt优化，支持更多选项
- [ ] 优化接口响应速度
- [x] Nginx部署

...

## 参考资料

- prompt暂时参考了： [JimmyLv/BibiGPT: BibiGPT · One-click summary for video & audio content: Bilibili | YouTube | Websites丨Podcasts | Meetings | Local files, etc. 音视频内容一键总结：哔哩哔哩丨YouTube丨网页丨播客丨会议丨本地文件等 (原 BiliGPT 省流神器 & 课代表) (github.com)](https://github.com/JimmyLv/BibiGPT)
- 必剪语音转文字：[SocialSisterYi/bcut-asr: 使用必剪API的语音字幕识别 (github.com)](https://github.com/SocialSisterYi/bcut-asr)

## Problem

1. 最大的IO瓶颈在GPT3.5接口请求上，要40秒左右（改成stream输出会好些），可能是我vpn的问题
2. 视频的字幕很碎，破坏了句子原本意思，很影响向量搜索的准确性

## 更新日志

- 4.15 新增自动生成视频评论：comment接口
- 4.17 nginx部署&note_query支持链接查询

## Contact Me

欢迎加我WX：yuchen59384 交流！