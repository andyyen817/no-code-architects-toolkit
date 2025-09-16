#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Whisper依賴檢查腳本
用於驗證Zeabur部署環境中openai-whisper的安裝和配置
"""

import sys
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_whisper_installation():
    """檢查whisper安裝情況"""
    try:
        import whisper
        logger.info("✅ openai-whisper 已成功導入")
        
        # 檢查可用模型
        available_models = whisper.available_models()
        logger.info(f"✅ 可用模型: {available_models}")
        
        # 檢查small模型是否可用
        if 'small' in available_models:
            logger.info("✅ small模型可用")
        else:
            logger.warning("⚠️ small模型不在可用列表中")
            
        return True
    except ImportError as e:
        logger.error(f"❌ openai-whisper 導入失敗: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ whisper檢查時發生錯誤: {e}")
        return False

def check_faster_whisper_installation():
    """檢查faster-whisper安裝情況"""
    try:
        from faster_whisper import WhisperModel
        logger.info("✅ faster-whisper 已成功導入")
        return True
    except ImportError as e:
        logger.error(f"❌ faster-whisper 導入失敗: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ faster-whisper檢查時發生錯誤: {e}")
        return False

def test_whisper_model_loading():
    """測試whisper模型加載"""
    try:
        import whisper
        logger.info("🔄 正在測試openai-whisper small模型加載...")
        
        # 嘗試加載small模型
        model = whisper.load_model("small")
        logger.info("✅ openai-whisper small模型加載成功")
        
        # 檢查模型屬性
        if hasattr(model, 'dims'):
            logger.info(f"✅ 模型維度: {model.dims}")
        
        return True
    except Exception as e:
        logger.error(f"❌ openai-whisper small模型加載失敗: {e}")
        return False

def test_faster_whisper_model_loading():
    """測試faster-whisper模型加載"""
    try:
        from faster_whisper import WhisperModel
        logger.info("🔄 正在測試faster-whisper small模型加載...")
        
        # 嘗試加載small模型
        model = WhisperModel("small", device="cpu", compute_type="int8")
        logger.info("✅ faster-whisper small模型加載成功")
        
        return True
    except Exception as e:
        logger.error(f"❌ faster-whisper small模型加載失敗: {e}")
        return False

def check_environment_variables():
    """檢查環境變量配置"""
    import os
    
    logger.info("🔍 檢查環境變量配置...")
    
    # 檢查關鍵環境變量
    env_vars = {
        'WHISPER_MODEL_SIZE': os.getenv('WHISPER_MODEL_SIZE', 'Not Set'),
        'WHISPER_COMPUTE_TYPE': os.getenv('WHISPER_COMPUTE_TYPE', 'Not Set'),
        'WHISPER_CACHE_DIR': os.getenv('WHISPER_CACHE_DIR', 'Not Set'),
        'WHISPER_MODEL': os.getenv('WHISPER_MODEL', 'Not Set')
    }
    
    for var, value in env_vars.items():
        if value == 'Not Set':
            logger.warning(f"⚠️ 環境變量 {var} 未設置")
        else:
            logger.info(f"✅ {var} = {value}")
    
    # 檢查是否設置為small模型
    if env_vars.get('WHISPER_MODEL_SIZE') == 'small' or env_vars.get('WHISPER_MODEL') == 'small':
        logger.info("✅ 環境變量已正確配置為small模型")
    else:
        logger.warning("⚠️ 環境變量未配置為small模型")

def main():
    """主函數"""
    logger.info("🚀 開始Whisper依賴檢查...")
    logger.info("=" * 50)
    
    # 檢查Python版本
    logger.info(f"🐍 Python版本: {sys.version}")
    
    # 檢查安裝情況
    openai_whisper_ok = check_whisper_installation()
    faster_whisper_ok = check_faster_whisper_installation()
    
    # 檢查環境變量
    check_environment_variables()
    
    # 測試模型加載
    if openai_whisper_ok:
        test_whisper_model_loading()
    
    if faster_whisper_ok:
        test_faster_whisper_model_loading()
    
    logger.info("=" * 50)
    
    # 總結
    if openai_whisper_ok:
        logger.info("🎉 openai-whisper 配置正常，可以使用統一的small模型")
    else:
        logger.error("💥 openai-whisper 配置有問題，需要檢查安裝")
    
    if faster_whisper_ok:
        logger.info("🎉 faster-whisper 也可用作備選方案")
    
    logger.info("✅ 檢查完成")

if __name__ == "__main__":
    main()