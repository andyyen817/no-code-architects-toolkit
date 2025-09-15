#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試Whisper功能
"""

import whisper
import os
import sys

def test_whisper():
    """測試whisper模型加載和基本功能"""
    try:
        print("正在加載Whisper模型...")
        model = whisper.load_model("base")
        print("✓ Whisper模型加載成功")
        
        # 測試模型信息
        print(f"模型類型: {type(model)}")
        print(f"模型設備: {model.device}")
        
        return True
        
    except Exception as e:
        print(f"✗ Whisper測試失敗: {e}")
        return False

if __name__ == "__main__":
    print("開始測試Whisper功能...")
    success = test_whisper()
    
    if success:
        print("\n✓ 所有測試通過！Whisper功能正常")
        sys.exit(0)
    else:
        print("\n✗ 測試失敗")
        sys.exit(1)