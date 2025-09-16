#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (c) 2024 by No-Code Architects
All rights reserved.
"""

from flask import Blueprint, jsonify
import sys
import os
import traceback
import importlib.util

# Create blueprint
v1_check_routes_bp = Blueprint('v1_check_routes', __name__)

@v1_check_routes_bp.route('/check-routes', methods=['GET'])
def check_routes():
    """Check import status of all route files"""
    result = {
        "status": "checking",
        "files_checked": 0,
        "files_with_errors": 0,
        "errors": []
    }
    
    # List of files to check for import errors
    files_to_check = [
        "routes/transcribe_media.py",
        "routes/v1/image/screenshot_webpage.py", 
        "routes/v1/media/download.py",
        "routes/v1/s3/upload.py"
    ]
    
    for file_path in files_to_check:
        result["files_checked"] += 1
        
        try:
            # Try to import the module
            spec = importlib.util.spec_from_file_location("temp_module", file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
        except ImportError as e:
            result["files_with_errors"] += 1
            result["errors"].append({
                "file": file_path,
                "error_type": "ImportError",
                "error_message": str(e),
                "traceback": traceback.format_exc()
            })
        except Exception as e:
            result["files_with_errors"] += 1
            result["errors"].append({
                "file": file_path,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": traceback.format_exc()
            })
    
    # Set overall status
    if result["files_with_errors"] == 0:
        result["status"] = "all_good"
    else:
        result["status"] = "errors_found"
    
    return jsonify(result)