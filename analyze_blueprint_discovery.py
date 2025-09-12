#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import time
import os

print("=== 分析藍圖發現過程 ===")

# 運行Flask應用並捕獲日誌
env = os.environ.copy()
env['API_KEY'] = 'production-api-key-2024'

proc = subprocess.Popen(
    ['python', 'app.py'], 
    stdout=subprocess.PIPE, 
    stderr=subprocess.STDOUT, 
    text=True, 
    bufsize=1, 
    universal_newlines=True,
    env=env
)

# 等待8秒讓應用啟動
time.sleep(8)
proc.terminate()

# 讀取輸出
output = proc.stdout.read()
lines = output.split('\n')

print("=== 查找最後處理的模塊 ===")
last_attempt = ''
last_register = ''
last_error = ''

for line in lines:
    if 'Attempting to import module:' in line:
        last_attempt = line
    if 'Registering:' in line:
        last_register = line
    if 'Error importing module' in line:
        last_error = line

print(f"最後嘗試導入: {last_attempt}")
print(f"最後成功註冊: {last_register}")
print(f"最後導入錯誤: {last_error}")

print("\n=== 所有導入嘗試 ===")
attempts = [line for line in lines if 'Attempting to import module:' in line]
for i, attempt in enumerate(attempts, 1):
    print(f"{i:2d}: {attempt}")

print("\n=== 所有註冊成功 ===")
registrations = [line for line in lines if 'Registering:' in line]
for i, reg in enumerate(registrations, 1):
    print(f"{i:2d}: {reg}")

print("\n=== 所有導入錯誤 ===")
errors = [line for line in lines if 'Error importing module' in line]
for i, error in enumerate(errors, 1):
    print(f"{i:2d}: {error}")

print(f"\n=== 統計 ===")
print(f"總導入嘗試: {len(attempts)}")
print(f"成功註冊: {len(registrations)}")
print(f"導入錯誤: {len(errors)}")

# 檢查是否有storage相關的處理
storage_attempts = [line for line in attempts if 'storage' in line.lower()]
storage_registrations = [line for line in registrations if 'storage' in line.lower()]
storage_errors = [line for line in errors if 'storage' in line.lower()]

print(f"\n=== Storage相關統計 ===")
print(f"Storage導入嘗試: {len(storage_attempts)}")
print(f"Storage成功註冊: {len(storage_registrations)}")
print(f"Storage導入錯誤: {len(storage_errors)}")

if storage_attempts:
    print("\nStorage導入嘗試:")
    for attempt in storage_attempts:
        print(f"  {attempt}")

if storage_registrations:
    print("\nStorage成功註冊:")
    for reg in storage_registrations:
        print(f"  {reg}")

if storage_errors:
    print("\nStorage導入錯誤:")
    for error in storage_errors:
        print(f"  {error}")