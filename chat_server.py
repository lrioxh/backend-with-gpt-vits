#coding:utf-8

from scipy.io.wavfile import write
from text import text_to_sequence,text_to_sequence2
from models import SynthesizerTrn
import utils
import commons
import sys
import regex as re
import json
import os
import time
import torch
from torch import no_grad, LongTensor
# import logging
# from text.symbols import symbols
import openai
import base64
from flask import Flask, request,make_response, jsonify
from asr_server import whisper_ASR
# import requests
# from threading import Thread, Event
# from queue import Queue
# import tiktoken
# encoding = tiktoken.get_encoding("p50k_base")
app = Flask(__name__)
openkey="c2stWXVqbjlEYjR1SW5PYzlka1psTHpUM0JsYmtGSlR1QnRaQnlNZVA0U21lVU5ka21Q"
openai.api_key = str(base64.b64decode(openkey.encode("ascii")), 'utf-8')
# logging.getLogger('numba').setLevel(logging.WARNING)

zh_pattern = re.compile(r'[\u4e00-\u9fa5]')
en_pattern = re.compile(r'[a-zA-Z]')
jp_pattern = re.compile(r'[\u3040-\u30ff\u31f0-\u31ff]')
kr_pattern = re.compile(r'[\uac00-\ud7af\u1100-\u11ff\u3130-\u318f\ua960-\ua97f]')
num_pattern=re.compile(r'[0-9]')
comma=r"(?<=[.。!！?？；;，,、:：'\"‘“”’()（）《》「」~——])"    #向前匹配但固定长度
tags={'ZH':'[ZH]','EN':'[EN]','JP':'[JA]','KR':'[KR]'}
# stop_event = Event()
# msg_queue = Queue()

def restart_program():
    python = sys.executable
    os.execl(python, python, * sys.argv)

# def get_asr_msg():
#     # from asr_server import whisper_ASR,sr
#     # asr=whisper_ASR(server_config)
#     # r = sr.Recognizer() #创建识别类
#     # mic = sr.Microphone() #创建麦克风对象
#     # print()
#     return asr.get_msg()

# def start_thread(size,device,model_path):
#     # 启动新线程
#     t = Thread(target=to_whisper,args=(size,device,model_path))
#     t.start()
#     return 'Started'

# def stop_thread():
#     # 设置Event对象，停止线程运行
#     stop_event.set()
#     return 'Stopped'

# def to_whisper(size,device,model_path):
#     from asr import whisper_ASR,sr
#     _ASR=whisper_ASR(size,device,model_path)
#     r = sr.Recognizer() #创建识别类
#     mic = sr.Microphone() #创建麦克风对象
#     while not stop_event.is_set():
#         # 这里可以写你的逻辑，获取msg并返回
#         msg = 'Hello World'
#         # print(msg)
#         # 通过Flask提供的方法将数据返回到主线程
#         msg_queue.put(msg)
#         # 线程休眠，避免过于频繁的操作
#         stop_event.wait(1)

def tag_cjke(text):
    '''为中英日韩加tag,中日正则分不开，故先分句分离中日再识别，以应对大部分情况
    TODO 另一种思路是匹配邻接假名的汉字，也需要先分句'''
    sentences = re.split(r"([.。!！?？；;，,、:：'\"‘“”’()（）【】《》「」~——]+ *(?![0-9]))", text) #分句排除小数点
    sentences.append("")
    sentences = ["".join(i) for i in zip(sentences[0::2],sentences[1::2])]
    # print(sentences)
    prev_lang=None
    tagged_text = ""
    for s in sentences:
        #全为符号跳过
        nu = re.sub(r'[\s\p{P}]+', '', s, flags=re.U).strip()
        if len(nu)==0:
            continue
        # print(s)
        # s=s.strip()
        s = re.sub(r'[()（）《》「」【】‘“”’]+', '', s)
        jp=re.findall(jp_pattern, s)
        #本句含日语字符判断为日语
        if len(jp)>0:  
            prev_lang,tagged_jke=tag_jke(s,prev_lang)
            tagged_text +=tagged_jke
        else:
            prev_lang,tagged_cke=tag_cke(s,prev_lang)
            tagged_text +=tagged_cke
    return tagged_text

