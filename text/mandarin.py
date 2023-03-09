import os
import sys
import re
from pypinyin import lazy_pinyin, BOPOMOFO
import jieba
import cn2an
import logging

logging.getLogger('jieba').setLevel(logging.WARNING)
jieba.set_dictionary(os.path.dirname(sys.argv[0])+'/jieba/dict.txt')
jieba.initialize()


# new
_bopomofo_to_pinyin=[(re.compile('%s' % x[0], re.IGNORECASE), x[1]) for x in [
    ('ㄅㄛ', 'bo'),
    ('ㄆㄛ', 'po'),
    ('ㄇㄛ', 'mo'),
    ('ㄈㄛ', 'fo'),
    ('ㄅ', 'b '),
    ('ㄆ', 'p '),
    ('ㄇ', 'm '),
    ('ㄈ', 'f '),
    ('ㄉ', 'd '),
    ('ㄊ', 't '),
    ('ㄋ', 'n '),
    ('ㄌ', 'l '),
    ('ㄍ', 'g '),
    ('ㄎ', 'k '),
    ('ㄏ', 'h '),
    ('ㄐ', 'j '),
    ('ㄑ', 'q '),
    ('ㄒ', 'x '),
    ('ㄓ', 'zhi'),
    ('ㄔ', 'chi'),
    ('ㄕ', 'shi'),
    ('ㄖ', 'ri'),
    ('ㄗ', 'zi'),
    ('ㄘ', 'ci'),
    ('ㄙ', 'si'),
    ('ㄚ', 'a'),
    ('ㄛ', 'o'),
    ('ㄜ', 'e'),
    ('ㄝ', 'e'),
    ('ㄞ', 'ai'),
    ('ㄟ', 'ei'),
    ('ㄠ', 'ao'),
    ('ㄡ', 'ou'),
    ('ㄧㄢ', 'ian'),
    ('ㄩㄢ', 'üan'),
    ('ㄢ', 'an'),
    ('ㄧㄣ', 'in'),
    ('ㄩㄣ', 'ün'),
    ('ㄣ', 'en'),
    ('ㄤ', 'ang'),
    ('ㄧㄥ', 'ing'),
    ('ㄨㄥ', 'ueng'),
    ('ㄩㄥ', 'iong'),
    ('ㄥ', 'eng'),
    ('ㄦ', 'er'),
    ('ㄧ', 'i'),
    ('ㄨ', 'u'),
    ('ㄩ', 'ü'),
    ('ˉ', '1 '),
    ('ˊ', '2 '),
    ('ˇ', '3 '),
    ('ˋ', '4 '),
    # ('˙', ''),
    # ('，', ','),
    # ('。', '.'),
    # ('！', '!'),
    # ('？', '?'),
    # ('—', '-')
]]

_math_to_chinese= [(re.compile('%s' % x[0], re.IGNORECASE), x[1]) for x in [
    ('π','派'),
    ('\=','等于'),
    ('\^','乘方'),
    ('\+','加'),
    # ('\-','减'),
    ('\*','乘'),
    ('÷','除以'),
    # ('\/','斜杠'),
    ('<','小于'),
    ('>','大于'),
    ('ln','劳恩'),
    ('log','捞个'),
    ('sin','三嗯'),
    ('cos','可三嗯'),
    ('°','度'),
    ('log₂','以二为底的对数'),
    ('\(',' '),
    ('\)',' '),
    ('≈','约等于'),

]]


_latin_to_bopomofo = [(re.compile('%s' % x[0], re.IGNORECASE), x[1]) for x in [
    ('a', 'ㄟˉ'),
    ('b', 'ㄅㄧˋ'),
    ('c', 'ㄙㄧˉ'),
    ('d', 'ㄉㄧˋ'),
    ('e', 'ㄧˋ'),
    ('f', 'ㄝˊㄈㄨˋ'),
    ('g', 'ㄐㄧˋ'),
    ('h', 'ㄝˇㄑㄩˋ'),
    ('i', 'ㄞˋ'),
    ('j', 'ㄐㄟˋ'),
    ('k', 'ㄎㄟˋ'),
    ('l', 'ㄝˊㄛˋ'),
    ('m', 'ㄝˊㄇㄨˋ'),
    ('n', 'ㄣˉ'),
    ('o', 'ㄡˉ'),
    ('p', 'ㄆㄧˉ'),
    ('q', 'ㄎㄧㄡˉ'),
    ('r', 'ㄚˋ'),
    ('s', 'ㄝˊㄙˋ'),
    ('t', 'ㄊㄧˋ'),
    ('u', 'ㄧㄡˉ'),
    ('v', 'ㄨㄧˉ'),
    ('w', 'ㄉㄚˋㄅㄨˋㄌㄧㄡˋ'),
    ('x', 'ㄝˉㄎㄨˋㄙˋ'),
    ('y', 'ㄨㄞˋ'),
    ('z', 'ㄗㄟˋ')
]]

