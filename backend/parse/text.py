"""
 @Author: jiran
 @Email: jiran214@qq.com
 @FileName: text.py
 @DateTime: 2023/4/16 12:59
 @SoftWare: PyCharm
"""
from parsel import Selector


def get_real_time_content(text_data):
    selector = Selector(text=text_data)
    # 解析
    # res['cid'] = selector.xpath("""//i/chatid/text()""").get()
    # res['maxlimit'] = selector.xpath("""//i/maxlimit/text()""").get()

    # <d p="585.60300,4,25,16777215,1586706085,0,b06bc17,31228643365617667,10">吴岳是真的惨，刚当上舰长，船就要拆了。。</d>
    real_time_content = []
    d_list = selector.xpath("""//i/d""")
    for d in d_list:
        occur_time = d.xpath("""./@p""").get().split(',')[0]
        content = d.xpath("""./text()""").get()
        # real_time_content.append({
        #         'occur_time': occur_time,
        #         'content': content
        # })
        real_time_content.append(content)
    return real_time_content