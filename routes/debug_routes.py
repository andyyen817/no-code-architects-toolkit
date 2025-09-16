#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, current_app
import logging

debug_routes_bp = Blueprint('debug_routes', __name__)
logger = logging.getLogger(__name__)

@debug_routes_bp.route('/debug/routes', methods=['GET'])
def list_routes():
    """
    列出所有已注册的路由
    """
    try:
        routes = []
        for rule in current_app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'rule': str(rule),
                'blueprint': getattr(rule, 'blueprint', None)
            })
        
        return jsonify({
            'status': 'success',
            'total_routes': len(routes),
            'routes': sorted(routes, key=lambda x: x['rule'])
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing routes: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@debug_routes_bp.route('/debug/blueprints', methods=['GET'])
def list_blueprints():
    """
    列出所有已注册的蓝图
    """
    try:
        blueprints = []
        for name, blueprint in current_app.blueprints.items():
            blueprints.append({
                'name': name,
                'url_prefix': blueprint.url_prefix,
                'static_folder': blueprint.static_folder,
                'template_folder': blueprint.template_folder
            })
        
        return jsonify({
            'status': 'success',
            'total_blueprints': len(blueprints),
            'blueprints': sorted(blueprints, key=lambda x: x['name'])
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing blueprints: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500