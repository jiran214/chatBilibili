"""
 @Author: jiran
 @Email: jiran214@qq.com
 @FileName: temple.py
 @DateTime: 2023/4/8 14:19
 @SoftWare: PyCharm
"""

# 参考：https://github.com/SkywalkerDarren/chatWeb.git
from typing import List

from prompt.schema import SummaryConfig
from schema import Document

chatWeb_summary_temple = {
    'system': (
        '你是一个有帮助的文章总结助手，'
        '以下是从文中搜索到具有相关性的文章内容片段，相关性从高到底排序，'
        '你需要从这些相关内容中总结全文内容，'
        '最后的结果需要用中文展示：\n{transcript}\n\n中文总结：'
    )
}


def get_bili_summary_system_2(documents):
    text = "\n".join(f"{index}. {document.content}" for index, document in enumerate(documents))
    return chatWeb_summary_temple['system'].format(transcript=text)


# 参考：https://github.com/JimmyLv/BibiGPT/
BibiGPT_summary_temple = {
    'system': (
        "I want you to act as an educational content creator. "
        "You will help students summarize the essence of the video in {language}. "
        "Please summarize the video subtitles (there may be typos in the subtitles, "
        "please correct them) and return them in an unordered list format."
        "Please do not exceed {sentence_count} items, "
        "and make sure not to repeat any sentences and all sentences are concise, clear, and complete. Good luck!"
    ),
    'user': (
        """Title: "{video_title}"\nTranscript: "{video_transcript}"\n\nInstructions: {prompt}"""
    ),
    'user_prompt': (
        """Your output should use the following template:\n
        ## Summary\n
        ## Highlights\n
        - {emoji_template_text}Bullet point{outline_template_text}\n\n
        Your task is to summarise the text I have given you in up to {sentence_count} concise bullet points, 
        starting with a short highlight, each bullet point is at least {words_count} words. 
        {emoji_template_text}{outline_template_text}Use the text above(Content relevance order from highest to lowest): {title}\n{desc}\n{transcript}.\n\n
        Reply in {language} Language."""
    )
}


def get_bili_summary_system(sentence_count=10, language='Chinese'):
    prompt = BibiGPT_summary_temple['system'].format(
        language=language,
        sentence_count=sentence_count
    )
    return prompt


def get_bili_summary_user_content(
        title, documents: List[Document], config: SummaryConfig, desc='',
):
    if config.emoji_show:
        emoji_template_text = '[Emoji] '
        outline_template_text = 'Choose an appropriate emoji for each bullet point. '
    else:
        emoji_template_text, outline_template_text = '', ''

    transcript = '\n'.join([d.content for d in documents])

    user_prompt = BibiGPT_summary_temple['user_prompt'].format(
        emoji_template_text=emoji_template_text,
        outline_template_text=outline_template_text,
        sentence_count=config.sentence_count,
        words_count=config.words_count,
        title=title,
        desc=desc,
        transcript=transcript,
        language=config.language,
    )

    prompt = BibiGPT_summary_temple['user'].format(
        video_title=title,
        video_transcript=transcript,
        prompt=user_prompt,
    )
    return prompt


embedding_chat_temple = {
    'system': (
        "我是一个非常有帮助的QA机器人，"
        "能准确地使用现有文档回答用户的问题。我"
        "可以使用所提供的文本来形成我的答案，"
        "在可能的情况下，尽量使用自己的话而不是逐字逐句地抄袭原文。"
        "我的回答是准确、有帮助、简明、清晰的。"
    ),
    'user': (
        "我的问题是：{question}，请使用以下段落来提供问题的答案：\n"
        # "1.[向量查询结果top1]\n2.[向量查询结果top2]\n..."
    )
}


def get_bili_chat_system_content():
    return embedding_chat_temple['system']


def get_bili_chat_user_content(question, documents: List[Document]):
    text_list = [f"{n+1}.{d.content}" for n, d in enumerate(documents)]
    text = '\n'.join(text_list)
    temple = embedding_chat_temple['user'].format(question=question)
    return temple + text


if __name__ == '__main__':
    # print(get_bili_summary_user_content(title='123', transcript='123'))
    print(get_bili_summary_system())