def tag_jke(text,prev_sentence=None):
    '''为英日韩加tag'''
    # 初始化标记变量
    tagged_text = ""
    prev_lang = None
    tagged=0
    # 遍历文本
    for char in text:
        # 判断当前字符属于哪种语言
        if jp_pattern.match(char):
            lang = "JP"
        elif zh_pattern.match(char):
            lang = "JP"
        elif kr_pattern.match(char):
            lang = "KR"
        elif en_pattern.match(char):
            lang = "EN"
        # elif num_pattern.match(char):
        #     lang = prev_sentence
        else:
            lang = None
            tagged_text += char
            continue
        # 如果当前语言与上一个语言不同，就添加标记
        if lang != prev_lang:
            tagged=1
            if prev_lang==None: # 开头
                tagged_text =tags[lang]+tagged_text
            else:
                tagged_text =tagged_text+tags[prev_lang]+tags[lang]

            # 重置标记变量
            prev_lang = lang

        # 添加当前字符到标记文本中
        tagged_text += char
    
    # 在最后一个语言的结尾添加对应的标记
    if prev_lang:
            tagged_text += tags[prev_lang]
    if not tagged:
        prev_lang=prev_sentence
        tagged_text =tags[prev_lang]+tagged_text+tags[prev_lang]

    return prev_lang,tagged_text

def tag_cke(text,prev_sentence=None):
    '''为中英韩加tag'''
    # 初始化标记变量
    tagged_text = ""
    prev_lang = None
    tagged=0
    
    # 遍历文本
    for char in text:
        # 判断当前字符属于哪种语言
        if zh_pattern.match(char):
            lang = "ZH"
        elif kr_pattern.match(char):
            lang = "KR"
        elif en_pattern.match(char):
            lang = "EN"
        # elif num_pattern.match(char):
        #     lang = prev_sentence
        else:
            lang = None
            tagged_text += char
            continue

        # 如果当前语言与上一个语言不同，就添加标记
        if lang != prev_lang:
            tagged=1
            if prev_lang==None: # 开头
                tagged_text =tags[lang]+tagged_text
            else:
            # print(char,prev_lang,lang)
                tagged_text =tagged_text+tags[prev_lang]+tags[lang]

            # 重置标记变量
            prev_lang = lang
        # 添加当前字符到标记文本中
        tagged_text += char
    
    # 在最后一个语言的结尾添加对应的标记
    if prev_lang:
            tagged_text += tags[prev_lang]
    # print(text)
    if tagged==0:
        prev_lang=prev_sentence
        tagged_text =tags[prev_lang]+tagged_text+tags[prev_lang]
    return prev_lang,tagged_text


def get_label_value(text, label, default, warning_name='value'):
    value = re.search(rf'\[{label}=(.+?)\]', text)
    if value:
        try:
            text = re.sub(rf'\[{label}=(.+?)\]', '', text, 1)
            value = float(value.group(1))
        except:
            print(f'Invalid {warning_name}!')
            sys.exit(1)
    else:
        value = default
    return value, text


def get_label(text, label):
    if f'[{label}]' in text:
        return True, text.replace(f'[{label}]', '')
    else:
        return False, text


def str2token(text):
    '''近似'''
    return len(text.encode('gbk'))
    # return len(encoding.encode(text))