# List of (bopomofo, romaji) pairs:
_bopomofo_to_romaji = [(re.compile('%s' % x[0]), x[1]) for x in [
    ('ㄅㄛ', 'p⁼wo'),
    ('ㄆㄛ', 'pʰwo'),
    ('ㄇㄛ', 'mwo'),
    ('ㄈㄛ', 'fwo'),
    ('ㄅ', 'p⁼'),
    ('ㄆ', 'pʰ'),
    ('ㄇ', 'm'),
    ('ㄈ', 'f'),
    ('ㄉ', 't⁼'),
    ('ㄊ', 'tʰ'),
    ('ㄋ', 'n'),
    ('ㄌ', 'l'),
    ('ㄍ', 'k⁼'),
    ('ㄎ', 'kʰ'),
    ('ㄏ', 'h'),
    ('ㄐ', 'ʧ⁼'),
    ('ㄑ', 'ʧʰ'),
    ('ㄒ', 'ʃ'),
    ('ㄓ', 'ʦ`⁼'),
    ('ㄔ', 'ʦ`ʰ'),
    ('ㄕ', 's`'),
    ('ㄖ', 'ɹ`'),
    ('ㄗ', 'ʦ⁼'),
    ('ㄘ', 'ʦʰ'),
    ('ㄙ', 's'),
    ('ㄚ', 'a'),
    ('ㄛ', 'o'),
    ('ㄜ', 'ə'),
    ('ㄝ', 'e'),
    ('ㄞ', 'ai'),
    ('ㄟ', 'ei'),
    ('ㄠ', 'au'),
    ('ㄡ', 'ou'),
    ('ㄧㄢ', 'yeNN'),
    ('ㄢ', 'aNN'),
    ('ㄧㄣ', 'iNN'),
    ('ㄣ', 'əNN'),
    ('ㄤ', 'aNg'),
    ('ㄧㄥ', 'iNg'),
    ('ㄨㄥ', 'uNg'),
    ('ㄩㄥ', 'yuNg'),
    ('ㄥ', 'əNg'),
    ('ㄦ', 'əɻ'),
    ('ㄧ', 'i'),
    ('ㄨ', 'u'),
    ('ㄩ', 'ɥ'),
    ('ˉ', '→'),
    ('ˊ', '↑'),
    ('ˇ', '↓↑'),
    ('ˋ', '↓'),
    ('˙', ''),
    ('，', ','),
    ('。', '.'),
    ('！', '!'),
    ('？', '?'),
    ('—', '-')
]]

# List of (romaji, ipa) pairs:
_romaji_to_ipa = [(re.compile('%s' % x[0], re.IGNORECASE), x[1]) for x in [
    ('ʃy', 'ʃ'),
    ('ʧʰy', 'ʧʰ'),
    ('ʧ⁼y', 'ʧ⁼'),
    ('NN', 'n'),
    ('Ng', 'ŋ'),
    ('y', 'j'),
    ('h', 'x')
]]

