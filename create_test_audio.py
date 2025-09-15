#!/usr/bin/env python3
import wave
import numpy as np

# 創建3秒的440Hz正弦波測試音頻
sample_rate = 44100
duration = 3  # 秒
frequency = 440  # Hz

# 生成音頻數據
t = np.linspace(0, duration, int(sample_rate * duration), False)
audio_data = np.sin(2 * np.pi * frequency * t)

# 轉換為16位整數
audio_data = (audio_data * 32767).astype(np.int16)

# 保存為WAV文件
with wave.open('test_tone.wav', 'w') as wav_file:
    wav_file.setnchannels(1)  # 單聲道
    wav_file.setsampwidth(2)  # 16位
    wav_file.setframerate(sample_rate)
    wav_file.writeframes(audio_data.tobytes())

print("測試音頻文件 test_tone.wav 已創建")