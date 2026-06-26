"""
面板模块
包含左右侧面板的创建和管理
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Callable, Optional, Set

from ..core.parser import TensorInfo
from ..core.tree_builder import TreeNode, natural_sort_key
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
        
        # 添加左侧滚动条
        tree_scroll = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.tree_view.yview)
        tree_scroll.pack(side=tk.LEFT, fill=tk.Y)
        
        # 配置树状图控件
        self.tree_view.pack(fill=tk.BOTH, expand=True)
        self.tree_view.configure(yscrollcommand=tree_scroll.set)
        
        # 信息显示区域
        self.info_frame = ttk.LabelFrame(self.frame, text=lang_manager.get_text('info_panel_title'))
        self.info_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.info_text = tk.Text(self.info_frame, height=6, state=tk.DISABLED)
        self.info_text.pack(fill=tk.X, padx=5, pady=5)
    
    def pack(self, **kwargs):
        """打包面板"""
        self.frame.pack(**kwargs)
    
    def update_tree(self, tree_root: Optional[TreeNode], format_size_func: Callable,
                    open_states: Optional[Dict[str, bool]] = None):
        """更新树状图显示"""
        # 清空现有项目
        for item in self.tree_view.get_children():
            self.tree_view.delete(item)
        
        if not tree_root:
            return
        
        # 递归添加节点
        self._add_tree_nodes('', tree_root, format_size_func, open_states)
    
    def _add_tree_nodes(self, parent_id: str, node: TreeNode, format_size_func: Callable,
                        open_states: Optional[Dict[str, bool]] = None):
        """递归添加树节点"""
        if node.name == 'root':
            # 根节点，直接添加子节点（按自然排序）
            sorted_children = sorted(node.children.items(), key=lambda x: natural_sort_key(x[0]))
            for child_name, child_node in sorted_children:
                self._add_tree_nodes(parent_id, child_node, format_size_func, open_states)
        else:
            # 计算显示文本
            if node.tensors and len(node.children) == 0:
                # 叶子节点且包含tensor，显示tensor详细信息
                tensor = node.tensors[0]
                shape_str = str(tensor.shape) if tensor.shape else "[]"
                display_text = f"{node.name} {shape_str} ({format_size_func(tensor.size_bytes)})"
            else:
                # 非叶子节点或不包含tensor
                direct_children_count = len(node.children)
                display_text = f"{node.name} [{direct_children_count}] ({node.tensor_count} tensors, {format_size_func(node.total_size)})"
            
            # 确定节点的展开状态
            is_open = True  # 默认展开
            if open_states and node.full_path in open_states:
                is_open = open_states[node.full_path]
            
            # 添加节点
            node_id = self.tree_view.insert(
                parent_id, 'end', 
                text=display_text,
                values=(node.full_path, node.tensor_count, format_size_func(node.total_size)),
                open=is_open
            )
            
            # 递归添加子节点（按自然排序）
            sorted_children = sorted(node.children.items(), key=lambda x: natural_sort_key(x[0]))
            for child_name, child_node in sorted_children:
                self._add_tree_nodes(node_id, child_node, format_size_func, open_states)
    
    def get_open_states(self) -> Dict[str, bool]:
        """获取所有节点的展开状态"""
        states = {}
        self._collect_open_states('', states)
        return states
    
    def _collect_open_states(self, parent_id: str, states: Dict[str, bool]):
        """递归收集节点展开状态"""
        for child_id in self.tree_view.get_children(parent_id):
            item = self.tree_view.item(child_id)
            values = item.get('values', [])
            if values:
                node_path = values[0]
                states[node_path] = self.tree_view.item(child_id, 'open')
            self._collect_open_states(child_id, states)
    
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
    
    def bind_open_close(self, callback: Callable):
        """绑定节点展开/折叠事件"""
        self.tree_view.bind('<<TreeviewOpen>>', callback)
        self.tree_view.bind('<<TreeviewClose>>', callback)
    
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
        
        # 添加右侧滚动条
        group_scroll = ttk.Scrollbar(self.group_list_frame, orient=tk.VERTICAL, command=self.group_tree.yview)
        group_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 配置树形控件
        self.group_tree.pack(fill=tk.BOTH, expand=True)
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
    
    def bind_open_close(self, callback: Callable):
        """绑定节点展开/折叠事件"""
        self.group_tree.bind('<<TreeviewOpen>>', callback)
        self.group_tree.bind('<<TreeviewClose>>', callback)
    
    def get_open_states(self) -> Dict[str, bool]:
        """获取所有节点的展开状态"""
        states = {}
        self._collect_open_states('', states)
        return states
    
    def _collect_open_states(self, parent_id: str, states: Dict[str, bool]):
        """递归收集节点展开状态"""
        for child_id in self.group_tree.get_children(parent_id):
            item = self.group_tree.item(child_id)
            tags = item.get('tags', [])
            values = item.get('values', [])
            
            # 只收集prefix节点的展开状态（group节点默认展开）
            if 'prefix' in tags and values:
                node_path = values[0]
                states[node_path] = self.group_tree.item(child_id, 'open')
            
            self._collect_open_states(child_id, states)
    
    def update_title(self, lang_manager: LanguageManager):
        """更新面板标题"""
        self.frame.config(text=lang_manager.get_text('group_panel_title'))
        self.group_list_frame.config(text=lang_manager.get_text('group_list_title'))
        self.detail_frame.config(text=lang_manager.get_text('group_detail_title'))