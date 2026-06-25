#!/usr/bin/env python3
"""
快速启动脚本
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """主函数"""
    print("=" * 50)
    print("Safetensors 可视化分割与组合工具")
    print("=" * 50)
    print()
    
    try:
        from src.gui.app import SafetensorsViewerApp
        
        print("正在启动应用程序...")
        print("如果中文无法显示，请参考README.md中的故障排除部分")
        print()
        
        app = SafetensorsViewerApp()
        
        # 检查是否有命令行参数
        if len(sys.argv) > 1:
            file_path = sys.argv[1]
            if os.path.exists(file_path):
                print(f"加载文件: {file_path}")
                app.load_file(file_path)
            else:
                print(f"文件不存在: {file_path}")
        
        app.run()
        
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保已安装所有依赖: pip install -r requirements.txt")
    except Exception as e:
        print(f"启动错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()