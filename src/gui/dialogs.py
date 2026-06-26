"""
对话框模块
包含应用程序中使用的各种对话框
"""

import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkFont
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


class FontDialog:
    """字体选择对话框"""
    
    def __init__(self, parent, lang_manager: LanguageManager, current_font: str):
        self.result = None
        self.lang = lang_manager
        self.current_font = current_font
        
        # 创建对话框窗口
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(lang_manager.get_text('dialog_font_title'))
        self.dialog.geometry("500x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 创建界面
        self.create_widgets()
        
        # 加载系统字体（在对话框打开后才加载）
        self.load_system_fonts()
        
        # 等待对话框关闭
        self.dialog.wait_window()
    
    def create_widgets(self):
        """创建对话框控件"""
        lang = self.lang
        
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 当前字体显示
        current_frame = ttk.LabelFrame(main_frame, text=lang.get_text('label_current_font'), padding="5")
        current_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.current_font_var = tk.StringVar(value=self.current_font)
        ttk.Label(current_frame, textvariable=self.current_font_var, font=("", 12)).pack()
        
        # 搜索框
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(search_frame, text=lang.get_text('label_search')).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_changed)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        search_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        # 字体分类选择
        category_frame = ttk.Frame(main_frame)
        category_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(category_frame, text=lang.get_text('label_category')).pack(side=tk.LEFT)
        self.category_var = tk.StringVar(value="all")
        categories = [
            ("all", lang.get_text('category_all')),
            ("chinese", lang.get_text('category_chinese')),
            ("mono", lang.get_text('category_mono')),
            ("other", lang.get_text('category_other'))
        ]
        for value, text in categories:
            ttk.Radiobutton(category_frame, text=text, variable=self.category_var, 
                           value=value, command=self.on_category_changed).pack(side=tk.LEFT, padx=5)
        
        # 字体列表
        list_frame = ttk.LabelFrame(main_frame, text=lang.get_text('label_font_list'), padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建字体列表（使用Listbox）
        self.font_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.font_listbox.yview)
        self.font_listbox.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.font_listbox.pack(fill=tk.BOTH, expand=True)
        
        # 绑定选择事件
        self.font_listbox.bind('<<ListboxSelect>>', self.on_font_selected)
        
        # 预览区域
        preview_frame = ttk.LabelFrame(main_frame, text=lang.get_text('label_preview'), padding="5")
        preview_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.preview_var = tk.StringVar(value="AaBbCcXxYyZz 123 你好世界")
        self.preview_label = ttk.Label(preview_frame, textvariable=self.preview_var, font=(self.current_font, 14))
        self.preview_label.pack()
        
        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text=lang.get_text('label_ok'), command=self.on_ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text=lang.get_text('label_cancel'), command=self.on_cancel).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text=lang.get_text('label_default'), command=self.on_default).pack(side=tk.LEFT, padx=5)
        
        # 存储所有字体和分类
        self.all_fonts = []
        self.chinese_fonts = []
        self.mono_fonts = []
        self.other_fonts = []
    
    def load_system_fonts(self):
        """加载系统字体列表"""
        # 获取所有可用字体
        all_fonts = tkFont.families(self.dialog)
        self.all_fonts = sorted(list(set(all_fonts)))
        
        # 分类字体
        self.chinese_fonts = []
        self.mono_fonts = []
        self.other_fonts = []
        
        chinese_keywords = ['cjk', 'chinese', 'ming', 'song', 'hei', 'kai', 'fang', 
                           'yahei', 'pingfang', 'noto sans sc', 'simsun', 'simhei',
                           'wenquanyi', 'source han', 'adobe']
        
        for font in self.all_fonts:
            font_lower = font.lower()
            
            # 检查是否是中文字体
            is_chinese = any(keyword in font_lower for keyword in chinese_keywords)
            # 检查是否包含中文字符
            if not is_chinese:
                is_chinese = any(ord(c) > 0x4e00 for c in font)
            
            # 检查是否是等宽字体
            is_mono = any(keyword in font_lower for keyword in ['mono', 'courier', 'consolas', 'fixed'])
            
            if is_chinese:
                self.chinese_fonts.append(font)
            elif is_mono:
                self.mono_fonts.append(font)
            else:
                self.other_fonts.append(font)
        
        # 显示字体列表
        self.update_font_list()
        
        # 如果有当前字体，选中它
        if self.current_font in self.all_fonts:
            index = self.all_fonts.index(self.current_font)
            self.font_listbox.selection_set(index)
            self.font_listbox.see(index)
    
    def update_font_list(self):
        """更新字体列表显示"""
        self.font_listbox.delete(0, tk.END)
        
        category = self.category_var.get()
        search_text = self.search_var.get().lower()
        
        if category == "all":
            fonts = self.all_fonts
        elif category == "chinese":
            fonts = self.chinese_fonts
        elif category == "mono":
            fonts = self.mono_fonts
        else:
            fonts = self.other_fonts
        
        # 应用搜索过滤
        if search_text:
            fonts = [f for f in fonts if search_text in f.lower()]
        
        for font in fonts:
            self.font_listbox.insert(tk.END, font)
    
    def on_search_changed(self, *args):
        """搜索文本变化时更新列表"""
        self.update_font_list()
    
    def on_category_changed(self):
        """分类变化时更新列表"""
        self.update_font_list()
    
    def on_font_selected(self, event):
        """字体被选中时更新预览"""
        selection = self.font_listbox.curselection()
        if selection:
            font_name = self.font_listbox.get(selection[0])
            self.preview_label.configure(font=(font_name, 14))
            self.current_font_var.set(font_name)
    
    def on_ok(self):
        """确定按钮处理"""
        selection = self.font_listbox.curselection()
        if selection:
            self.result = self.font_listbox.get(selection[0])
        self.dialog.destroy()
    
    def on_cancel(self):
        """取消按钮处理"""
        self.dialog.destroy()
    
    def on_default(self):
        """恢复默认字体"""
        import platform
        system = platform.system()
        if system == "Windows":
            self.result = "Microsoft YaHei"
        elif system == "Darwin":
            self.result = "PingFang SC"
        else:
            self.result = "Noto Sans CJK SC"
        self.dialog.destroy()