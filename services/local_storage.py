# Local storage provider for testing and development
import os
import shutil
import logging
from datetime import datetime
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class LocalStorageProvider:
    def __init__(self):
        # 創建本地輸出目錄
        self.output_dir = os.path.join(os.getcwd(), 'output')
        self.videos_dir = os.path.join(self.output_dir, 'videos')
        self.audio_dir = os.path.join(self.output_dir, 'audio')
        self.images_dir = os.path.join(self.output_dir, 'images')
        
        # 確保目錄存在
        os.makedirs(self.videos_dir, exist_ok=True)
        os.makedirs(self.audio_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)
        
        logger.info(f"Local storage initialized at: {self.output_dir}")
    
    def save_file(self, source_path: str, category: str = 'videos') -> str:
        """
        保存文件到本地存儲
        Args:
            source_path: 源文件路徑
            category: 文件類別 (videos, audio, images)
        Returns:
            本地文件路徑
        """
        try:
            # 確定目標目錄
            if category == 'videos':
                target_dir = self.videos_dir
            elif category == 'audio':
                target_dir = self.audio_dir
            elif category == 'images':
                target_dir = self.images_dir
            else:
                target_dir = self.output_dir
            
            # 生成時間戳文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_ext = os.path.splitext(source_path)[1]
            filename = f"{category}_{timestamp}{file_ext}"
            target_path = os.path.join(target_dir, filename)
            
            # 複製文件
            shutil.copy2(source_path, target_path)
            
            logger.info(f"File saved locally: {target_path}")
            
            # 返回相對路徑供訪問
            relative_path = os.path.relpath(target_path, os.getcwd())
            return relative_path.replace('\\', '/')  # 確保路徑格式一致
            
        except Exception as e:
            logger.error(f"Error saving file locally: {e}")
            raise
    
    def get_file_url(self, file_path: str, base_url: str = "http://localhost:8080") -> str:
        """
        生成文件訪問URL
        """
        # 確保路徑格式正確
        clean_path = file_path.replace('\\', '/')
        if not clean_path.startswith('/'):
            clean_path = '/' + clean_path
        
        return urljoin(base_url, clean_path)
    
    def list_files(self, category: str = None):
        """
        列出本地存儲的文件
        """
        if category:
            target_dir = getattr(self, f"{category}_dir", self.output_dir)
            dirs_to_scan = [target_dir]
        else:
            dirs_to_scan = [self.videos_dir, self.audio_dir, self.images_dir]
        
        files = []
        for directory in dirs_to_scan:
            if os.path.exists(directory):
                for filename in os.listdir(directory):
                    file_path = os.path.join(directory, filename)
                    if os.path.isfile(file_path):
                        files.append({
                            'filename': filename,
                            'path': os.path.relpath(file_path, os.getcwd()).replace('\\', '/'),
                            'size': os.path.getsize(file_path),
                            'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                        })
        
        return files

# 全局實例
local_storage = LocalStorageProvider()