# List of (bopomofo, ipa) pairs:
_bopomofo_to_ipa = [(re.compile('%s' % x[0]), x[1]) for x in [
    ('ㄅㄛ', 'p⁼wo'),
    ('ㄆㄛ', 'pʰwo'),
    ('ㄇㄛ', 'mwo'),
    ('ㄈㄛ', 'fwo'),
    ('ㄅ', 'p⁼'),
    ('ㄆ', 'pʰ'),
    ('ㄇ', 'm'),
    ('ㄈ', 'f'),
    ('ㄉ', 't⁼'),
    ('ㄊ', 'tʰ'),
    ('ㄋ', 'n'),
    ('ㄌ', 'l'),
    ('ㄍ', 'k⁼'),
    ('ㄎ', 'kʰ'),
    ('ㄏ', 'x'),
    ('ㄐ', 'tʃ⁼'),
    ('ㄑ', 'tʃʰ'),
    ('ㄒ', 'ʃ'),
    ('ㄓ', 'ts`⁼'),
    ('ㄔ', 'ts`ʰ'),
    ('ㄕ', 's`'),
    ('ㄖ', 'ɹ`'),
    ('ㄗ', 'ts⁼'),
    ('ㄘ', 'tsʰ'),
    ('ㄙ', 's'),
    ('ㄚ', 'a'),
    ('ㄛ', 'o'),
    ('ㄜ', 'ə'),
    ('ㄝ', 'ɛ'),
    ('ㄞ', 'aɪ'),
    ('ㄟ', 'eɪ'),
    ('ㄠ', 'ɑʊ'),
    ('ㄡ', 'oʊ'),
    ('ㄧㄢ', 'jɛn'),
    ('ㄩㄢ', 'ɥæn'),
    ('ㄢ', 'an'),
    ('ㄧㄣ', 'in'),
    ('ㄩㄣ', 'ɥn'),
    ('ㄣ', 'ən'),
    ('ㄤ', 'ɑŋ'),
    ('ㄧㄥ', 'iŋ'),
    ('ㄨㄥ', 'ʊŋ'),
    ('ㄩㄥ', 'jʊŋ'),
    ('ㄥ', 'əŋ'),
    ('ㄦ', 'əɻ'),
    ('ㄧ', 'i'),
    ('ㄨ', 'u'),
    ('ㄩ', 'ɥ'),
    ('ˉ', '→'),
    ('ˊ', '↑'),
    ('ˇ', '↓↑'),
    ('ˋ', '↓'),
    ('˙', ''),
    ('，', ','),
    ('。', '.'),
    ('！', '!'),
    ('？', '?'),
    ('—', '-')
]]

# List of (bopomofo, ipa2) pairs:
_bopomofo_to_ipa2 = [(re.compile('%s' % x[0]), x[1]) for x in [
    ('ㄅㄛ', 'pwo'),
    ('ㄆㄛ', 'pʰwo'),
    ('ㄇㄛ', 'mwo'),
    ('ㄈㄛ', 'fwo'),
    ('ㄅ', 'p'),
    ('ㄆ', 'pʰ'),
    ('ㄇ', 'm'),
    ('ㄈ', 'f'),
    ('ㄉ', 't'),
    ('ㄊ', 'tʰ'),
    ('ㄋ', 'n'),
    ('ㄌ', 'l'),
    ('ㄍ', 'k'),
    ('ㄎ', 'kʰ'),
    ('ㄏ', 'h'),
    ('ㄐ', 'tɕ'),
    ('ㄑ', 'tɕʰ'),
    ('ㄒ', 'ɕ'),
    ('ㄓ', 'tʂ'),
    ('ㄔ', 'tʂʰ'),
    ('ㄕ', 'ʂ'),
    ('ㄖ', 'ɻ'),
    ('ㄗ', 'ts'),
    ('ㄘ', 'tsʰ'),
    ('ㄙ', 's'),
    ('ㄚ', 'a'),
    ('ㄛ', 'o'),
    ('ㄜ', 'ɤ'),
    ('ㄝ', 'ɛ'),
    ('ㄞ', 'aɪ'),
    ('ㄟ', 'eɪ'),
    ('ㄠ', 'ɑʊ'),
    ('ㄡ', 'oʊ'),
    ('ㄧㄢ', 'jɛn'),
    ('ㄩㄢ', 'yæn'),
    ('ㄢ', 'an'),
    ('ㄧㄣ', 'in'),
    ('ㄩㄣ', 'yn'),
    ('ㄣ', 'ən'),
    ('ㄤ', 'ɑŋ'),
    ('ㄧㄥ', 'iŋ'),
    ('ㄨㄥ', 'ʊŋ'),
    ('ㄩㄥ', 'jʊŋ'),
    ('ㄥ', 'ɤŋ'),
    ('ㄦ', 'əɻ'),
    ('ㄧ', 'i'),
    ('ㄨ', 'u'),
    ('ㄩ', 'y'),
    ('ˉ', '˥'),
    ('ˊ', '˧˥'),
    ('ˇ', '˨˩˦'),
    ('ˋ', '˥˩'),
    ('˙', ''),
    ('，', ','),
    ('。', '.'),
    ('！', '!'),
    ('？', '?'),
    ('—', '-')
]]


