#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zeabur MySQL 持久化存儲管理器 v2.0
簡化的文件存儲管理系統，統一路由結構和錯誤處理
"""

import os
import json
import uuid
import hashlib
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from flask import Flask, request, jsonify, send_file, abort, Blueprint
import logging

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 創建存儲藍圖
storage_bp = Blueprint('storage', __name__, url_prefix='/api/v1/storage')

class StorageManager:
    """統一的文件存儲管理器"""
    
    def __init__(self):
        from database_manager import get_database_manager
        self.db_manager = get_database_manager()
        self.storage_config = self._load_storage_config()
        self._ensure_directories()
        
    def _load_storage_config(self) -> Dict[str, Any]:
        """加載存儲配置"""
        config = {
            'upload_folder': os.getenv('STORAGE_UPLOAD_FOLDER', './uploads'),
            'max_file_size': int(os.getenv('STORAGE_MAX_FILE_SIZE', '100')) * 1024 * 1024,  # MB to bytes
            'allowed_extensions': os.getenv('STORAGE_ALLOWED_EXTENSIONS', 
                'txt,pdf,png,jpg,jpeg,gif,mp4,mp3,wav,doc,docx,xls,xlsx,ppt,pptx').split(','),
            'cleanup_days': int(os.getenv('STORAGE_CLEANUP_DAYS', '30'))
        }
        
        logger.info(f"存儲配置加載成功: {config['upload_folder']}")
        return config
    
    def _ensure_directories(self):
        """確保存儲目錄存在"""
        upload_path = Path(self.storage_config['upload_folder'])
        upload_path.mkdir(parents=True, exist_ok=True)
        
        # 創建按年月分組的子目錄
        current_date = datetime.now()
        year_month_path = upload_path / f"{current_date.year}" / f"{current_date.month:02d}"
        year_month_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"存儲目錄確認: {upload_path}")
    
    def _is_allowed_file(self, filename: str) -> bool:
        """檢查文件類型是否允許"""
        if '.' not in filename:
            return False
        extension = filename.rsplit('.', 1)[1].lower()
        return extension in self.storage_config['allowed_extensions']
    
    def _generate_file_id(self) -> str:
        """生成唯一文件ID"""
        return str(uuid.uuid4())
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """計算文件哈希值"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"計算文件哈希失敗: {e}")
            return ""
    
    def _get_file_storage_path(self, filename: str) -> str:
        """獲取文件存儲路徑"""
        current_date = datetime.now()
        year_month_dir = f"{current_date.year}/{current_date.month:02d}"
        
        storage_path = Path(self.storage_config['upload_folder']) / year_month_dir
        storage_path.mkdir(parents=True, exist_ok=True)
        
        return str(storage_path / filename)
    
    def upload_file(self, file: FileStorage, user_id: Optional[str] = None, 
                   metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """上傳文件"""
        try:
            # 驗證文件
            if not file or not file.filename:
                return {'success': False, 'error': '沒有選擇文件'}
            
            if not self._is_allowed_file(file.filename):
                return {'success': False, 'error': '不支持的文件類型'}
            
            # 檢查文件大小
            file.seek(0, 2)  # 移動到文件末尾
            file_size = file.tell()
            file.seek(0)  # 重置到開始
            
            if file_size > self.storage_config['max_file_size']:
                return {'success': False, 'error': '文件大小超過限制'}
            
            # 生成安全文件名
            original_filename = file.filename
            secure_name = secure_filename(original_filename)
            file_id = self._generate_file_id()
            
            # 添加文件ID前綴避免重名
            final_filename = f"{file_id}_{secure_name}"
            file_path = self._get_file_storage_path(final_filename)
            
            # 保存文件
            file.save(file_path)
            
            # 計算文件哈希
            file_hash = self._calculate_file_hash(file_path)
            
            # 獲取MIME類型
            mime_type, _ = mimetypes.guess_type(original_filename)
            
            # 保存到數據庫
            insert_query = """
            INSERT INTO files (id, filename, original_filename, file_path, 
                             file_size, file_hash, mime_type, user_id, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            metadata_json = json.dumps(metadata) if metadata else None
            
            self.db_manager.execute_update(
                insert_query,
                (file_id, final_filename, original_filename, file_path,
                 file_size, file_hash, mime_type, user_id, metadata_json)
            )
            
            logger.info(f"文件上傳成功: {file_id} - {original_filename}")
            
            return {
                'success': True,
                'file_id': file_id,
                'filename': final_filename,
                'original_filename': original_filename,
                'file_size': file_size,
                'mime_type': mime_type,
                'upload_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"文件上傳失敗: {e}")
            return {'success': False, 'error': f'上傳失敗: {str(e)}'}
    
    def get_file_info(self, file_id: str) -> Optional[Dict[str, Any]]:
        """獲取文件信息"""
        try:
            query = "SELECT * FROM files WHERE id = %s"
            results = self.db_manager.execute_query(query, (file_id,))
            
            if not results:
                return None
                
            file_info = results[0]
            
            # 解析metadata
            if file_info['metadata']:
                try:
                    file_info['metadata'] = json.loads(file_info['metadata'])
                except:
                    file_info['metadata'] = {}
            
            return file_info
            
        except Exception as e:
            logger.error(f"獲取文件信息失敗: {e}")
            return None
    
    def download_file(self, file_id: str) -> Optional[Tuple[str, str]]:
        """下載文件"""
        try:
            file_info = self.get_file_info(file_id)
            if not file_info:
                return None
                
            file_path = file_info['file_path']
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {file_path}")
                return None
                
            return file_path, file_info['original_filename']
            
        except Exception as e:
            logger.error(f"下載文件失敗: {e}")
            return None
    
    def delete_file(self, file_id: str) -> bool:
        """刪除文件"""
        try:
            file_info = self.get_file_info(file_id)
            if not file_info:
                return False
                
            # 刪除物理文件
            file_path = file_info['file_path']
            if os.path.exists(file_path):
                os.remove(file_path)
                
            # 從數據庫刪除記錄
            delete_query = "DELETE FROM files WHERE id = %s"
            affected_rows = self.db_manager.execute_update(delete_query, (file_id,))
            
            if affected_rows > 0:
                logger.info(f"文件刪除成功: {file_id}")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"刪除文件失敗: {e}")
            return False
    
    def list_files(self, user_id: Optional[str] = None, limit: int = 100, 
                  offset: int = 0) -> List[Dict[str, Any]]:
        """列出文件"""
        try:
            if user_id:
                query = """
                SELECT * FROM files WHERE user_id = %s 
                ORDER BY created_at DESC LIMIT %s OFFSET %s
                """
                params = (user_id, limit, offset)
            else:
                query = """
                SELECT * FROM files 
                ORDER BY created_at DESC LIMIT %s OFFSET %s
                """
                params = (limit, offset)
                
            results = self.db_manager.execute_query(query, params)
            
            # 處理metadata
            for file_info in results:
                if file_info['metadata']:
                    try:
                        file_info['metadata'] = json.loads(file_info['metadata'])
                    except:
                        file_info['metadata'] = {}
                        
            return results
            
        except Exception as e:
            logger.error(f"列出文件失敗: {e}")
            return []
    
    def cleanup_old_files(self, days: Optional[int] = None) -> int:
        """清理舊文件"""
        try:
            cleanup_days = days or self.storage_config['cleanup_days']
            
            # 查找舊文件
            query = """
            SELECT id, file_path FROM files 
            WHERE created_at < DATE_SUB(NOW(), INTERVAL %s DAY)
            """
            
            old_files = self.db_manager.execute_query(query, (cleanup_days,))
            
            deleted_count = 0
            for file_info in old_files:
                if self.delete_file(file_info['id']):
                    deleted_count += 1
                    
            logger.info(f"清理完成，刪除了 {deleted_count} 個舊文件")
            return deleted_count
            
        except Exception as e:
            logger.error(f"清理舊文件失敗: {e}")
            return 0

# 全局存儲管理器實例
_storage_manager = None

def get_storage_manager() -> StorageManager:
    """獲取全局存儲管理器實例"""
    global _storage_manager
    if _storage_manager is None:
        _storage_manager = StorageManager()
    return _storage_manager

# ===== 路由定義 =====

@storage_bp.route('/upload', methods=['POST'])
def upload_file():
    """文件上傳端點"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '沒有文件'}), 400
            
        file = request.files['file']
        user_id = request.form.get('user_id')
        
        # 解析metadata
        metadata = {}
        if 'metadata' in request.form:
            try:
                metadata = json.loads(request.form['metadata'])
            except:
                pass
                
        storage_manager = get_storage_manager()
        result = storage_manager.upload_file(file, user_id, metadata)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"上傳端點錯誤: {e}")
        return jsonify({'success': False, 'error': '服務器內部錯誤'}), 500

