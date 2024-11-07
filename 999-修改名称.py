import pypinyin

def translate_to_pinyin(text):
    pinyin_text = ''
    for char in text:
        if '\u4e00' <= char <= '\u9fff':  # 判断是否为中文字符
            pinyin = pypinyin.lazy_pinyin(char)
            pinyin_text += pinyin[0]  # 添加拼音到结果字符串
        else:
            pinyin_text += char  # 非中文字符不变
    return pinyin_text


