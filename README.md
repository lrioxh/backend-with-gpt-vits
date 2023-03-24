# Backend server with GPT & VITS

TODO：whiper&riva语音输入



GPT方面接入chatGPT和gpt3 api，有记忆连续对话，可切换

VITS方面详见表格，中英日韩自动tag读出

代码基于[MoeGoe](https://github.com/CjangCjengh/MoeGoe)参考[vits_with_chatgpt-gpt3](https://github.com/Paraworks/vits_with_chatgpt-gpt3)、[VITS-fast-fine-tuning](https://github.com/Plachtaa/VITS-fast-fine-tuning)，感谢各位大佬

## Requirements

##### 0. 本项目仅含后端，需要前端图形界面（比如 [Live2DMascot](https://github.com/Arkueid/Live2DMascot) ）

##### 1. 依赖参考

```
pip install -r requirements.txt
```

```
pip install -U openai-whisper
```

##### 2. openai-python

openai 0.27.0 pypi已更新，可直接pip安装，已成功安装0.27以上版本可略过

> 最新库可能需要手动安装
>
> [仓库](https://github.com/openai/openai-python)下载源码，不要下载release
>
> 激活你的环境，cd源码目录
>
> ```
> pip install .
> ```
>
> OpenAI API Key: 自行注册或[联系我](https://space.bilibili.com/23698455)
>

##### espeak

vctk依赖于espeak，不使用该模型可以略过

> [关于espeak安装](https://github.com/bootphon/phonemizer/issues/44)
>
> 下载安装[espeak-ng](https://github.com/espeak-ng/espeak-ng/releases)
>
> 添加环境变量
>
> ```
> PHONEMIZER_ESPEAK_PATH “C:\Program Files\eSpeak NG”
> PHONEMIZER_ESPEAK_LIBRARY "C:\Program Files\eSpeak NG\libespeak-ng.dll"
> ```
>
> 或conda环境可以
>
> ```
> conda env config vars set PHONEMIZER_ESPEAK_PATH=“C:\Program Files\eSpeak NG”`
> conda env config vars set PHONEMIZER_ESPEAK_LIBRARY="C:\Program Files\eSpeak NG\libespeak-ng.dll"
> ```
>



## Pre-trained models

技术交流，严禁商用

| 名称                                                         | 音素     | 语言        | 语料     | 来源                                                         | 人   |
| ------------------------------------------------------------ | -------- | ----------- | -------- | ------------------------------------------------------------ | ---- |
| [vctk(base)](https://drive.google.com/drive/folders/1ksarh-cJf3F5eKJjLVWY0X1j1qsQqiS2) | 英文音标 | en,zh       | vctk     | [vits](https://github.com/jaywalnut310/vits)                 | 110  |
| [yuzu](https://sjtueducn-my.sharepoint.com/:u:/g/personal/cjang_cjengh_sjtu_edu_cn/EQ0IKHchgzZAt0E6GryW17EBsIlIkmby6BcO9FtoODjwNQ?e=5uzWtj) | 国际音标 | jp,zh       | yuzusoft | [moegeo](https://github.com/CjangCjengh/TTSModels)           | 4    |
| [cjke](https://sjtueducn-my.sharepoint.com/:u:/g/personal/cjang_cjengh_sjtu_edu_cn/EfW8nGHBejxEisHhxVjq1v4BOxqT7YJ-p_pudTPEoDDxxw?e=O8DNrR) | 国际音标 | jp,zh,en,kr | anime    | [moegeo](https://github.com/CjangCjengh/TTSModels)           | 2890 |
| [genshin](https://huggingface.co/lrioxh/vits/blob/main/G_809000.pth) | 汉语拼音 | zh          | 原       | [link](http://nscc-gz.cn/)                                   | 53   |
| [uma87](https://huggingface.co/spaces/Plachta/VITS-Umamusume-voice-synthesizer/blob/main/pretrained_models/G_jp.pth) | 罗马音   | jp          | 马       | [Plachta](https://huggingface.co/spaces/Plachta/VITS-Umamusume-voice-synthesizer) | 87   |
| [yumag](https://huggingface.co/spaces/Plachta/VITS-Umamusume-voice-synthesizer/blob/main/pretrained_models/G_trilingual.pth) | 国际音标 | zh,jp,en    | 马yuzu原 | [Plachta](https://huggingface.co/spaces/Plachta/VITS-Umamusume-voice-synthesizer) | 147  |
| [humag](https://huggingface.co/spaces/Plachta/VITS-Umamusume-voice-synthesizer) | 国际音标 | zh,jp       | 马崩原   | [sayashi](https://huggingface.co/spaces/sayashi/vits-uma-genshin-honkai) | 804  |

更改了genshin的cleaner可以读简单的数学公式。

## Run

运行server.py 与 前端

注意端口与前端一致

[配置文件](https://github.com/lrioxh/backend-with-gpt-vits/blob/main/server_config.json)可以添加模型，更改默认配置

![image-20230310114752315](http://m.qpic.cn/psc?/V52VtAJj03gqAZ1Zi9Ot2f5BBX0L3sbF/bqQfVz5yrrGYSXMvKr.cqWsrEn6Fs7jn8YSikLlBqs5oRsu5FD3zxHbcEtAHADMqlT*6bPEXcxyPhzd0QLOp2T7M4ouw7BlCEuiBRpsfdc0!/b&bo=2wEpAQAAAAADB9A!&rf=viewer_4)

## Fuctions
指令集，用于更改设定和执行一些简单功能，无需指令也可正常运行，运行后可随时输入指令

| 指令                       | 作用                       | 说明                                  | 示例       |
| -------------------------- | -------------------------- | ------------------------------------- | ---------- |
| /{model_name}              | 更换vits模型               | 合法值见模型名称，默认yumag           | /uma87     |
| /{model_name}={speaker_id} | 更换vits模型同时指定说话人 | speaker_id合法值可通过/speakers查看   | /humag=328 |
| /{speaker_id}              | 指定当前模型说话人         | 同上                                  | /233       |
| /speakers                  | 显示可用说话人和当前说话人 | -                                     | -          |
| /models                    | 显示可用模型和当前模型     | -                                     | -          |
| /{device}                  | 更换推理设备               | [cpu,cuda], 默认cuda                  | /cpu       |
| /name={str}                | 设置对话AI名字             | 给你的幻想朋友起个名                  | /name=MOSS |
| /api={api}, /{api}         | 更换对话API                | api合法值[gpt3, chatGPT]，默认chatGPT | /gpt3      |
| /restart                   | 重启服务，重置设定         | -                                     | -          |

bug反馈可提交issue

## Reference
- [jaywalnut310/vits: VITS: Conditional Variational Autoencoder with Adversarial Learning for End-to-End Text-to-Speech](https://github.com/jaywalnut310/vits)
- [CjangCjengh/MoeGoe: Executable file for VITS inference](https://github.com/CjangCjengh/MoeGoe)
- [Paraworks/vits_with_chatgpt-gpt3](https://github.com/Paraworks/vits_with_chatgpt-gpt3)
- [w4123/vits: VITS: Conditional Variational Autoencoder with Adversarial Learning for End-to-End Text-to-Speech](https://github.com/w4123/vits)

+ [Plachtaa/VITS-fast-fine-tuning: This repo is a pipeline of VITS finetuning for fast speaker adaptation TTS, and any-to-any voice conversion](https://github.com/Plachtaa/VITS-fast-fine-tuning)