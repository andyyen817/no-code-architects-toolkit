#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統一輸出文件管理服務
處理所有API功能產出的文件，統一保存到MySQL數據庫並提供外部訪問URL

作者：AI助手
創建日期：2025-01-09
"""

import os
import uuid
import shutil
import logging
from datetime import datetime
from typing import Dict, Optional, Any, Union
from services.database_logger import database_logger

logger = logging.getLogger(__name__)

class OutputFileManager:
    """統一輸出文件管理器"""
    
    def __init__(self):
        self.base_storage_path = os.path.join(os.getcwd(), 'output', 'nca')
        self.base_url = "https://vidsparkback.zeabur.app/nca/files"
        
        # 🚨 初始化時創建基礎目錄結構
        try:
            for file_type in ['audio', 'video', 'image']:
                type_dir = os.path.join(self.base_storage_path, file_type)
                os.makedirs(type_dir, exist_ok=True)
            logger.info(f"✅ 存儲目錄初始化完成: {self.base_storage_path}")
        except Exception as e:
            logger.error(f"❌ 初始化存儲目錄失敗: {e}")
        
    def save_output_file(self, 
                        source_file_path: str, 
                        file_type: str, 
                        operation: str,
                        original_filename: Optional[str] = None,
                        metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        保存輸出文件到統一管理系統
        
        Args:
            source_file_path: 源文件路徑
            file_type: 文件類型 (audio/video/image)
            operation: 操作類型 (cut/trim/thumbnail/concatenate/transcribe等)
            original_filename: 原始文件名（可選）
            metadata: 額外的元數據（可選）
            
        Returns:
            包含文件信息的字典
        """
        try:
            # 檢查源文件是否存在
            if not os.path.exists(source_file_path):
                raise FileNotFoundError(f"源文件不存在: {source_file_path}")
            
            # 生成文件信息
            file_id = str(uuid.uuid4())
            file_extension = os.path.splitext(source_file_path)[1].lower()
            
            if original_filename:
                base_name = os.path.splitext(original_filename)[0]
                safe_filename = f"{base_name}_{operation}_{file_id}{file_extension}"
            else:
                safe_filename = f"{operation}_{file_id}{file_extension}"
            
            # 創建目標目錄（使用os.path.join確保路徑相容性）
            current_date = datetime.now()
            year = current_date.strftime("%Y")
            month = current_date.strftime("%m") 
            target_dir = os.path.join(self.base_storage_path, file_type, year, month)
            os.makedirs(target_dir, exist_ok=True)
            
            # 複製文件到目標位置
            target_file_path = os.path.join(target_dir, safe_filename)
            shutil.copy2(source_file_path, target_file_path)
            
            # 獲取文件信息
            file_size = os.path.getsize(target_file_path)
            # URL中使用正斜線保持Web標準
            file_url = f"{self.base_url}/{file_type}/{year}/{month}/{safe_filename}"
            
            # 準備數據庫記錄
            file_record = {
                'file_id': file_id,
                'original_filename': original_filename or os.path.basename(source_file_path),
                'safe_filename': safe_filename,
                'file_type': file_type,
                'file_size': file_size,
                'file_path': target_file_path,
                'file_url': file_url,
                'upload_time': current_date,
                'operation_type': operation,
                'metadata': metadata
            }
            
            # 保存到數據庫
            self._save_to_database(file_record)
            
            # 清理源文件（如果是臨時文件）
            if source_file_path.startswith('/tmp') or 'temp' in source_file_path.lower():
                try:
                    os.remove(source_file_path)
                    logger.info(f"清理臨時文件: {source_file_path}")
                except Exception as e:
                    logger.warning(f"清理臨時文件失敗: {e}")
            
            logger.info(f"輸出文件保存成功: {operation} -> {file_url}")
            
            return {
                'file_id': file_id,
                'file_url': file_url,
                'filename': safe_filename,
                'file_path': target_file_path,
                'file_size': file_size,
                'file_type': file_type,
                'operation': operation,
                'created_at': current_date.isoformat()
            }
            
        except Exception as e:
            error_msg = f"保存輸出文件失敗: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise Exception(error_msg)
    
    def _save_to_database(self, file_record: Dict[str, Any]):
        """保存文件記錄到數據庫"""
        try:
            # 擴展文件記錄結構以支持操作類型
            enhanced_record = {
                'file_id': file_record['file_id'],
                'original_filename': file_record['original_filename'],
                'safe_filename': file_record['safe_filename'],
                'file_type': file_record['file_type'],
                'file_size': file_record['file_size'],
                'file_path': file_record['file_path'],
                'file_url': file_record['file_url'],
                'upload_time': file_record['upload_time'],
                'operation_type': file_record.get('operation_type', 'unknown'),
                'metadata': file_record.get('metadata', {})
            }
            
            # 使用現有的數據庫記錄器（安全方法調用）
            try:
                method = getattr(database_logger, 'log_output_file', None)
                if method:
                    success = method(enhanced_record)
                else:
                    # 使用備選方法
                    alt_method = getattr(database_logger, 'log_file_upload', None)
                    if alt_method:
                        success = alt_method(enhanced_record)
                    else:
                        # 本地日誌記錄
                        logger.info(f"💾 輸出文件記錄 (本地): {enhanced_record['original_filename']}")
                        success = True
            except Exception as e:
                logger.warning(f"數據庫記錄錯誤: {e}")
                success = True  # 繼續執行，文件已成功保存
            
            if not success:
                logger.warning("數據庫記錄失敗，但文件已保存")
                
        except Exception as e:
            logger.error(f"數據庫記錄錯誤: {e}")
            # 不拋出異常，因為文件已經保存成功
    
    def get_file_info(self, file_id: str) -> Optional[Dict[str, Any]]:
        """根據文件ID獲取文件信息"""
        try:
            try:
                method = getattr(database_logger, 'get_output_file_by_id', None)
                if method:
                    return method(file_id)
                else:
                    logger.warning("數據庫方法不可用，返回None")
                    return None
            except Exception as e:
                logger.error(f"獲取文件信息錯誤: {e}")
                return None
        except Exception as e:
            logger.error(f"獲取文件信息失敗: {e}")
            return None
    
    def list_output_files(self, 
                         file_type: Optional[str] = None, 
                         operation: Optional[str] = None, 
                         limit: int = 50) -> list:
        """列出輸出文件"""
        try:
            try:
                method = getattr(database_logger, 'get_output_files', None)
                if method:
                    return method(file_type, operation, limit)
                else:
                    logger.warning("數據庫方法不可用，返回空列表")
                    return []
            except Exception as e:
                logger.error(f"列出文件錯誤: {e}")
                return []
        except Exception as e:
            logger.error(f"列出文件失敗: {e}")
            return []

# 創建全局實例
output_file_manager = OutputFileManager()