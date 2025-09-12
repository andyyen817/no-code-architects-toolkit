#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import glob
import sys

print("=== 測試glob.glob文件順序 ===")

cwd = os.getcwd()
base_dir = 'routes'
if not os.path.isabs(base_dir):
    base_dir = os.path.join(cwd, base_dir)

print(f"當前工作目錄: {cwd}")
print(f"基礎目錄: {base_dir}")

# 使用與app_utils.py相同的方法查找文件
python_files = glob.glob(os.path.join(base_dir, '**', '*.py'), recursive=True)
print(f"\n找到 {len(python_files)} 個Python文件")

print("\n=== 所有文件（glob順序） ===")
for i, file_path in enumerate(python_files, 1):
    rel_path = os.path.relpath(file_path, cwd)
    module_path = os.path.splitext(rel_path)[0].replace(os.path.sep, '.')
    if 'storage' in file_path:
        print(f"{i:3d}: ⭐ {module_path} (STORAGE)")
    else:
        print(f"{i:3d}: {module_path}")

print("\n=== Storage相關文件位置 ===")
storage_files = [(i+1, f) for i, f in enumerate(python_files) if 'storage' in f]
for pos, file_path in storage_files:
    rel_path = os.path.relpath(file_path, cwd)
    module_path = os.path.splitext(rel_path)[0].replace(os.path.sep, '.')
    print(f"位置 {pos:3d}: {module_path}")

# 檢查前25個文件
print("\n=== 前25個文件（實際處理的範圍） ===")
for i, file_path in enumerate(python_files[:25], 1):
    rel_path = os.path.relpath(file_path, cwd)
    module_path = os.path.splitext(rel_path)[0].replace(os.path.sep, '.')
    if 'storage' in file_path:
        print(f"{i:3d}: ⭐ {module_path} (STORAGE)")
    else:
        print(f"{i:3d}: {module_path}")

# 檢查是否有storage文件在前25個中
storage_in_first_25 = [f for f in python_files[:25] if 'storage' in f]
print(f"\n前25個文件中的storage文件: {len(storage_in_first_25)} 個")
for f in storage_in_first_25:
    rel_path = os.path.relpath(f, cwd)
    module_path = os.path.splitext(rel_path)[0].replace(os.path.sep, '.')
    print(f"  - {module_path}")

# 檢查第26個文件之後的storage文件
storage_after_25 = [f for f in python_files[25:] if 'storage' in f]
print(f"\n第26個文件之後的storage文件: {len(storage_after_25)} 個")
for f in storage_after_25:
    rel_path = os.path.relpath(f, cwd)
    module_path = os.path.splitext(rel_path)[0].replace(os.path.sep, '.')
    print(f"  - {module_path}")