class api_server():
    def __init__(self,config_path='./server_config.json') -> None:
        self.cfg=utils.get_hparams_from_file(config_path)
        self.net_g_ms=None
        self.hps_ms=None
        self.n_symbols=0
        self.sys_title=None     # chatGPT system prompt
        self.device=torch.device(self.cfg.device)
        self.res_path=f"{self.cfg.cache_path}/res.wav"
        self.log=[]             # 聊天上下文缓存
        self.log_path=None
        self.token=0            # openai request 长度
        # self.log_format="csv"   # csv/jsonl 保存聊天log格式
        # self.log_pattern="acumu"   # acumu/single 记录模式，累积记录或单条，未启用
        self._time=time.strftime('%Y%m%d%H%M%S',time.localtime())
        self.update_gpt()
    
        
    # 基本功能
    def update_gpt(self):
        '''更新gpt设置'''
        self.log_path=self.get_log_path()
        if self.cfg.gpt.api=='chatGPT':
            self.chatGPT_init(self.cfg.gpt.name,self.cfg.gpt.lang)
    def update_vits(self):
        '''更新vits设置'''
        self.load_moudle()
    def get_speaker(self):
        '''返回speaker字典'''
        speakers=self.hps_ms.speakers if 'speakers' in self.hps_ms.keys() else ['0']
        # print(speakers,type(speakers))
        if not isinstance(speakers,list):
            speakers={_id:name for name,_id in speakers.items()}
        else:
            speakers={_id:name for _id,name in enumerate(speakers)}
        # print(speakers,type(speakers))
        return speakers
    def get_log_path(self):
        '''生成log save path'''
        return rf"{self.cfg.log_root}/{self.cfg.gpt.api}_{self.cfg.gpt.name}_{self._time}.{self.cfg.log_save_fmt}"
    def log_jsonl(self,prompt,reply):
        '''保存jsonl'''
        pc_pair= {"prompt": prompt,
                  "completion": reply}   # prompt-completion
        pc_pair=json.dumps(pc_pair,ensure_ascii=False)
        print(pc_pair)
        with open(self.log_path,"a",encoding='utf-8') as f:
            f.write(pc_pair+'\n')
    def log_csv(self,prompt,reply):
        '''保存csv'''
        line=f'"{prompt}","{reply}"'
        # print(line)
        if not os.path.exists(self.log_path):
            line='prompt,completion\n'+line
        with open(self.log_path,"a",encoding='utf-8-sig') as f:     #带签名bom的utf8
            f.write(line+'\n')
    def save_log(self,prompt,reply):
        if self.cfg.log_save_fmt=='jsonl':
            self.log_jsonl(prompt,reply)
        elif self.cfg.log_save_fmt=='csv':
            self.log_csv(prompt,reply)
    def speakers_str(self):
        speakers=self.get_speaker()
        s=""
        for id, name in speakers.items():
            s+=f"{id}:{name}  "
        s+=f"\t当前:{speakers[self.cfg.vits[self.cfg.pipeline]._id]}"
        return s
    def get_models(self):
        # return re.sub(r'["\{\}]+','',json.dumps(self.cfg.vits))+f"\t当前: {self.cfg.pipeline}"
        return "".join(list(self.cfg.vits.keys()))+f"\t当前: {self.cfg.vits[self.cfg.pipeline]}"
    # 指令处理
    def command(self,text):
        '''可以自定义指令'''
        print('reveive command...')
        # global pipeline
        for cmd in text.strip().split('/'):
            cmd=cmd.strip()
            if len(cmd)==0:continue
            elif len(re.sub(r'[0-9]+', '', cmd))==0:
                self.cfg.vits[self.cfg.pipeline]._id=int(cmd)

            elif cmd in self.cfg.vits.keys():
                self.cfg.pipeline=cmd
                self.update_vits()
            elif cmd in ['cuda','cpu']:
                self.device=torch.device(cmd);self.update_vits();asr.reload(self.cfg)
            elif cmd in ['gpt3','chatGPT']:
                self.cfg.gpt.api=cmd
                self.update_gpt()
            elif cmd=='speakers':
                return self.speakers_str()
            # cfg[pipeline]=0
            elif cmd=='models':
                return self.get_models()
            elif cmd=='restart':restart_program()
            # elif cmd=='listen':return get_asr_msg()
            # elif cmd=='quit':return stop_thread()
            elif '=' in cmd:
                k,v=cmd.split('=')
                if k in self.cfg.vits.keys():
                    self.cfg.vits[k]._id=int(v)
                    self.cfg.pipeline=k
                    self.update_vits()
                elif k in self.cfg.gpt.keys():
                    self.cfg.gpt[k]=v
                    self.update_gpt()
                else:return 'Error: 未知指令'
            else:
                return 'Error: 未知指令'         
        

    # 聊天
    def chat_gpt3(self,text,name,lang):
        '''
        prompt=
        User:缓存+{text}
        {name}:reply
        缓存溢出阈值会清理最开始的一条问答

        返回提问和回答
        '''
        # if lang=='en':identity = "reply in english"
        # elif lang=='ja':identity = "用日语回答,日本語て答えてください"
        # else:
        #     identity = "用中文回答"
        prompt0=f"\nUser:{text}"
        if text == 'quit':
            return prompt0
        gpt_cfg=self.cfg.gpt3
        while self.token+str2token(text) >gpt_cfg.log_thr:    #阈值
            print('token overflow')
            # print(self.token,len(self.log[0].encode('gbk')))
            self.token-=str2token(text) 
            self.log=self.log[1:]
        prompt="".join(self.log)+prompt0+f"\n{name}:"

        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=gpt_cfg.temperature,    #较高的值（如 0.8）将使输出更加随机，而较低的值（如 0.2）将使其更加集中和确定，默认1
            max_tokens=gpt_cfg.max_tokens,    #长度限制
            # top_p=1.0,
            frequency_penalty=gpt_cfg.frequency_penalty,  # 降低模型逐字重复同一行的可能性
            presence_penalty=gpt_cfg.presence_penalty,   # 增加模型谈论新主题的可能性
            # stop="\n"
        )
        reply=response['choices'][0]['text'].strip().replace('\n',' ')
        # print(reply)
        self.log.append(prompt0+f"\n{name}:{reply}")
        # print(log)
        self.token=response['usage']['total_tokens']
        print("cache log:",self.token)
        # print(response,self.token,self.log)
        return prompt,reply
    
    def chatGPT_init(self,name,lang):
        if lang=='en':
            self.sys_title={"role": "system", "content": 
                    f'Your name is {name}. '+
                    self.cfg.chatGPT.sys_title
                    }
        
        elif lang=='zh':
            self.sys_title={"role": "system", "content": 
                    f'你的名字是{name}。\n'+
                    self.cfg.chatGPT.sys_title
            }
        
        elif lang=='jp':
            self.sys_title={"role": "system", "content": 
                    f'あなたの名前は{name}で、'+
                    self.cfg.chatGPT.sys_title
                    }
        self.token=str2token(self.sys_title['content'])
        # self.save_log(self.sys_title['content'],"")

    def chatGPT(self,text,name):
        '''
        messages=
        {sys:title}+
        [{log}]+
        {prompt}
        缓存溢出阈值会清理最开始的一条log

        返回提问和回答
        '''
        # if lang=='en':identity = "reply in english"
        # elif lang=='ja':identity = "用日语回答,日本語て答えてください"
        # else:
        #     identity = "用中文回答"
        
        gpt_cfg=self.cfg.chatGPT
        while self.token+str2token(text) >gpt_cfg.log_thr:    #阈值
            print('token overflow',end=' ')
            self.token-=str2token(self.log[0]['content'])//2    #经验/2
            self.log=self.log[1:]
            print(self.token)
            
        prompt={"role": "user", "content": f"{text}"}
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",
            messages=[self.sys_title,*self.log,prompt],
            temperature=gpt_cfg.temperature,    #较高的值（如 0.8）将使输出更加随机，而较低的值（如 0.2）将使其更加集中和确定，默认1
            max_tokens=gpt_cfg.max_tokens,    #回复长度限制
            # top_p=1.0,
            frequency_penalty=gpt_cfg.frequency_penalty,  # 降低模型逐字重复同一行的可能性
            presence_penalty=gpt_cfg.presence_penalty,   # 增加模型谈论新主题的可能性
            # stop="\n"
        )
        # print(response)
        reply=response['choices'][0]['message']['content'].strip().replace('\n',' ')
        
        self.log.extend([prompt,response['choices'][0]['message']])
        # print(log)
        self.token=response['usage']['total_tokens']
        print("cache log:",self.token)
        # print(response,self.token,self.log)
        return reply
    
    def chat(self,text):
        '''chat接口,保存log文件'''
        try:
            print('getting reply...')
            if self.cfg.gpt.api=='chatGPT':
                reply= self.chatGPT(text,self.cfg.gpt.name)
                prompt=text
            elif self.cfg.gpt.api=='gpt3':
                prompt,reply=self.chat_gpt3(text,self.cfg.gpt.name,self.cfg.gpt.lang)
        
        except Exception as e:
            print("chat faild:",e)
            return
        try:
            # save log
            print('log saving...')
            # print(prompt,reply)
            self.save_log(prompt,reply)

        except Exception as e:
            print("save log faild:",e)
        return  reply
    
    # vits
    def load_moudle(self):
        '''加载模型,只在server启动或更改所需模型时运行'''
        # root=r'pipeline/'
        model=self.cfg.vits[self.cfg.pipeline].model
        config=self.cfg.vits[self.cfg.pipeline].config

        self.hps_ms = utils.get_hparams_from_file(config)
        n_speakers = self.hps_ms.data.n_speakers if 'n_speakers' in self.hps_ms.data.keys() else 0
        
        self.n_symbols = len(self.hps_ms.symbols) if 'symbols' in self.hps_ms.keys() else 0
        # speakers = hps_ms.speakers if 'speakers' in hps_ms.keys() else ['0']
        # use_f0 = hps_ms.data.use_f0 if 'use_f0' in hps_ms.data.keys() else False
        # print(self.n_symbols)
        self.net_g_ms = SynthesizerTrn(
            self.n_symbols,
            self.hps_ms.data.filter_length // 2 + 1,
            self.hps_ms.train.segment_size // self.hps_ms.data.hop_length,
            n_speakers=n_speakers,
            # emotion_embedding=emotion_embedding,
            **self.hps_ms.model)
        _ = self.net_g_ms.eval().to(self.device)
        _ = utils.load_checkpoint(model, self.net_g_ms,self.device)
        # return net_g_ms

    def get_text(self,text):
        '''
        注意cleaner&symbols
        genshin,yuzu和vctk采用了不同cleaner路线,
        具体来说genshin基于拼音,yuzu&cjke转注音符號bopomofo,最终基于国际音标ipa,vctk则是英语音标
        yuzu&cjke除语言支持外,所用ipa略有不同,详见_romaji_to_ipa

        yuzu&cjke的symbols在config中,genshin和vctk则在text.symbols中

        返回text的量化序列
        '''

        if self.cfg.pipeline=='genshin':
            text=text.lower().replace('transformer','穿丝否莫').replace('diffusion','地府幽深')     #人工智能，主要是人工 #部分移动到cleaner中
            text_norm = text_to_sequence2(text, self.hps_ms.symbols, self.hps_ms.data.text_cleaners)
        elif self.cfg.pipeline in self.cfg.vits.keys():
            if self.cfg.vits[self.cfg.pipeline].cjke:
                text=tag_cjke(text)
            text_norm = text_to_sequence(text, self.hps_ms.symbols, self.hps_ms.data.text_cleaners)

        if self.hps_ms.data.add_blank:
            text_norm = commons.intersperse(text_norm, 0)

        text_norm = LongTensor(text_norm)
        return text_norm

    def infer(self,text):
        '''
        tts推理
        '''     
        if self.n_symbols != 0:
            
            model_cfg=self.cfg.vits[self.cfg.pipeline]
            length_scale, text = get_label_value(
                text, 'LENGTH', model_cfg.length_scale, 'length scale')      # 控制整体语速。默认为1.
            noise_scale, text = get_label_value(
                text, 'NOISE', model_cfg.noise_scale, 'noise scale')    # 控制感情等变化程度。默认为0.667
            noise_scale_w, text = get_label_value(
                text, 'NOISEW', model_cfg.noise_scale, 'deviation of noise')  # 控制音素发音长度变化程度。默认为0.8
            # cleaned, text = get_label(text, 'CLEANED')

            print('Cleaned text: ')     # print在_clean_text
            stn_tst = self.get_text(text)

            with no_grad():
                x_tst = stn_tst.unsqueeze(0)
                x_tst_lengths = LongTensor([stn_tst.size(0)])
                sid = LongTensor([self.cfg.vits[self.cfg.pipeline]._id])

                audio = self.net_g_ms.infer(x_tst.to(self.device), x_tst_lengths.to(self.device), sid=sid.to(self.device),
                    noise_scale=torch.tensor(noise_scale).to(self.device),noise_scale_w=torch.tensor(noise_scale_w).to(self.device), length_scale=torch.tensor(length_scale).to(self.device))\
                    [0][0, 0].data.cpu().float().numpy()


            write(self.res_path, self.hps_ms.data.sampling_rate, audio)
            # if self.pipeline=='vctk':speaker='vctk'
            speakers=self.get_speaker()  
            speaker=speakers[self.cfg.vits[self.cfg.pipeline]._id] if self.cfg.pipeline!='vctk' else 'vctk'
            print(f'Successfully in {speaker}')


