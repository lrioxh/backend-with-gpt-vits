import re
import jieba
from pypinyin.style._utils import get_finals, get_initials
from pypinyin import pinyin, load_phrases_dict, Style
from pypinyin_dict.phrase_pinyin_data import cc_cedict
from pypinyin_dict.pinyin_data import kmandarin_8105

kmandarin_8105.load()
cc_cedict.load()

def japanese_cleaners(text):
    from text.japanese import japanese_to_romaji_with_accent
    text = japanese_to_romaji_with_accent(text)
    text = re.sub(r'([A-Za-z])$', r'\1.', text)
    return text


def japanese_cleaners2(text):
    return japanese_cleaners(text).replace('ts', 'ʦ').replace('...', '…')


def korean_cleaners(text):
    '''Pipeline for Korean text'''
    from text.korean import latin_to_hangul, number_to_hangul, divide_hangul
    text = latin_to_hangul(text)
    text = number_to_hangul(text)
    text = divide_hangul(text)
    text = re.sub(r'([\u3131-\u3163])$', r'\1.', text)
    return text


def chinese_cleaners(text):
    '''Pipeline for Chinese text'''
    from text.mandarin import number_to_chinese, chinese_to_bopomofo, latin_to_bopomofo
    text = number_to_chinese(text)
    text = chinese_to_bopomofo(text)
    text = latin_to_bopomofo(text)
    text = re.sub(r'([ˉˊˇˋ˙])$', r'\1。', text)
    return text

PHRASE_LIST = [
    "米哈游",
    "琴", "安柏", "丽莎", "凯亚", "芭芭拉", "迪卢克", "雷泽", "温迪", "可莉", "班尼特", "诺艾尔", "菲谢尔",
    "砂糖", "莫娜", "迪奥娜", "阿贝多", "罗莎莉亚", "优菈", "魈", "北斗", "凝光", "香菱", "行秋", "重云",
    "七七", "刻晴", "达达利亚", "钟离", "辛焱", "甘雨", "胡桃", "烟绯", "申鹤", "云堇", "夜兰", "神里绫华",
    "神里", "绫华", "枫原万叶", "枫原", "万叶", "宵宫", "早柚", "雷电将军", "九条裟罗", "九条", "裟罗", "珊瑚宫心海",
    "珊瑚宫", "心海", "托马", "荒泷", "一斗", "荒泷派", "五郎", "八重神子", "神子", "神里绫人", "绫人",
    "久岐忍", "鹿野院平藏", "平藏", "蒙德", "璃月", "稻妻", "北风的王狼", "风魔龙", "特瓦林", "若陀龙王", "龙脊雪山",
    "金苹果群岛", "渊下宫", "层岩巨渊", "奥赛尔", "七天神像", "钩钩果", "落落莓", "塞西莉亚花", "风车菊", "尘歌壶",
    "提瓦特", "明冠山地", "风龙废墟", "明冠峡", "坠星山谷", "果酒湖", "望风山地", "坎瑞亚", "须弥", "枫丹", "纳塔",
    "至冬", "丘丘人", "丘丘暴徒", "深渊法师", "深渊咏者", "盗宝团", "愚人众", "深渊教团", "骗骗花", "急冻树", "龙蜥",
    "鸣神岛", "神无冢", "八酝岛", "海祇岛", "清籁岛", "鹤观", "绝云间", "群玉阁", "南十字", "死兆星", "木漏茶室",
    "神樱",
    "鸣神大社", "天使的馈赠", "社奉行", "勘定奉行", "天领奉行", "夜叉", "风神", "岩神", "雷神", "风之神", "岩之神",
    "雷之神",
    "风神瞳", "岩神瞳", "雷神瞳", "摩拉克斯", "契约之神", "雷电影", "雷电真", "八重宫司", "宫司大人", "巴巴托斯",
    "玉衡星",
    "天权星", "璃月七星", "留云借风", "削月筑阳", "理水叠山", "请仙典仪",
    "故事","环境","目标","社会","米哈游","原神","各地","发布","目标","系统","人工智能","数据","设计","快速","深度学习","乐观",
    "时候","女孩","日本","音乐","技能",
    "穿丝否莫","地府幽深","劳恩","捞个","三嗯","可三嗯"
]

for phrase in PHRASE_LIST:
    jieba.add_word(phrase)