@storage_bp.route('/download/<file_id>', methods=['GET'])
def download_file(file_id: str):
    """文件下載端點"""
    try:
        storage_manager = get_storage_manager()
        result = storage_manager.download_file(file_id)
        
        if result:
            file_path, original_filename = result
            return send_file(file_path, as_attachment=True, 
                           download_name=original_filename)
        else:
            return jsonify({'error': '文件不存在'}), 404
            
    except Exception as e:
        logger.error(f"下載端點錯誤: {e}")
        return jsonify({'error': '服務器內部錯誤'}), 500

@storage_bp.route('/info/<file_id>', methods=['GET'])
def get_file_info(file_id: str):
    """獲取文件信息端點"""
    try:
        storage_manager = get_storage_manager()
        file_info = storage_manager.get_file_info(file_id)
        
        if file_info:
            # 移除敏感信息
            safe_info = {
                'id': file_info['id'],
                'filename': file_info['filename'],
                'original_filename': file_info['original_filename'],
                'file_size': file_info['file_size'],
                'mime_type': file_info['mime_type'],
                'created_at': file_info['created_at'].isoformat() if file_info['created_at'] else None,
                'metadata': file_info.get('metadata', {})
            }
            return jsonify(safe_info), 200
        else:
            return jsonify({'error': '文件不存在'}), 404
            
    except Exception as e:
        logger.error(f"文件信息端點錯誤: {e}")
        return jsonify({'error': '服務器內部錯誤'}), 500

