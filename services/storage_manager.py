#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
存儲管理服務
負責初始化存儲目錄、監控存儲使用情況和維護存儲健康

作者：AI助手
創建日期：2025-01-09
目的：解決Zeabur持久化存儲管理問題
"""

import os
import logging
import shutil
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class StorageManager:
    """
    存儲管理器
    負責存儲目錄的創建、監控和維護
    """
    
    def __init__(self):
        """初始化存儲管理器"""
        # 從環境變量獲取存儲路徑
        self.output_dir = os.environ.get('LOCAL_STORAGE_PATH', '/app/output')
        self.whisper_cache_dir = os.environ.get('WHISPER_CACHE_DIR', '/app/whisper_cache')
        self.voice_clone_dir = os.environ.get('VOICE_CLONE_DIR', '/app/voice_clone')
        self.digital_human_dir = os.environ.get('DIGITAL_HUMAN_DIR', '/app/digital_human')
        self.temp_dir = '/app/temp'
        
        # 定義所有需要創建的目錄
        self.required_directories = [
            # 主要輸出目錄
            self.output_dir,
            os.path.join(self.output_dir, 'nca'),
            os.path.join(self.output_dir, 'nca', 'audio'),
            os.path.join(self.output_dir, 'nca', 'video'),
            os.path.join(self.output_dir, 'nca', 'image'),
            os.path.join(self.output_dir, 'vidspark'),
            os.path.join(self.output_dir, 'vidspark', 'storage'),
            os.path.join(self.output_dir, 'videos'),  # 舊版兼容
            os.path.join(self.output_dir, 'audio'),   # 舊版兼容
            os.path.join(self.output_dir, 'images'),  # 舊版兼容
            os.path.join(self.output_dir, 'subtitles'),
            
            # 專用存儲目錄
            self.whisper_cache_dir,
            self.voice_clone_dir,
            self.digital_human_dir,
            self.temp_dir,
            
            # 按年月組織的目錄（當前年月）
            os.path.join(self.output_dir, 'nca', 'audio', '2025', '01'),
            os.path.join(self.output_dir, 'nca', 'video', '2025', '01'),
            os.path.join(self.output_dir, 'nca', 'image', '2025', '01'),
        ]
        
        # 關鍵存儲路徑（需要持久化的）
        self.critical_paths = [
            self.output_dir,
            self.voice_clone_dir,
            self.digital_human_dir,
            self.whisper_cache_dir
        ]
    
    def initialize_storage(self) -> Dict:
        """
        初始化所有存儲目錄
        
        Returns:
            Dict: 初始化結果
        """
        logger.info("🚀 開始初始化存儲目錄...")
        
        results = {
            "success": True,
            "created_directories": [],
            "existing_directories": [],
            "failed_directories": [],
            "errors": []
        }
        
        for directory in self.required_directories:
            try:
                if os.path.exists(directory):
                    results["existing_directories"].append(directory)
                    logger.debug(f"✅ 目錄已存在: {directory}")
                else:
                    os.makedirs(directory, exist_ok=True)
                    results["created_directories"].append(directory)
                    logger.info(f"📁 創建目錄: {directory}")
                    
                # 設置目錄權限
                os.chmod(directory, 0o755)
                
            except Exception as e:
                error_msg = f"創建目錄失敗 {directory}: {str(e)}"
                logger.error(error_msg)
                results["failed_directories"].append(directory)
                results["errors"].append(error_msg)
                results["success"] = False
        
        logger.info(f"📊 存儲初始化完成: 創建 {len(results['created_directories'])} 個目錄")
        return results
    
    def get_storage_usage(self) -> Dict:
        """
        獲取存儲使用情況
        
        Returns:
            Dict: 存儲使用統計
        """
        usage_stats = {
            "timestamp": datetime.now().isoformat(),
            "paths": {},
            "total_size_bytes": 0,
            "total_size_mb": 0,
            "total_size_gb": 0
        }
        
        for path in self.critical_paths:
            if os.path.exists(path):
                try:
                    total_size = self._calculate_directory_size(path)
                    file_count = self._count_files_in_directory(path)
                    
                    usage_stats["paths"][path] = {
                        "size_bytes": total_size,
                        "size_mb": round(total_size / 1024 / 1024, 2),
                        "size_gb": round(total_size / 1024 / 1024 / 1024, 3),
                        "file_count": file_count,
                        "exists": True,
                        "writable": os.access(path, os.W_OK)
                    }
                    
                    usage_stats["total_size_bytes"] += total_size
                    
                except Exception as e:
                    logger.error(f"計算目錄大小失敗 {path}: {str(e)}")
                    usage_stats["paths"][path] = {
                        "error": str(e),
                        "exists": True,
                        "writable": False
                    }
            else:
                usage_stats["paths"][path] = {
                    "exists": False,
                    "error": "目錄不存在"
                }
        
        usage_stats["total_size_mb"] = round(usage_stats["total_size_bytes"] / 1024 / 1024, 2)
        usage_stats["total_size_gb"] = round(usage_stats["total_size_bytes"] / 1024 / 1024 / 1024, 3)
        
        return usage_stats
    
    def health_check(self) -> Dict:
        """
        存儲健康檢查
        
        Returns:
            Dict: 健康檢查結果
        """
        health_status = {
            "healthy": True,
            "timestamp": datetime.now().isoformat(),
            "checks": {
                "directories_exist": True,
                "directories_writable": True,
                "sufficient_space": True
            },
            "issues": [],
            "recommendations": []
        }
        
        # 檢查關鍵目錄是否存在
        for path in self.critical_paths:
            if not os.path.exists(path):
                health_status["checks"]["directories_exist"] = False
                health_status["issues"].append(f"關鍵目錄不存在: {path}")
                health_status["healthy"] = False
            elif not os.access(path, os.W_OK):
                health_status["checks"]["directories_writable"] = False
                health_status["issues"].append(f"目錄不可寫: {path}")
                health_status["healthy"] = False
        
        # 檢查存儲空間
        try:
            usage = self.get_storage_usage()
            total_gb = usage["total_size_gb"]
            
            # 警告閾值：總使用量超過40GB
            if total_gb > 40:
                health_status["checks"]["sufficient_space"] = False
                health_status["issues"].append(f"存儲使用量過高: {total_gb}GB")
                health_status["recommendations"].append("考慮清理舊文件或增加存儲容量")
                
            # 建議閾值：總使用量超過30GB
            elif total_gb > 30:
                health_status["recommendations"].append(f"存儲使用量較高: {total_gb}GB，建議定期清理")
                
        except Exception as e:
            health_status["issues"].append(f"無法檢查存儲空間: {str(e)}")
            health_status["healthy"] = False
        
        # 生成建議
        if not health_status["issues"]:
            health_status["recommendations"].append("存儲系統運行正常")
        
        return health_status
    
    def cleanup_temp_files(self, max_age_hours: int = 24) -> Dict:
        """
        清理臨時文件
        
        Args:
            max_age_hours: 文件最大保留時間（小時）
            
        Returns:
            Dict: 清理結果
        """
        cleanup_results = {
            "cleaned_files": 0,
            "freed_bytes": 0,
            "freed_mb": 0,
            "errors": []
        }
        
        if not os.path.exists(self.temp_dir):
            return cleanup_results
        
        current_time = datetime.now().timestamp()
        max_age_seconds = max_age_hours * 3600
        
        try:
            for root, dirs, files in os.walk(self.temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        file_age = current_time - os.path.getmtime(file_path)
                        if file_age > max_age_seconds:
                            file_size = os.path.getsize(file_path)
                            os.remove(file_path)
                            cleanup_results["cleaned_files"] += 1
                            cleanup_results["freed_bytes"] += file_size
                            logger.debug(f"清理臨時文件: {file_path}")
                    except Exception as e:
                        error_msg = f"清理文件失敗 {file_path}: {str(e)}"
                        cleanup_results["errors"].append(error_msg)
                        logger.error(error_msg)
        
        except Exception as e:
            error_msg = f"清理臨時目錄失敗: {str(e)}"
            cleanup_results["errors"].append(error_msg)
            logger.error(error_msg)
        
        cleanup_results["freed_mb"] = round(cleanup_results["freed_bytes"] / 1024 / 1024, 2)
        
        logger.info(f"🧹 臨時文件清理完成: 清理 {cleanup_results['cleaned_files']} 個文件，釋放 {cleanup_results['freed_mb']}MB")
        return cleanup_results
    
    def _calculate_directory_size(self, directory: str) -> int:
        """
        計算目錄總大小
        
        Args:
            directory: 目錄路徑
            
        Returns:
            int: 目錄大小（字節）
        """
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(file_path)
                    except (OSError, FileNotFoundError):
                        # 忽略無法訪問的文件
                        pass
        except Exception as e:
            logger.error(f"計算目錄大小時出錯 {directory}: {str(e)}")
        
        return total_size
    
    def _count_files_in_directory(self, directory: str) -> int:
        """
        計算目錄中的文件數量
        
        Args:
            directory: 目錄路徑
            
        Returns:
            int: 文件數量
        """
        file_count = 0
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                file_count += len(filenames)
        except Exception as e:
            logger.error(f"計算文件數量時出錯 {directory}: {str(e)}")
        
        return file_count
    
    def create_year_month_directories(self, year: int = None, month: int = None) -> Dict:
        """
        創建指定年月的目錄結構
        
        Args:
            year: 年份，默認為當前年
            month: 月份，默認為當前月
            
        Returns:
            Dict: 創建結果
        """
        if year is None:
            year = datetime.now().year
        if month is None:
            month = datetime.now().month
        
        year_str = str(year)
        month_str = f"{month:02d}"
        
        directories_to_create = [
            os.path.join(self.output_dir, 'nca', 'audio', year_str, month_str),
            os.path.join(self.output_dir, 'nca', 'video', year_str, month_str),
            os.path.join(self.output_dir, 'nca', 'image', year_str, month_str),
        ]
        
        results = {
            "created": [],
            "existing": [],
            "failed": []
        }
        
        for directory in directories_to_create:
            try:
                if os.path.exists(directory):
                    results["existing"].append(directory)
                else:
                    os.makedirs(directory, exist_ok=True)
                    results["created"].append(directory)
                    logger.info(f"📅 創建年月目錄: {directory}")
            except Exception as e:
                logger.error(f"創建年月目錄失敗 {directory}: {str(e)}")
                results["failed"].append(directory)
        
        return results

# 全局存儲管理器實例
storage_manager = StorageManager()

# 應用啟動時自動初始化存儲
def initialize_storage_on_startup():
    """
    應用啟動時初始化存儲
    """
    try:
        logger.info("🚀 應用啟動 - 初始化存儲系統...")
        result = storage_manager.initialize_storage()
        
        if result["success"]:
            logger.info("✅ 存儲系統初始化成功")
        else:
            logger.error(f"❌ 存儲系統初始化失敗: {result['errors']}")
        
        # 創建當前年月目錄
        storage_manager.create_year_month_directories()
        
        return result
        
    except Exception as e:
        logger.error(f"存儲初始化異常: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}