# Simple test route without cloud dependencies
import os
import logging
from flask import Blueprint, jsonify
from services.authentication import authenticate

v1_toolkit_test_simple_bp = Blueprint('v1_toolkit_test_simple', __name__)
logger = logging.getLogger(__name__)

@v1_toolkit_test_simple_bp.route('/v1/toolkit/test', methods=['GET'])
@authenticate
def test_api_simple():
    """Simple test endpoint without cloud storage dependencies"""
    logger.info("Testing NCA Toolkit API setup (simple version)")
    
    try:
        return jsonify({
            "message": "NCA Toolkit API is working!",
            "status": "success",
            "version": "1.0.0",
            "endpoints_available": "Basic functionality ready"
        }), 200
        
    except Exception as e:
        logger.error(f"Error testing API setup - {str(e)}")
        return jsonify({
            "message": f"Error: {str(e)}",
            "status": "error"
        }), 500