@storage_bp.route('/delete/<file_id>', methods=['DELETE'])
def delete_file(file_id: str):
    """刪除文件端點"""
    try:
        storage_manager = get_storage_manager()
        success = storage_manager.delete_file(file_id)
        
        if success:
            return jsonify({'success': True, 'message': '文件刪除成功'}), 200
        else:
            return jsonify({'success': False, 'error': '文件不存在或刪除失敗'}), 404
            
    except Exception as e:
        logger.error(f"刪除端點錯誤: {e}")
        return jsonify({'success': False, 'error': '服務器內部錯誤'}), 500

@storage_bp.route('/list', methods=['GET'])
def list_files():
    """列出文件端點"""
    try:
        user_id = request.args.get('user_id')
        limit = min(int(request.args.get('limit', 100)), 1000)  # 最大1000
        offset = int(request.args.get('offset', 0))
        
        storage_manager = get_storage_manager()
        files = storage_manager.list_files(user_id, limit, offset)
        
        # 格式化返回數據
        formatted_files = []
        for file_info in files:
            formatted_files.append({
                'id': file_info['id'],
                'filename': file_info['filename'],
                'original_filename': file_info['original_filename'],
                'file_size': file_info['file_size'],
                'mime_type': file_info['mime_type'],
                'created_at': file_info['created_at'].isoformat() if file_info['created_at'] else None,
                'metadata': file_info.get('metadata', {})
            })
            
        return jsonify({
            'success': True,
            'files': formatted_files,
            'count': len(formatted_files),
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        logger.error(f"列表端點錯誤: {e}")
        return jsonify({'success': False, 'error': '服務器內部錯誤'}), 500

@storage_bp.route('/cleanup', methods=['POST'])
def cleanup_files():
    """清理舊文件端點"""
    try:
        days = request.json.get('days') if request.json else None
        
        storage_manager = get_storage_manager()
        deleted_count = storage_manager.cleanup_old_files(days)
        
        return jsonify({
            'success': True,
            'deleted_count': deleted_count,
            'message': f'清理完成，刪除了 {deleted_count} 個文件'
        }), 200
        
    except Exception as e:
        logger.error(f"清理端點錯誤: {e}")
        return jsonify({'success': False, 'error': '服務器內部錯誤'}), 500

@storage_bp.route('/health', methods=['GET'])
def health_check():
    """存儲系統健康檢查"""
    try:
        storage_manager = get_storage_manager()
        db_health = storage_manager.db_manager.health_check()
        
        # 檢查存儲目錄
        upload_path = Path(storage_manager.storage_config['upload_folder'])
        storage_accessible = upload_path.exists() and upload_path.is_dir()
        
        return jsonify({
            'status': 'healthy' if db_health['status'] == 'healthy' and storage_accessible else 'unhealthy',
            'database': db_health,
            'storage': {
                'accessible': storage_accessible,
                'upload_folder': str(upload_path),
                'config': storage_manager.storage_config
            },
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"健康檢查錯誤: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

def register_storage_routes(app: Flask):
    """註冊存儲路由到Flask應用"""
    app.register_blueprint(storage_bp)
    logger.info("存儲路由註冊成功")

if __name__ == '__main__':
    # 測試存儲管理器
    storage_manager = get_storage_manager()
    print(f"✅ 存儲管理器初始化成功")
    print(f"配置: {storage_manager.storage_config}")
    
    # 測試數據庫連接
    health = storage_manager.db_manager.health_check()
    print(f"數據庫健康檢查: {health}")