"""
对话框模块
包含应用程序中使用的各种对话框
"""

import tkinter as tk
from tkinter import ttk, messagebox
from .language import LanguageManager


class GroupDialog:
    """分组创建对话框"""
    
    def __init__(self, parent, lang_manager: LanguageManager):
        self.result = None
        self.lang = lang_manager
        
        # 创建对话框窗口
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(lang_manager.get_text('dialog_create_group_title'))
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 创建界面
        self.create_widgets()
        
        # 等待对话框关闭
        self.dialog.wait_window()
    
    def create_widgets(self):
        """创建对话框控件"""
        lang = self.lang
        
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 分组ID
        ttk.Label(main_frame, text=lang.get_text('label_group_id')).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.group_id_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.group_id_var, width=30).grid(row=0, column=1, pady=5)
        
        # 分组名称
        ttk.Label(main_frame, text=lang.get_text('label_group_name')).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var, width=30).grid(row=1, column=1, pady=5)
        
        # 描述
        ttk.Label(main_frame, text=lang.get_text('label_description')).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.desc_text = tk.Text(main_frame, height=4, width=30)
        self.desc_text.grid(row=2, column=1, pady=5)
        
        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text=lang.get_text('label_ok'), command=self.on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text=lang.get_text('label_cancel'), command=self.on_cancel).pack(side=tk.LEFT, padx=5)
    
    def on_ok(self):
        """确定按钮处理"""
        lang = self.lang
        
        group_id = self.group_id_var.get().strip()
        name = self.name_var.get().strip()
        description = self.desc_text.get(1.0, tk.END).strip()
        
        if not group_id or not name:
            messagebox.showwarning(lang.get_text('msg_warning'), lang.get_text('msg_group_id_name_empty'))
            return
        
        self.result = (group_id, name, description)
        self.dialog.destroy()
    
    def on_cancel(self):
        """取消按钮处理"""
        self.dialog.destroy()