def number_to_chinese(text):
    numbers = re.findall(r'\d+(?:\.?\d+)?', text)
    for number in numbers:
        text = text.replace(number, cn2an.an2cn(number), 1)
    return text

def math_to_chinese(text):
    for regex, replacement in _math_to_chinese:
        text = re.sub(regex, replacement, text)
    return text

def chinese_to_bopomofo(text):
    text = text.replace('、', '，').replace('；', '，').replace('：', '，')
    words = jieba.lcut(text, cut_all=False)
    text = ''
    for word in words:
        bopomofos = lazy_pinyin(word, BOPOMOFO)
        if not re.search('[\u4e00-\u9fff]', word):
            text += word
            continue
        for i in range(len(bopomofos)):
            bopomofos[i] = re.sub(r'([\u3105-\u3129])$', r'\1ˉ', bopomofos[i])
        if text != '':
            text += ' '
        text += ''.join(bopomofos)
    return text


def latin_to_bopomofo(text):
    for regex, replacement in _latin_to_bopomofo:
        text = re.sub(regex, replacement, text)
    return text

def bopomofo_to_pinyin(text):
    for regex, replacement in _bopomofo_to_pinyin:
        text = re.sub(regex, replacement, text)
        # print(text)
    return text

def bopomofo_to_romaji(text):
    for regex, replacement in _bopomofo_to_romaji:
        text = re.sub(regex, replacement, text)
    return text


def bopomofo_to_ipa(text):
    for regex, replacement in _bopomofo_to_ipa:
        text = re.sub(regex, replacement, text)
    return text


def bopomofo_to_ipa2(text):
    for regex, replacement in _bopomofo_to_ipa2:
        text = re.sub(regex, replacement, text)
    return text


def chinese_to_romaji(text):
    text = number_to_chinese(text)
    text = chinese_to_bopomofo(text)
    text = latin_to_bopomofo(text)
    text = bopomofo_to_romaji(text)
    text = re.sub('i([aoe])', r'y\1', text)
    text = re.sub('u([aoəe])', r'w\1', text)
    text = re.sub('([ʦsɹ]`[⁼ʰ]?)([→↓↑ ]+|$)',
                  r'\1ɹ`\2', text).replace('ɻ', 'ɹ`')
    text = re.sub('([ʦs][⁼ʰ]?)([→↓↑ ]+|$)', r'\1ɹ\2', text)
    return text


def chinese_to_lazy_ipa(text):
    text = chinese_to_romaji(text)
    for regex, replacement in _romaji_to_ipa:
        text = re.sub(regex, replacement, text)
    return text


def chinese_to_ipa(text):
    text = math_to_chinese(text)
    text = number_to_chinese(text)
    text = chinese_to_bopomofo(text)
    text = latin_to_bopomofo(text)
    text = bopomofo_to_ipa(text)
    text = re.sub('i([aoe])', r'j\1', text)
    text = re.sub('u([aoəe])', r'w\1', text)
    text = re.sub('([sɹ]`[⁼ʰ]?)([→↓↑ ]+|$)',
                  r'\1ɹ`\2', text).replace('ɻ', 'ɹ`')
    text = re.sub('([s][⁼ʰ]?)([→↓↑ ]+|$)', r'\1ɹ\2', text)
    return text


def chinese_to_ipa2(text):
    text = number_to_chinese(text)
    text = chinese_to_bopomofo(text)
    text = latin_to_bopomofo(text)
    text = bopomofo_to_ipa2(text)
    text = re.sub(r'i([aoe])', r'j\1', text)
    text = re.sub(r'u([aoəe])', r'w\1', text)
    text = re.sub(r'([ʂɹ]ʰ?)([˩˨˧˦˥ ]+|$)', r'\1ʅ\2', text)
    text = re.sub(r'(sʰ?)([˩˨˧˦˥ ]+|$)', r'\1ɿ\2', text)
    return text
