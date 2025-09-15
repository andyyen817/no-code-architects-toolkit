#!/usr/bin/env python3
# Test script to verify FFmpeg subtitle functionality

import os
import tempfile
import ffmpeg
from config import LOCAL_STORAGE_PATH

def test_ffmpeg_subtitle():
    """Test FFmpeg subtitle functionality with absolute paths"""
    print("Testing FFmpeg subtitle functionality...")
    
    # Create test ASS file
    test_ass_content = """[Script Info]
Title: Test Subtitle
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2,0,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:01.00,0:00:03.00,Default,,0,0,0,,Hello World
Dialogue: 0,0:00:04.00,0:00:06.00,Default,,0,0,0,,Test Subtitle
"""
    
    # Ensure uploads directory exists
    absolute_storage_path = os.path.abspath(LOCAL_STORAGE_PATH)
    os.makedirs(absolute_storage_path, exist_ok=True)
    print(f"Storage path: {absolute_storage_path}")
    
    # Create test ASS file
    test_ass_path = os.path.join(absolute_storage_path, "test_subtitle.ass")
    with open(test_ass_path, 'w', encoding='utf-8') as f:
        f.write(test_ass_content)
    print(f"Test ASS file created: {test_ass_path}")
    
    # Check if file exists
    if os.path.exists(test_ass_path):
        print(f"✓ ASS file exists and is readable")
        with open(test_ass_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"File size: {len(content)} characters")
    else:
        print(f"✗ ASS file does not exist")
        return False
    
    # Test FFmpeg command
    try:
        # Create a simple test video (black screen)
        test_video_path = os.path.join(absolute_storage_path, "test_video.mp4")
        test_output_path = os.path.join(absolute_storage_path, "test_output.mp4")
        
        print(f"Creating test video: {test_video_path}")
        # Create a 5-second black video
        ffmpeg.input('color=black:size=640x480:duration=5', f='lavfi').output(
            test_video_path,
            vcodec='libx264',
            pix_fmt='yuv420p'
        ).run(overwrite_output=True, quiet=True)
        
        if os.path.exists(test_video_path):
            print(f"✓ Test video created successfully")
        else:
            print(f"✗ Failed to create test video")
            return False
        
        # Test subtitle rendering
        print(f"Testing subtitle rendering...")
        
        # Change to the uploads directory to use relative paths
        original_cwd = os.getcwd()
        try:
            os.chdir(absolute_storage_path)
            print(f"Changed to directory: {absolute_storage_path}")
            
            # Use simple relative filenames
            rel_video = "test_video.mp4"
            rel_ass = "test_subtitle.ass"
            rel_output = "test_output.mp4"
            
            print(f"Using relative paths: video={rel_video}, ass={rel_ass}, output={rel_output}")
            
            # Try subtitles filter with relative path
            ffmpeg.input(rel_video).output(
                rel_output,
                vf=f"subtitles={rel_ass}",
                acodec='copy'
            ).run(overwrite_output=True)
            
        finally:
            # Always restore original working directory
            os.chdir(original_cwd)
            print(f"Restored working directory to: {original_cwd}")
        
        if os.path.exists(test_output_path):
            print(f"✓ Subtitle rendering successful!")
            print(f"Output file: {test_output_path}")
            print(f"Output file size: {os.path.getsize(test_output_path)} bytes")
            return True
        else:
            print(f"✗ Subtitle rendering failed - no output file")
            return False
            
    except Exception as e:
        print(f"✗ FFmpeg error: {str(e)}")
        return False
    
    finally:
        # Cleanup
        for file_path in [test_ass_path, test_video_path, test_output_path]:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"Cleaned up: {file_path}")
                except:
                    pass

if __name__ == "__main__":
    success = test_ffmpeg_subtitle()
    if success:
        print("\n🎉 FFmpeg subtitle test PASSED!")
    else:
        print("\n❌ FFmpeg subtitle test FAILED!")