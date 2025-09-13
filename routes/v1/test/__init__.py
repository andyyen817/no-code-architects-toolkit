# Test module for FFmpeg and audio processing functionality

# 導入測試藍圖
from .ffmpeg_test import ffmpeg_test_bp

# 導出藍圖供動態發現使用
__all__ = ['ffmpeg_test_bp']