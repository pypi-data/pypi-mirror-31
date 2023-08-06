#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""本模块提供百度语音API类 - BaiduYuyin
"""

__author__ = 'Zhao Xin <7176466@qq.com>'
__copyright__ = 'All rights reserved © 1975-2018 Zhao Xin'
__license__ = 'GNU General Public License v3 (GPLv3)'
__version__ = '2018-03-28'


import os
import io
import time
import base64
import pygame
import requests
from zhao.xin_net import local_mac_addr

MAC = local_mac_addr()


class BaiduYuyin(object):
    """百度语音API

    文档：http://yuyin.baidu.com/docs/

    使用方法：
        >>> yaya = BaiduYuyin(api_key='你的百度开发者API_KEY',
                              secret_key='你的百度开发者SECRET_KEY')
        >>> yaya.tts_setup(speed=3, person=4)
        >>> yaya.tts('我是百度语音的丫丫')
    """

    def __init__(self, api_key=os.environ.get('BAIDU_API_KEY'),
                 secret_key=os.environ.get('BAIDU_SECRET_KEY'), **kwargs):
        self._auth_params = dict(grant_type='client_credentials',
                                 client_id=api_key,
                                 client_secret=secret_key)
        self._expire_time = 0
        self._token = ''
        self._tts_params = dict(lan='zh', ctp=1, cuid=MAC, tok='', tex='',
                                spd=kwargs.get('speed', 5),
                                pit=kwargs.get('pit', 5),
                                vol=kwargs.get('volume', 5),
                                per=kwargs.get('person', 0))
        self._asr_params = dict(channel=1, cuid=MAC, token='', lan='zh',
                                format='pcm', rate=16000, speech=b'', len=0)
        pygame.mixer.pre_init(16000, -16, 1, 4096)  # 百度语音合成的音频格式
        pygame.mixer.init()

    def __del__(self):
        pygame.mixer.quit()

    @property
    def token(self):
        """百度语音API访问令牌
        """
        if time.time() > self._expire_time:  # 令牌过期则更新
            auth_response = requests.get(url='https://openapi.baidu.com/oauth/2.0/token',
                                         params=self._auth_params).json()
            self._expire_time = time.time() + auth_response['expires_in'] - 60
            self._token = auth_response['access_token']
        return self._token

    def tts_setup(self, **kwargs):
        """语音合成参数设置
        """
        # 语速，取值0-9，默认为5中语速
        spd = kwargs.get('speed')
        if spd and 0 <= spd <= 9:
            self._tts_params['spd'] = spd
        # 音调，取值0-9，默认为5中语调
        pit = kwargs.get('pit')
        if pit and 0 <= pit <= 9:
            self._tts_params['pit'] = pit
        # 音量，取值0-15，默认为5中音量
        vol = kwargs.get('volume')
        if vol and 0 <= vol <= 15:
            self._tts_params['vol'] = vol
        # 0为普通女声，1为普通男生，3为情感合成-度逍遥，4为情感合成-度丫丫，默认为普通女声
        per = kwargs.get('person')
        if per and per in [0, 1, 3, 4]:
            self._tts_params['per'] = per

    def tts(self, text, save=''):
        """语音合成
        """
        text = str(text)
        while text:
            paragraph, text = text[:512], text[512:]  # 百度语音API语音合成文本长度限制512个字
            self._tts_params.update(tex=paragraph, tok=self.token)
            responce = requests.get(url='http://tsn.baidu.com/text2audio', params=self._tts_params, timeout=3)
            if responce.headers.get('Content-type') == 'audio/mp3':
                pygame.mixer.music.load(io.BytesIO(responce.content))
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(100)
                if save:
                    with open(save, 'wb') as mp3_file:
                        mp3_file.write(responce.content)

    def asr_setup(self, fmt=None, rate=None):
        """语音识别参数设置
        """
        if fmt in ['pcm', 'wav', 'amr']:
            self._asr_params.update(format=fmt)
        if rate in [8000, 16000]:
            self._asr_params.update(rate=rate)

    def asr(self, speech, fmt='wav'):
        """语音识别
        长度上限为60秒
        """
        if isinstance(speech, str) and os.path.isfile(speech):
            with open(speech, 'rb') as sound_file:
                data = sound_file.read()
        elif isinstance(speech, bytes):
            data = speech
        else:
            return 'Error'
        self._asr_params.update(token=self.token,
                                speech=base64.b64encode(data).decode(),
                                len=len(data),
                                format=fmt)
        responce = requests.post(url='http://vop.baidu.com/server_api',
                                 json=self._asr_params)
        result = ''
        if responce.ok:
            result = responce.json().get('result', [''])[0]
        return result


if __name__ == '__main__':
    BaiduYuyin().tts('你好百度')