load_phrases_dict({"若陀": [["rě"], ["tuó"]], "平藏": [["píng"], ["zàng"]],
                   "派蒙": [["pài"], ["méng"]], "安柏": [["ān"], ["bó"]],
                   "一斗": [["yī"], ["dǒu"]],"音乐":[["yīn"], ["yuè"]]
                   })
def genshin_cleaners(text):
    from text.mandarin import number_to_chinese,latin_to_bopomofo,bopomofo_to_pinyin,math_to_chinese
    text=number_to_chinese(text)    #读数字
    text=math_to_chinese(text)  #读数学符号
    text=latin_to_bopomofo(text)    #读字母
    text=bopomofo_to_pinyin(text)

    return " ".join([
        p
        for phone in pinyin(text, style=Style.TONE3, v_to_u=True)
        for p in [
            get_initials(phone[0], strict=True),
            get_finals(phone[0][:-1], strict=True) + phone[0][-1]
            if phone[0][-1].isdigit()
            else get_finals(phone[0], strict=True)
            if phone[0][-1].isalnum()
            else phone[0],
        ]
        if len(p) != 0 and not p.isdigit()
    ])


def zh_ja_mixture_cleaners(text):
    from text.mandarin import chinese_to_romaji
    from text.japanese import japanese_to_romaji_with_accent
    text = re.sub(r'\[ZH\](.*?)\[ZH\]',
                  lambda x: chinese_to_romaji(x.group(1))+' ', text)
    text = re.sub(r'\[JA\](.*?)\[JA\]', lambda x: japanese_to_romaji_with_accent(
        x.group(1)).replace('ts', 'ʦ').replace('u', 'ɯ').replace('...', '…')+' ', text)
    text = re.sub(r'\s+$', '', text)
    text = re.sub(r'([^\.,!\?\-…~])$', r'\1.', text)
    return text


def sanskrit_cleaners(text):
    text = text.replace('॥', '।').replace('ॐ', 'ओम्')
    text = re.sub(r'([^।])$', r'\1।', text)
    return text


def cjks_cleaners(text):
    from text.mandarin import chinese_to_lazy_ipa
    from text.japanese import japanese_to_ipa
    from text.korean import korean_to_lazy_ipa
    from text.sanskrit import devanagari_to_ipa
    from text.english import english_to_lazy_ipa
    text = re.sub(r'\[ZH\](.*?)\[ZH\]',
                  lambda x: chinese_to_lazy_ipa(x.group(1))+' ', text)
    text = re.sub(r'\[JA\](.*?)\[JA\]',
                  lambda x: japanese_to_ipa(x.group(1))+' ', text)
    text = re.sub(r'\[KO\](.*?)\[KO\]',
                  lambda x: korean_to_lazy_ipa(x.group(1))+' ', text)
    text = re.sub(r'\[SA\](.*?)\[SA\]',
                  lambda x: devanagari_to_ipa(x.group(1))+' ', text)
    text = re.sub(r'\[EN\](.*?)\[EN\]',
                  lambda x: english_to_lazy_ipa(x.group(1))+' ', text)
    text = re.sub(r'\s+$', '', text)
    text = re.sub(r'([^\.,!\?\-…~])$', r'\1.', text)
    return text


def cjke_cleaners(text):
    from text.mandarin import chinese_to_lazy_ipa
    from text.japanese import japanese_to_ipa
    from text.korean import korean_to_ipa
    from text.english import english_to_ipa2
    text = re.sub(r'\[ZH\](.*?)\[ZH\]', lambda x: chinese_to_lazy_ipa(x.group(1)).replace(
        'ʧ', 'tʃ').replace('ʦ', 'ts').replace('ɥan', 'ɥæn')+' ', text)
    text = re.sub(r'\[JA\](.*?)\[JA\]', lambda x: japanese_to_ipa(x.group(1)).replace('ʧ', 'tʃ').replace(
        'ʦ', 'ts').replace('ɥan', 'ɥæn').replace('ʥ', 'dz')+' ', text)
    text = re.sub(r'\[KO\](.*?)\[KO\]',
                  lambda x: korean_to_ipa(x.group(1))+' ', text)
    text = re.sub(r'\[EN\](.*?)\[EN\]', lambda x: english_to_ipa2(x.group(1)).replace('ɑ', 'a').replace(
        'ɔ', 'o').replace('ɛ', 'e').replace('ɪ', 'i').replace('ʊ', 'u')+' ', text)
    text = re.sub(r'\s+$', '', text)
    text = re.sub(r'([^\.,!\?\-…~])$', r'\1.', text)
    return text


