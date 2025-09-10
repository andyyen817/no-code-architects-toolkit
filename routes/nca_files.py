#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NCA文件存儲訪問路由
為測試中心上傳的文件提供外部訪問
"""

from flask import Blueprint, send_file, jsonify, abort
import os
import logging
import mimetypes
from werkzeug.security import safe_join

# 創建NCA文件訪問藍圖
nca_files_bp = Blueprint('nca_files', __name__)
logger = logging.getLogger(__name__)

@nca_files_bp.route('/nca/files/<file_type>/<path:file_path>')
def serve_nca_file(file_type, file_path):
    """
    提供NCA測試中心上傳文件的外部訪問
    
    URL格式: https://domain.com/nca/files/audio/2025/01/filename.mp3
    本地路徑: ./output/nca/audio/2025/01/filename.mp3
    
    Args:
        file_type: 文件類型 (audio/video/image)
        file_path: 文件相對路徑，如 2025/01/filename.mp3
        
    Returns:
        文件內容或404錯誤
    """
    try:
        # 🚨 Debug: 記錄請求詳情
        logger.info(f"🔍 請求文件訪問: {file_type}/{file_path}")
        
        # 驗證文件類型（支援 audio, video, image）
        if file_type not in ['audio', 'video', 'image']:
            logger.warning(f"無效的文件類型: {file_type}")
            abort(404)
        
        # 構建安全的文件路徑
        output_dir = os.path.join(os.getcwd(), 'output')
        nca_storage_dir = os.path.join(output_dir, 'nca', file_type)
        
        # 🚨 Debug: 記錄路徑信息
        logger.info(f"🔍 工作目錄: {os.getcwd()}")
        logger.info(f"🔍 基礎輸出目錄: {output_dir}")
        logger.info(f"🔍 NCA存儲目錄: {nca_storage_dir}")
        logger.info(f"🔍 目標文件路徑: {file_path}")
        
        # 使用safe_join防止路徑遍歷攻擊
        full_file_path = safe_join(nca_storage_dir, file_path)
        
        if not full_file_path:
            logger.warning(f"不安全的文件路徑: {file_path}")
            abort(404)
        
        # 🚨 Debug: 記錄完整路徑和檢查結果
        logger.info(f"🔍 完整文件路徑: {full_file_path}")
        logger.info(f"🔍 文件是否存在: {os.path.exists(full_file_path)}")
        
        # 如果文件不存在，列出目錄內容進行診斷
        if not os.path.exists(full_file_path):
            logger.warning(f"文件不存在: {full_file_path}")
            
            # 🚨 Debug: 列出目錄內容
            try:
                if os.path.exists(nca_storage_dir):
                    logger.info(f"🔍 NCA存儲目錄內容: {os.listdir(nca_storage_dir)}")
                    # 嘗試遞歸列出子目錄
                    for root, dirs, files in os.walk(nca_storage_dir):
                        logger.info(f"🔍 {root}: dirs={dirs}, files={files}")
                else:
                    logger.warning(f"🔍 NCA存儲目錄不存在: {nca_storage_dir}")
                    
                    # 檢查父目錄
                    if os.path.exists(output_dir):
                        logger.info(f"🔍 輸出目錄內容: {os.listdir(output_dir)}")
                    else:
                        logger.warning(f"🔍 輸出目錄不存在: {output_dir}")
                        
                    # 🚨 嘗試創建基礎目錄結構
                    try:
                        os.makedirs(nca_storage_dir, exist_ok=True)
                        logger.info(f"✅ 創建NCA存儲目錄: {nca_storage_dir}")
                    except Exception as create_e:
                        logger.error(f"❌ 創建目錄失敗: {create_e}")
                        
            except Exception as debug_e:
                logger.error(f"🔍 Debug列表錯誤: {debug_e}")
            
            abort(404)
        
        # 獲取MIME類型
        mime_type, _ = mimetypes.guess_type(full_file_path)
        if not mime_type:
            mime_type = 'application/octet-stream'
        
        # 記錄文件訪問
        logger.info(f"✅ 提供文件訪問: {file_type}/{file_path}")
        
        # 返回文件（添加跨域和緩存頭）
        response = send_file(
            full_file_path,
            mimetype=mime_type,
            as_attachment=False,
            download_name=os.path.basename(file_path)
        )
        
        # 🚨 重要：添加跨域頭，允許外部API訪問
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
        response.headers['Cache-Control'] = 'public, max-age=86400'  # 24小時緩存
        
        return response
        
    except Exception as e:
        logger.error(f"提供文件時發生錯誤 {file_type}/{file_path}: {str(e)}")
        import traceback
        logger.error(f"詳細錯誤堆疊: {traceback.format_exc()}")
        abort(500)

@nca_files_bp.route('/nca/files/health')
def files_health_check():
    """文件服務健康檢查"""
    try:
        output_dir = os.path.join(os.getcwd(), 'output', 'nca')
        
        # 🚨 詳細的健康檢查診斷
        health_status = {
            "status": "healthy",
            "message": "NCA文件服務運行正常",
            "storage_path": output_dir,
            "storage_exists": os.path.exists(output_dir),
            "supported_types": ['audio', 'video', 'image'],
            "directory_structure": {}
        }
        
        # 檢查每個文件類型目錄
        for file_type in ['audio', 'video', 'image']:
            type_dir = os.path.join(output_dir, file_type)
            health_status["directory_structure"][file_type] = {
                "path": type_dir,
                "exists": os.path.exists(type_dir),
                "writable": os.access(type_dir, os.W_OK) if os.path.exists(type_dir) else False
            }
            
            # 嘗試創建目錄（如果不存在）
            if not os.path.exists(type_dir):
                try:
                    os.makedirs(type_dir, exist_ok=True)
                    health_status["directory_structure"][file_type]["created"] = True
                    health_status["directory_structure"][file_type]["exists"] = True
                    health_status["directory_structure"][file_type]["writable"] = True
                except Exception as e:
                    health_status["directory_structure"][file_type]["error"] = str(e)
                    health_status["status"] = "warning"
        
        status_code = 200 if health_status["status"] == "healthy" else 207
        return jsonify(health_status), status_code
        
    except Exception as e:
        logger.error(f"文件服務健康檢查失敗: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"文件服務錯誤: {str(e)}"
        }), 500