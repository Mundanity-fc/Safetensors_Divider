#!/usr/bin/env python3
"""
可视化大模型 safetensors 内部结构分割与组合工具
主入口文件
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.gui.app import SafetensorsViewerApp

def main():
    app = SafetensorsViewerApp()
    app.run()

if __name__ == "__main__":
    main()