def cjke_cleaners2(text):
    from text.mandarin import chinese_to_ipa
    from text.japanese import japanese_to_ipa2
    from text.korean import korean_to_ipa
    from text.english import english_to_ipa2
    text = re.sub(r'\[ZH\](.*?)\[ZH\]',
                  lambda x: chinese_to_ipa(x.group(1))+' ', text)
    text = re.sub(r'\[JA\](.*?)\[JA\]',
                  lambda x: japanese_to_ipa2(x.group(1))+' ', text)
    text = re.sub(r'\[KO\](.*?)\[KO\]',
                  lambda x: korean_to_ipa(x.group(1))+' ', text)
    text = re.sub(r'\[EN\](.*?)\[EN\]',
                  lambda x: english_to_ipa2(x.group(1))+' ', text)
    text = re.sub(r'\s+$', '', text)
    text = re.sub(r'([^\.,!\?\-…~])$', r'\1.', text)
    # print(text)
    return text


def thai_cleaners(text):
    from text.thai import num_to_thai, latin_to_thai
    text = num_to_thai(text)
    text = latin_to_thai(text)
    return text


def shanghainese_cleaners(text):
    from text.shanghainese import shanghainese_to_ipa
    text = shanghainese_to_ipa(text)
    text = re.sub(r'([^\.,!\?\-…~])$', r'\1.', text)
    return text


def chinese_dialect_cleaners(text):
    from text.mandarin import chinese_to_ipa2
    from text.japanese import japanese_to_ipa3
    from text.shanghainese import shanghainese_to_ipa
    from text.cantonese import cantonese_to_ipa
    from text.english import english_to_lazy_ipa2
    from text.ngu_dialect import ngu_dialect_to_ipa
    text = re.sub(r'\[ZH\](.*?)\[ZH\]',
                  lambda x: chinese_to_ipa2(x.group(1))+' ', text)
    text = re.sub(r'\[JA\](.*?)\[JA\]',
                  lambda x: japanese_to_ipa3(x.group(1)).replace('Q', 'ʔ')+' ', text)
    text = re.sub(r'\[SH\](.*?)\[SH\]', lambda x: shanghainese_to_ipa(x.group(1)).replace('1', '˥˧').replace('5',
                  '˧˧˦').replace('6', '˩˩˧').replace('7', '˥').replace('8', '˩˨').replace('ᴀ', 'ɐ').replace('ᴇ', 'e')+' ', text)
    text = re.sub(r'\[GD\](.*?)\[GD\]',
                  lambda x: cantonese_to_ipa(x.group(1))+' ', text)
    text = re.sub(r'\[EN\](.*?)\[EN\]',
                  lambda x: english_to_lazy_ipa2(x.group(1))+' ', text)
    text = re.sub(r'\[([A-Z]{2})\](.*?)\[\1\]', lambda x: ngu_dialect_to_ipa(x.group(2), x.group(
        1)).replace('ʣ', 'dz').replace('ʥ', 'dʑ').replace('ʦ', 'ts').replace('ʨ', 'tɕ')+' ', text)
    text = re.sub(r'\s+$', '', text)
    text = re.sub(r'([^\.,!\?\-…~])$', r'\1.', text)
    return text


from unidecode import unidecode
from phonemizer import phonemize

def expand_numbers(text):
  from text.english import normalize_numbers
  return normalize_numbers(text)

def lowercase(text):
  return text.lower()

def convert_to_ascii(text):
  return unidecode(text)


def english_cleaners2(text):
    '''Pipeline for English text, including abbreviation expansion. + punctuation + stress'''
    from text.english import expand_abbreviations,collapse_whitespace
    text = convert_to_ascii(text)
    text = lowercase(text)
    text = expand_abbreviations(text)
    phonemes = phonemize(text, language='en-us', backend='espeak', strip=True, preserve_punctuation=True, with_stress=True)
    phonemes = collapse_whitespace(phonemes)
    return phonemes

# if __name__ == '__main__':