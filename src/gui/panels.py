"""
面板模块
包含左右侧面板的创建和管理
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Callable, Optional

from ..core.parser import TensorInfo
from ..core.tree_builder import TreeNode
from .language import LanguageManager


class LeftPanel:
    """左侧面板（Tensor结构树）"""
    
    def __init__(self, parent: ttk.Frame, lang_manager: LanguageManager):
        self.lang = lang_manager
        self.frame = ttk.LabelFrame(parent, text=lang_manager.get_text('tree_panel_title'))
        
        # 树状图显示
        self.tree_frame = ttk.Frame(self.frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建树状图控件
        self.tree_view = ttk.Treeview(self.tree_frame)
        self.tree_view.pack(fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        tree_scroll = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.tree_view.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_view.configure(yscrollcommand=tree_scroll.set)
        
        # 信息显示区域
        self.info_frame = ttk.LabelFrame(self.frame, text=lang_manager.get_text('info_panel_title'))
        self.info_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.info_text = tk.Text(self.info_frame, height=6, state=tk.DISABLED)
        self.info_text.pack(fill=tk.X, padx=5, pady=5)
    
    def pack(self, **kwargs):
        """打包面板"""
        self.frame.pack(**kwargs)
    
    def update_tree(self, tree_root: Optional[TreeNode], format_size_func: Callable):
        """更新树状图显示"""
        # 清空现有项目
        for item in self.tree_view.get_children():
            self.tree_view.delete(item)
        
        if not tree_root:
            return
        
        # 递归添加节点
        self._add_tree_nodes('', tree_root, format_size_func)
    
    def _add_tree_nodes(self, parent_id: str, node: TreeNode, format_size_func: Callable):
        """递归添加树节点"""
        if node.name == 'root':
            # 根节点，直接添加子节点
            for child_name, child_node in node.children.items():
                self._add_tree_nodes(parent_id, child_node, format_size_func)
        else:
            # 计算显示文本
            display_text = f"{node.name} ({node.tensor_count} tensors, {format_size_func(node.total_size)})"
            
            # 添加节点
            node_id = self.tree_view.insert(
                parent_id, 'end', 
                text=display_text,
                values=(node.full_path, node.tensor_count, format_size_func(node.total_size))
            )
            
            # 递归添加子节点
            for child_name, child_node in node.children.items():
                self._add_tree_nodes(node_id, child_node, format_size_func)
    
    def update_info(self, info_lines: List[str]):
        """更新信息显示"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, "\n".join(info_lines))
        self.info_text.config(state=tk.DISABLED)
    
    def get_selection(self):
        """获取选中的节点"""
        return self.tree_view.selection()
    
    def get_item(self, item_id):
        """获取节点信息"""
        return self.tree_view.item(item_id)
    
    def bind_select(self, callback: Callable):
        """绑定选择事件"""
        self.tree_view.bind('<<TreeviewSelect>>', callback)
    
    def update_title(self, lang_manager: LanguageManager):
        """更新面板标题"""
        self.frame.config(text=lang_manager.get_text('tree_panel_title'))
        self.info_frame.config(text=lang_manager.get_text('info_panel_title'))


class RightPanel:
    """右侧面板（分组管理）"""
    
    def __init__(self, parent: ttk.Frame, lang_manager: LanguageManager):
        self.lang = lang_manager
        self.frame = ttk.LabelFrame(parent, text=lang_manager.get_text('group_panel_title'))
        
        # 分组树形视图
        self.group_list_frame = ttk.LabelFrame(self.frame, text=lang_manager.get_text('group_list_title'))
        self.group_list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.group_tree = ttk.Treeview(self.group_list_frame)
        self.group_tree.pack(fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        group_scroll = ttk.Scrollbar(self.group_list_frame, orient=tk.VERTICAL, command=self.group_tree.yview)
        group_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.group_tree.configure(yscrollcommand=group_scroll.set)
        
        # 分组操作按钮
        self.ops_frame = ttk.Frame(self.frame)
        self.ops_frame.pack(fill=tk.X, pady=(5, 0))
        
        # 分组详情显示
        self.detail_frame = ttk.LabelFrame(self.frame, text=lang_manager.get_text('group_detail_title'))
        self.detail_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.detail_text = tk.Text(self.detail_frame, height=6, state=tk.DISABLED)
        self.detail_text.pack(fill=tk.X, padx=5, pady=5)
    
    def pack(self, **kwargs):
        """打包面板"""
        self.frame.pack(**kwargs)
    
    def add_button(self, text: str, command: Callable) -> ttk.Button:
        """添加操作按钮"""
        btn = ttk.Button(self.ops_frame, text=text, command=command)
        btn.pack(side=tk.LEFT, padx=2)
        return btn
    
    def update_detail(self, info_lines: List[str]):
        """更新详情显示"""
        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.delete(1.0, tk.END)
        self.detail_text.insert(1.0, "\n".join(info_lines))
        self.detail_text.config(state=tk.DISABLED)
    
    def get_selection(self):
        """获取选中的节点"""
        return self.group_tree.selection()
    
    def get_item(self, item_id):
        """获取节点信息"""
        return self.group_tree.item(item_id)
    
    def get_children(self, parent_id=''):
        """获取子节点"""
        return self.group_tree.get_children(parent_id)
    
    def insert(self, parent, index, **kwargs):
        """插入节点"""
        return self.group_tree.insert(parent, index, **kwargs)
    
    def delete(self, *items):
        """删除节点"""
        for item in items:
            self.group_tree.delete(item)
    
    def clear(self):
        """清空所有节点"""
        for item in self.group_tree.get_children():
            self.group_tree.delete(item)
    
    def parent(self, item_id):
        """获取父节点"""
        return self.group_tree.parent(item_id)
    
    def bind_select(self, callback: Callable):
        """绑定选择事件"""
        self.group_tree.bind('<<TreeviewSelect>>', callback)
    
    def update_title(self, lang_manager: LanguageManager):
        """更新面板标题"""
        self.frame.config(text=lang_manager.get_text('group_panel_title'))
        self.group_list_frame.config(text=lang_manager.get_text('group_list_title'))
        self.detail_frame.config(text=lang_manager.get_text('group_detail_title'))