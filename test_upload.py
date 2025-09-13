#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文件上传功能
"""

import requests
import os

def test_file_upload():
    """测试文件上传到本地API"""
    
    # API配置
    base_url = "http://localhost:5000"
    api_key = "vidspark-production-api-key-2024-secure"
    
    # 创建测试文件
    test_file_path = "test_audio.txt"
    if not os.path.exists(test_file_path):
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write("This is a test audio file for upload testing")
    
    # 准备上传
    url = f"{base_url}/v1/files/upload/audio"
    headers = {
        'X-API-Key': api_key
    }
    
    # 上传文件
    with open(test_file_path, 'rb') as f:
        files = {
            'file': (test_file_path, f, 'text/plain')
        }
        data = {
            'file_type': 'audio'
        }
        
        print(f"🚀 开始上传文件: {test_file_path}")
        print(f"📡 API端点: {url}")
        
        try:
            response = requests.post(url, headers=headers, files=files, data=data, timeout=30)
            
            print(f"📊 HTTP状态码: {response.status_code}")
            print(f"📄 响应内容: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 上传成功!")
                print(f"📎 文件URL: {result.get('file_url', 'N/A')}")
                print(f"📏 文件大小: {result.get('file_size', 'N/A')}")
                print(f"🆔 文件ID: {result.get('file_id', 'N/A')}")
                return True
            else:
                print(f"❌ 上传失败: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 请求异常: {str(e)}")
            return False

def test_file_list():
    """测试获取文件列表"""
    
    base_url = "http://localhost:5000"
    api_key = "vidspark-production-api-key-2024-secure"
    
    url = f"{base_url}/v1/files/list"
    headers = {
        'X-API-Key': api_key
    }
    
    print(f"\n📋 获取文件列表")
    print(f"📡 API端点: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"📊 HTTP状态码: {response.status_code}")
        print(f"📄 响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 获取成功!")
            files = result.get('files', [])
            print(f"📁 文件数量: {len(files)}")
            
            for i, file_info in enumerate(files[:5]):  # 只显示前5个
                print(f"  {i+1}. {file_info.get('original_filename', 'N/A')} - {file_info.get('file_type', 'N/A')}")
            
            return True
        else:
            print(f"❌ 获取失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 开始测试文件上传功能")
    print("=" * 50)
    
    # 测试上传
    upload_success = test_file_upload()
    
    # 测试列表
    list_success = test_file_list()
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果:")
    print(f"  文件上传: {'✅ 成功' if upload_success else '❌ 失败'}")
    print(f"  文件列表: {'✅ 成功' if list_success else '❌ 失败'}")