@app.route("/chat", methods=["GET"])
def chat():
    '''处理前端信息和后端响应'''
    # 接收客户端的聊天文本
    text = request.args.get("Text", "")
    print("文本: %s" % text)
    
    if text[0]=="/":
        if text=="//":
            text=asr.get_msg()
        else:
            res=vist_chat.command(text)
            print(vist_chat.cfg.gpt,vist_chat.cfg.pipeline,vist_chat.cfg.vits[vist_chat.cfg.pipeline]._id,vist_chat.device)
            # vist_chat.load_moudle()
            rsp = make_response()
            if res:
                print(res)
                rsp.headers.add_header("Text", res.encode("utf-8"))
            else:
                rsp.headers.add_header("Text", "更改成功".encode("utf-8"))
            return rsp
    
    rsp = make_response()
    reply=vist_chat.chat(text)
    print('Raw reply:')
    print(reply)
    reply= re.sub(r'[\s]+', ' ', reply)
    vist_chat.infer(reply)
    # 响应头中添加Text字段
    rsp.headers.add_header("Text", reply.encode("utf-8"))

    # 响应body中写入音频数据
    with open(vist_chat.res_path, "rb") as f:
        rsp.set_data(f.read())
    return rsp


if __name__ == '__main__':
    server_config=r'./server_config.json'
    vist_chat=api_server(server_config)
    vist_chat.load_moudle()
    asr=whisper_ASR(server_config)
    
    app.run("0.0.0.0", 55000,debug=True) 


    # vist_chat.cfg.pipeline='yumag'
    # vist_chat.cfg.vits['yumag']._id=165 #
    # vist_chat.load_moudle()
    # vist_chat.infer('うるさい！これは日本語テストです。宜しくお願い致します！')
    # vist_chat.infer('这是diffusion，これはtransformer，中嘞哥，"饺子"delicious食べます。原神怎么你了!?うるさい！')
    # vist_chat.infer('喵~ 晚上好主人，我是一只名叫"MOSS"的猫娘，很高兴能够与您相遇。我有着柔软的毛发和尖尖的耳朵，虽然有些害羞但是很愿意与您交流喵~')#今天天气真是好呢！なんて素晴らしい天気なんでしょう！The sunshine feels so warm. 现在是不是应该喝点水呢？水のお代わりでもしていいですか、ご主人様？')
    # vist_chat.infer('现在是不是应该喝点水呢？水のお代わりでもしていいですか、ご主人様？')
    # vist_chat.infer('这是英文,this is Chinese')
    # vist_chat.infer("和弦进行有很多不同的方式，以下是一些常见的例子：  1. 1-4-5:这是一个非常基础的和弦进行,"+
    #                 "在流行音乐中非常常见。例如，Elvis Presley 的歌曲《Blue Suede Shoes》就采用了这个和弦进行。  2. 2-5-1：这个和弦进行在爵士乐中非常流行。例如，Duke Ellington 的歌曲《Take the A Train》就采用了这个和弦进行。  3. 6-4-1-5：这也是一个非常流行的和弦进行，在很多流行歌曲中都可以听到。例如，The Beatles 的歌曲《Let it Be》就采用了这个和弦进行。  以上只是一些例子，并不代表全部。希望能对你有所帮助！")
    # vist_chat.infer('お——2002年的第一场雪，A bit later than usual~')
    # vist_chat.infer("可以使用三角函数的cos函数来计算，cos(60°) = cos(π/3) = 0.5。自然对数函数ln(x)，其中x为10。")
    # vist_chat.infer("x，y，z,这是π≈3.1415926")
    # print(len(vist_chat.get_speaker()))
    # print(vist_chat.speakers_str())
