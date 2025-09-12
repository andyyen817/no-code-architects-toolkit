#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
存儲管理模塊
提供存儲相關的API端點和功能
"""

# 導入存儲管理藍圖
from .storage_management import storage_management_bp

__all__ = ['storage_management_bp']