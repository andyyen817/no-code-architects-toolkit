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
        
        # 🚨 標準化路徑分隔符 - Windows兼容性修復
        # 保持使用正斜杠，讓safe_join自動處理路徑分隔符
        normalized_file_path = file_path
        
        # 🚨 多層級文件路徑查找策略 - 兼容舊文件
        potential_paths = []
        
        # 1. 標準路徑：./output/nca/{file_type}/{path}
        standard_path = safe_join(nca_storage_dir, normalized_file_path)
        if standard_path:
            potential_paths.append(("標準路徑", standard_path))
        
        # 2. 直接路徑：./output/nca/{file_type}/{filename}
        if os.sep in normalized_file_path:
            filename_only = os.path.basename(normalized_file_path)
            direct_path = safe_join(nca_storage_dir, filename_only)
            if direct_path:
                potential_paths.append(("直接路徑", direct_path))
        
        # 3. 舊版路徑：./output/{file_type}/{path} (修復前的結構)
        legacy_dir = os.path.join(output_dir, file_type)
        legacy_path = safe_join(legacy_dir, normalized_file_path)
        if legacy_path:
            potential_paths.append(("舊版路徑", legacy_path))
        
        # 4. 根目錄路徑：./output/{path}
        root_path = safe_join(output_dir, normalized_file_path)
        if root_path:
            potential_paths.append(("根目錄路徑", root_path))
        
        # 🔍 逐一檢查每個可能的路徑
        found_file_path = None
        found_strategy = None
        
        for strategy, path in potential_paths:
            logger.info(f"🔍 檢查{strategy}: {path}")
            if os.path.exists(path):
                found_file_path = path
                found_strategy = strategy
                logger.info(f"✅ 找到文件 - {strategy}: {path}")
                break
            else:
                logger.info(f"❌ 文件不存在 - {strategy}: {path}")
        
        # 🚨 新增：如果精確匹配失敗，嘗試前綴匹配（處理帶後綴的文件）
        if not found_file_path:
            logger.info("🔍 精確匹配失敗，嘗試前綴匹配...")
            
            # 提取原始文件名（不含擴展名）
            original_filename = os.path.splitext(os.path.basename(normalized_file_path))[0]
            file_extension = os.path.splitext(normalized_file_path)[1]
            
            logger.info(f"🔍 原始文件名: {original_filename}, 擴展名: {file_extension}")
            
            # 在每個可能的目錄中搜索前綴匹配的文件
            search_directories = [
                nca_storage_dir,  # 標準目錄
                os.path.join(output_dir, file_type),  # 舊版目錄
                output_dir  # 根目錄
            ]
            
            for search_dir in search_directories:
                if not os.path.exists(search_dir):
                    continue
                    
                # 檢查目錄及其子目錄
                for root, dirs, files in os.walk(search_dir):
                    for filename in files:
                        # 檢查文件是否以原始文件名開頭且有相同擴展名
                        if (filename.startswith(original_filename) and 
                            filename.endswith(file_extension) and 
                            filename != os.path.basename(normalized_file_path)):
                            
                            candidate_path = os.path.join(root, filename)
                            logger.info(f"🔍 找到前綴匹配文件: {candidate_path}")
                            
                            # 驗證這是一個有效的變體（包含常見後綴）
                            valid_suffixes = ['_trim_', '_cut_', '_process_', '_convert_', '_captioned']
                            if any(suffix in filename for suffix in valid_suffixes):
                                found_file_path = candidate_path
                                found_strategy = f"前綴匹配 ({os.path.relpath(search_dir, output_dir)})"
                                logger.info(f"✅ 前綴匹配成功 - {found_strategy}: {found_file_path}")
                                break
                    
                    if found_file_path:
                        break
                
                if found_file_path:
                    break
        
        if not found_file_path:
            logger.warning(f"🚨 所有路徑都未找到文件: {file_path}")
            
            # 🚨 Debug: 列出目錄內容進行診斷
            try:
                if os.path.exists(nca_storage_dir):
                    logger.info(f"🔍 NCA存儲目錄內容: {os.listdir(nca_storage_dir)}")
                    # 嘗試遞歸列出子目錄
                    for root, dirs, files in os.walk(nca_storage_dir):
                        if files:  # 只顯示有文件的目錄
                            logger.info(f"🔍 {root}: files={files[:5]}{'...' if len(files) > 5 else ''}")
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
        
        # 使用找到的文件路徑
        full_file_path = found_file_path
        
        # 獲取MIME類型
        mime_type, _ = mimetypes.guess_type(full_file_path)
        
        # 🚨 修復：針對音頻文件優化MIME類型設置
        file_ext = os.path.splitext(full_file_path)[1].lower()
        if file_type == 'audio':
            if file_ext == '.m4a':
                mime_type = 'audio/mp4'  # 正確的m4a MIME類型
            elif file_ext == '.mp3':
                mime_type = 'audio/mpeg'
            elif file_ext == '.wav':
                mime_type = 'audio/wav'
            elif file_ext == '.aac':
                mime_type = 'audio/aac'
            elif file_ext == '.ogg':
                mime_type = 'audio/ogg'
            elif file_ext == '.flac':
                mime_type = 'audio/flac'
        
        if not mime_type:
            mime_type = 'application/octet-stream'
        
        # 記錄文件訪問
        logger.info(f"✅ 提供文件訪問: {file_type}/{file_path} (MIME: {mime_type})")
        
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
        
        # 🚨 修復：強制設置正確的Content-Type，確保音頻文件在瀏覽器中播放而不是下載
        if file_type == 'audio':
            response.headers['Content-Type'] = mime_type  # 強制設置正確的MIME類型
            response.headers['Content-Disposition'] = 'inline'
            response.headers['Accept-Ranges'] = 'bytes'  # 支持音頻播放器的範圍請求
        
        return response
        
    except Exception as e:
        logger.error(f"提供文件時發生錯誤 {file_type}/{file_path}: {str(e)}")
        import traceback
        logger.error(f"詳細錯誤堆疊: {traceback.format_exc()}")
        
        # 🚨 修復：正確處理404錯誤，不要轉換為500
        if "404 Not Found" in str(e) or "NotFound" in str(type(e).__name__):
            abort(404)
        else:
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
            "directory_structure": {},
            "migration_status": None
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
        
        # 🚨 添加遷移狀態檢查
        try:
            from services.file_migration import file_migration_service
            migration_health = file_migration_service.get_migration_health_check()
            health_status["migration_status"] = migration_health
            
            if migration_health['legacy_files_found'] > 0:
                health_status["status"] = "needs_migration"
                health_status["message"] = f"NCA文件服務運行正常，但發現 {migration_health['legacy_files_found']} 個舊文件需要遷移"
        except Exception as migration_e:
            health_status["migration_status"] = {"error": str(migration_e)}
        
        status_code = 200 if health_status["status"] in ["healthy", "needs_migration"] else 207
        return jsonify(health_status), status_code
        
    except Exception as e:
        logger.error(f"文件服務健康檢查失敗: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"文件服務錯誤: {str(e)}"
        }), 500

@nca_files_bp.route('/nca/files/migrate', methods=['POST'])
def migrate_legacy_files():
    """遷移舊文件到新的結構"""
    try:
        from services.file_migration import file_migration_service
        
        logger.info("🚀 開始文件遷移任務...")
        migration_results = file_migration_service.migrate_legacy_files()
        
        return jsonify({
            "status": "completed",
            "message": "文件遷移任務完成",
            "results": migration_results
        }), 200
        
    except Exception as e:
        error_msg = f"文件遷移失敗: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return jsonify({
            "status": "error",
            "message": error_msg
        }), 500