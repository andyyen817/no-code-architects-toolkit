#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件遷移和兼容性服務
處理舊文件路徑結構的遷移和兼容訪問

作者：AI助手
創建日期：2025-01-09
目的：解決Zeabur部署後的文件存儲持久性問題
"""

import os
import shutil
import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class FileMigrationService:
    """文件遷移服務"""
    
    def __init__(self):
        self.base_output_dir = os.path.join(os.getcwd(), 'output')
        self.nca_storage_dir = os.path.join(self.base_output_dir, 'nca')
        self.file_types = ['audio', 'video', 'image']
        
    def migrate_legacy_files(self) -> Dict[str, Any]:
        """
        遷移舊版本文件到新的標準路徑結構
        
        Returns:
            遷移結果統計
        """
        migration_stats = {
            'total_files_found': 0,
            'total_files_migrated': 0,
            'failed_migrations': 0,
            'migration_details': [],
            'errors': []
        }
        
        try:
            logger.info("🚀 開始文件遷移任務...")
            
            # 確保新的目錄結構存在
            self._ensure_directory_structure()
            
            # 搜索需要遷移的文件
            legacy_files = self._find_legacy_files()
            migration_stats['total_files_found'] = len(legacy_files)
            
            logger.info(f"📊 發現 {len(legacy_files)} 個需要遷移的文件")
            
            # 執行遷移
            for legacy_file in legacy_files:
                try:
                    result = self._migrate_single_file(legacy_file)
                    if result['success']:
                        migration_stats['total_files_migrated'] += 1
                    else:
                        migration_stats['failed_migrations'] += 1
                        migration_stats['errors'].append(result['error'])
                    
                    migration_stats['migration_details'].append(result)
                    
                except Exception as e:
                    error_msg = f"遷移文件 {legacy_file['path']} 時發生錯誤: {str(e)}"
                    logger.error(error_msg)
                    migration_stats['failed_migrations'] += 1
                    migration_stats['errors'].append(error_msg)
            
            logger.info(f"✅ 遷移完成：成功 {migration_stats['total_files_migrated']}，失敗 {migration_stats['failed_migrations']}")
            
        except Exception as e:
            error_msg = f"文件遷移任務失敗: {str(e)}"
            logger.error(error_msg)
            migration_stats['errors'].append(error_msg)
        
        return migration_stats
    
    def _ensure_directory_structure(self):
        """確保新的目錄結構存在"""
        for file_type in self.file_types:
            type_dir = os.path.join(self.nca_storage_dir, file_type)
            os.makedirs(type_dir, exist_ok=True)
            logger.info(f"✅ 確保目錄存在: {type_dir}")
    
    def _find_legacy_files(self) -> List[Dict[str, Any]]:
        """查找需要遷移的舊文件"""
        legacy_files = []
        
        # 搜索策略：
        # 1. ./output/{file_type}/ 目錄下的文件
        # 2. ./output/ 根目錄下的媒體文件
        # 3. 其他可能的舊路徑
        
        for file_type in self.file_types:
            # 策略1：查找 ./output/{file_type}/ 下的文件
            legacy_type_dir = os.path.join(self.base_output_dir, file_type)
            if os.path.exists(legacy_type_dir):
                for root, dirs, files in os.walk(legacy_type_dir):
                    for file in files:
                        if self._is_media_file(file, file_type):
                            file_path = os.path.join(root, file)
                            legacy_files.append({
                                'path': file_path,
                                'type': file_type,
                                'filename': file,
                                'strategy': 'legacy_type_directory',
                                'relative_path': os.path.relpath(file_path, legacy_type_dir)
                            })
        
        # 策略2：查找根目錄下的媒體文件
        if os.path.exists(self.base_output_dir):
            for file in os.listdir(self.base_output_dir):
                file_path = os.path.join(self.base_output_dir, file)
                if os.path.isfile(file_path):
                    file_type = self._detect_file_type(file)
                    if file_type:
                        legacy_files.append({
                            'path': file_path,
                            'type': file_type,
                            'filename': file,
                            'strategy': 'root_directory',
                            'relative_path': file
                        })
        
        return legacy_files
    
    def _is_media_file(self, filename: str, file_type: str) -> bool:
        """檢查文件是否為指定類型的媒體文件"""
        extensions = {
            'audio': ['.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a'],
            'video': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']
        }
        
        file_ext = os.path.splitext(filename.lower())[1]
        return file_ext in extensions.get(file_type, [])
    
    def _detect_file_type(self, filename: str) -> str:
        """根據文件擴展名檢測文件類型"""
        for file_type in self.file_types:
            if self._is_media_file(filename, file_type):
                return file_type
        return None
    
    def _migrate_single_file(self, legacy_file: Dict[str, Any]) -> Dict[str, Any]:
        """遷移單個文件"""
        try:
            source_path = legacy_file['path']
            file_type = legacy_file['type']
            filename = legacy_file['filename']
            
            # 生成新的目標路徑（使用當前日期結構）
            current_date = datetime.now()
            year = current_date.strftime("%Y")
            month = current_date.strftime("%m")
            
            target_dir = os.path.join(self.nca_storage_dir, file_type, year, month)
            os.makedirs(target_dir, exist_ok=True)
            
            target_path = os.path.join(target_dir, filename)
            
            # 如果目標文件已存在，生成新名稱
            if os.path.exists(target_path):
                base_name, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(target_path):
                    new_filename = f"{base_name}_migrated_{counter}{ext}"
                    target_path = os.path.join(target_dir, new_filename)
                    counter += 1
                filename = os.path.basename(target_path)
            
            # 執行文件遷移
            shutil.copy2(source_path, target_path)
            
            # 生成新的URL
            new_url = f"https://vidsparkback.zeabur.app/nca/files/{file_type}/{year}/{month}/{filename}"
            
            logger.info(f"✅ 遷移成功: {source_path} -> {target_path}")
            
            return {
                'success': True,
                'source_path': source_path,
                'target_path': target_path,
                'new_url': new_url,
                'strategy': legacy_file['strategy'],
                'file_type': file_type,
                'filename': filename
            }
            
        except Exception as e:
            error_msg = f"遷移文件失敗: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'source_path': legacy_file['path'],
                'error': error_msg,
                'strategy': legacy_file['strategy']
            }
    
    def cleanup_legacy_files(self, migration_results: List[Dict[str, Any]]) -> int:
        """清理已成功遷移的舊文件"""
        cleaned_count = 0
        
        for result in migration_results:
            if result['success']:
                try:
                    source_path = result['source_path']
                    if os.path.exists(source_path):
                        os.remove(source_path)
                        cleaned_count += 1
                        logger.info(f"🗑️ 清理舊文件: {source_path}")
                except Exception as e:
                    logger.error(f"清理舊文件失敗 {source_path}: {str(e)}")
        
        return cleaned_count
    
    def get_migration_health_check(self) -> Dict[str, Any]:
        """獲取遷移狀態健康檢查"""
        health_info = {
            'legacy_files_found': 0,
            'directories_checked': [],
            'nca_structure_ready': True,
            'recommendations': []
        }
        
        # 檢查是否還有舊文件需要遷移
        legacy_files = self._find_legacy_files()
        health_info['legacy_files_found'] = len(legacy_files)
        
        # 檢查目錄結構
        for file_type in self.file_types:
            type_dir = os.path.join(self.nca_storage_dir, file_type)
            health_info['directories_checked'].append({
                'type': file_type,
                'path': type_dir,
                'exists': os.path.exists(type_dir),
                'writable': os.access(type_dir, os.W_OK) if os.path.exists(type_dir) else False
            })
        
        # 生成建議
        if health_info['legacy_files_found'] > 0:
            health_info['recommendations'].append(f"發現 {health_info['legacy_files_found']} 個舊文件需要遷移")
        
        return health_info

# 創建全局實例
file_migration_service = FileMigrationService()