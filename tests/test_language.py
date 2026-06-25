#!/usr/bin/env python3
"""
测试语言切换功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.gui.language import LanguageManager

def test_language_manager():
    """测试语言管理器"""
    print("测试语言管理器...")
    
    # 创建语言管理器
    lang = LanguageManager()
    
    # 默认语言应该是英文
    print(f"默认语言: {lang.language} ({lang.get_language_name()})")
    assert lang.language == 'en', "默认语言应该是英文"
    
    # 测试获取文本
    title = lang.get_text('window_title')
    print(f"窗口标题: {title}")
    assert title == 'Safetensors Visualization Split & Combine Tool', "英文标题不正确"
    
    # 测试切换到中文
    lang.language = 'zh'
    print(f"切换后语言: {lang.language} ({lang.get_language_name()})")
    assert lang.language == 'zh', "语言应该是中文"
    
    title = lang.get_text('window_title')
    print(f"中文标题: {title}")
    assert title == 'Safetensors 可视化分割与组合工具', "中文标题不正确"
    
    # 测试带回调的文本
    msg = lang.get_text('status_file_loaded', filename='test.json')
    print(f"带参数的文本: {msg}")
    assert 'test.json' in msg, "参数替换失败"
    
    # 测试切换回英文
    lang.language = 'en'
    title = lang.get_text('window_title')
    print(f"切换回英文后: {title}")
    assert title == 'Safetensors Visualization Split & Combine Tool', "切换回英文失败"
    
    # 测试回调函数
    callback_called = False
    def on_lang_change(new_lang):
        nonlocal callback_called
        callback_called = True
        print(f"回调函数被调用，新语言: {new_lang}")
    
    lang.register_callback(on_lang_change)
    lang.language = 'zh'
    assert callback_called, "回调函数应该被调用"
    
    print("所有测试通过!")

if __name__ == "__main__":
    test_language_manager()