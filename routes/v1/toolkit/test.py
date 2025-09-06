# Copyright (c) 2025 Stephen G. Pope
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.



import os
import logging
from flask import Blueprint, jsonify
from services.authentication import authenticate
try:
    from services.cloud_storage import upload_file
    CLOUD_STORAGE_AVAILABLE = True
except ImportError:
    CLOUD_STORAGE_AVAILABLE = False
try:
    from app_utils import queue_task_wrapper
    QUEUE_AVAILABLE = True
except ImportError:
    QUEUE_AVAILABLE = False
from config import LOCAL_STORAGE_PATH

v1_toolkit_test_bp = Blueprint('v1_toolkit_test', __name__)
logger = logging.getLogger(__name__)

@v1_toolkit_test_bp.route('/v1/toolkit/test', methods=['GET'])
@authenticate
def test_api():
    """Test endpoint with fallback for missing dependencies"""
    logger.info("Testing NCA Toolkit API setup")
    
    try:
        if CLOUD_STORAGE_AVAILABLE:
            # Original cloud storage test
            test_filename = os.path.join(LOCAL_STORAGE_PATH, "success.txt")
            with open(test_filename, 'w') as f:
                f.write("You have successfully installed the NCA Toolkit API, great job!")
            
            upload_url = upload_file(test_filename)
            os.remove(test_filename)
            
            return jsonify({
                "message": "success",
                "response": upload_url,
                "status": "cloud_storage_enabled"
            }), 200
        else:
            # Simple test without cloud storage
            return jsonify({
                "message": "success", 
                "response": "NCA Toolkit API is working!",
                "status": "basic_functionality",
                "version": "1.0.0"
            }), 200
        
    except Exception as e:
        logger.error(f"Error testing API setup - {str(e)}")
        return jsonify({
            "message": "error",
            "response": str(e)
        }), 500