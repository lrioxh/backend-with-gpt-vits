import whisper
import torch
import speech_recognition as sr
import utils

from flask import Flask, request,make_response
app = Flask(__name__)

class whisper_ASR():
    def __init__(self,config_path='./server_config.json') -> None:
        self.cfg=utils.get_hparams_from_file(config_path)
        self.device=torch.device(self.cfg.device)
        self.model = whisper.load_model(self.cfg.whisper.size,self.device,self.cfg.whisper.model_path)
        # pass

    def recognize(self,file):
        # load audio and pad/trim it to fit 30 seconds
        audio = whisper.load_audio(file)

        audio = whisper.pad_or_trim(audio)

        # make log-Mel spectrogram and move to the same device as the model
        mel = whisper.log_mel_spectrogram(audio).to(self.model.device)

        # detect the spoken language
        _, probs = self.model.detect_language(mel)
        print(f"Detected language: {max(probs, key=probs.get)}")

        # decode the audio
        options = whisper.DecodingOptions()
        result = whisper.decode(self.model, mel, options)
        print(result.text)
        return result.text

@app.route("/asr", methods=["GET"])
def asr_():
    '''处理前端信息和后端响应'''
    with mic as source:
        r.adjust_for_ambient_noise(source) #减少环境噪音
        audio = r.listen(source, timeout=1000) #录音，1000ms超时
    with open('cache/' + f"test.wav", "wb") as f:
        f.write(audio.get_wav_data(convert_rate=16000)) #写文件
    message = asr.recognize(f"cache/test.wav")
    return message
    
if __name__ == '__main__':
    server_config=r'./server_config.json'
    asr=whisper_ASR(server_config)
    r = sr.Recognizer() #创建识别类
    mic = sr.Microphone() #创建麦克风对象
    
    app.run("0.0.0.0", 55001,debug=True) 