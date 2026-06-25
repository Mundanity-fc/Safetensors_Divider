"""
主应用GUI
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from typing import Dict, List, Any, Optional

from ..core.parser import SafetensorsParser, TensorInfo
from ..core.tree_builder import TreeBuilder, TreeNode
from ..core.group_manager import GroupManager, TensorGroup
from ..core.exporter import SafetensorsExporter
from .language import LanguageManager
from .dialogs import GroupDialog
from .panels import LeftPanel, RightPanel
from .tree_utils import (
    build_group_tensor_tree, count_tensors_in_tree,
    get_node_info_text, find_group_node, format_size
)


class SafetensorsViewerApp:
    """safetensors可视化工具主应用"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("1200x800")
        
        # 初始化语言管理器
        self.lang_manager = LanguageManager()
        self.lang_manager.register_callback(self._on_language_changed)
        
        # 设置窗口标题
        self._update_window_title()
        
        # 设置中文字体
        self.setup_chinese_font()
        
        # 核心组件
        self.parser: Optional[SafetensorsParser] = None
        self.tree_builder: Optional[TreeBuilder] = None
        self.group_manager = GroupManager()
        self.exporter: Optional[SafetensorsExporter] = None
        
        # 当前状态
        self.current_file = None
        self.tensors: Dict[str, TensorInfo] = {}
        self.tree_root: Optional[TreeNode] = None
        
        # GUI组件
        self.menu_bar = None
        self.toolbar_buttons = {}
        self.status_var = None
        self.language_var = None
        self.left_panel: Optional[LeftPanel] = None
        self.right_panel: Optional[RightPanel] = None
        
        # 创建界面
        self.setup_ui()
    
    def _update_window_title(self):
        """更新窗口标题"""
        self.root.title(self.lang_manager.get_text('window_title'))
    
    def setup_chinese_font(self):
        """设置中文字体"""
        import tkinter.font as tkFont
        
        chinese_fonts = [
            "Source Han Sans SC",
            "Noto Sans CJK SC",
            "WenQuanYi Micro Hei",
            "Microsoft YaHei",
            "SimHei",
            "SimSun",
            "FangSong",
            "KaiTi"
        ]
        
        selected_font = None
        for font_name in chinese_fonts:
            try:
                self.root.tk.call('font', 'configure', 'TkDefaultFont', '-family', font_name, '-size', '10')
                self.root.tk.call('font', 'configure', 'TkTextFont', '-family', font_name, '-size', '10')
                self.root.tk.call('font', 'configure', 'TkFixedFont', '-family', font_name, '-size', '10')
                self.root.tk.call('font', 'configure', 'TkMenuFont', '-family', font_name, '-size', '10')
                self.root.tk.call('font', 'configure', 'TkHeadingFont', '-family', font_name, '-size', '10')
                
                actual_family = self.root.tk.call('font', 'configure', 'TkDefaultFont', '-family')
                if actual_family == font_name:
                    selected_font = font_name
                    break
            except Exception:
                continue
        
        if selected_font:
            print(f"已设置中文字体: {selected_font}")
        else:
            try:
                self.root.tk.call('font', 'configure', 'TkDefaultFont', '-family', 'sans-serif', '-size', '10')
                self.root.tk.call('font', 'configure', 'TkTextFont', '-family', 'sans-serif', '-size', '10')
                self.root.tk.call('font', 'configure', 'TkFixedFont', '-family', 'monospace', '-size', '10')
                self.root.tk.call('font', 'configure', 'TkMenuFont', '-family', 'sans-serif', '-size', '10')
                self.root.tk.call('font', 'configure', 'TkHeadingFont', '-family', 'sans-serif', '-size', '10')
                print("已设置字体: sans-serif")
            except Exception as e:
                print(f"设置字体失败: {e}")
                default_font = tkFont.nametofont("TkDefaultFont")
                default_font.configure(family="Helvetica", size=10)
    
    def setup_ui(self):
        """设置用户界面"""
        lang = self.lang_manager
        
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建菜单栏
        self.create_menu()
        
        # 创建工具栏
        self.create_toolbar(main_frame)
        
        # 创建主分割窗口
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # 创建左侧面板
        self.left_panel = LeftPanel(paned_window, lang)
        self.left_panel.bind_select(self.on_tree_select)
        paned_window.add(self.left_panel.frame, weight=1)
        
        # 创建右侧面板
        self.right_panel = RightPanel(paned_window, lang)
        self.right_panel.bind_select(self.on_group_select)
        self._create_right_panel_buttons()
        paned_window.add(self.right_panel.frame, weight=1)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set(lang.get_text('status_ready'))
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, pady=(5, 0))
    
    def _create_right_panel_buttons(self):
        """创建右侧面板的按钮"""
        lang = self.lang_manager
        
        self.toolbar_buttons['add_to_group'] = self.right_panel.add_button(
            lang.get_text('btn_add_to_group'), self.add_to_group
        )
        self.toolbar_buttons['remove_from_group'] = self.right_panel.add_button(
            lang.get_text('btn_remove_from_group'), self.remove_from_group
        )
        self.toolbar_buttons['delete_group'] = self.right_panel.add_button(
            lang.get_text('btn_delete_group'), self.delete_group
        )
    
    def create_menu(self):
        """创建菜单栏"""
        lang = self.lang_manager
        
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        # 文件菜单
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=lang.get_text('menu_file'), menu=file_menu)
        file_menu.add_command(label=lang.get_text('menu_open_file'), command=self.open_file)
        file_menu.add_command(label=lang.get_text('menu_save_groups'), command=self.save_groups)
        file_menu.add_command(label=lang.get_text('menu_load_groups'), command=self.load_groups)
        file_menu.add_separator()
        file_menu.add_command(label=lang.get_text('menu_exit'), command=self.root.quit)
        
        # 操作菜单
        operation_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=lang.get_text('menu_operation'), menu=operation_menu)
        operation_menu.add_command(label=lang.get_text('menu_create_group'), command=self.create_group)
        operation_menu.add_command(label=lang.get_text('menu_export_groups'), command=self.export_groups)
        operation_menu.add_command(label=lang.get_text('menu_refresh_view'), command=self.refresh_view)
        
        # 语言菜单
        language_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=lang.get_text('menu_language'), menu=language_menu)
        
        self.language_var = tk.StringVar(value=lang.language)
        for lang_code, lang_name in lang.get_supported_languages().items():
            language_menu.add_radiobutton(
                label=lang_name,
                variable=self.language_var,
                value=lang_code,
                command=lambda code=lang_code: self._change_language(code)
            )
        
        # 帮助菜单
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=lang.get_text('menu_help'), menu=help_menu)
        help_menu.add_command(label=lang.get_text('menu_about'), command=self.show_about)
    
    def create_toolbar(self, parent):
        """创建工具栏"""
        lang = self.lang_manager
        
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        self.toolbar_buttons['open'] = ttk.Button(
            toolbar, text=lang.get_text('btn_open_file'), command=self.open_file
        )
        self.toolbar_buttons['open'].pack(side=tk.LEFT, padx=2)
        
        self.toolbar_buttons['create_group'] = ttk.Button(
            toolbar, text=lang.get_text('btn_create_group'), command=self.create_group
        )
        self.toolbar_buttons['create_group'].pack(side=tk.LEFT, padx=2)
        
        self.toolbar_buttons['export'] = ttk.Button(
            toolbar, text=lang.get_text('btn_export'), command=self.export_groups
        )
        self.toolbar_buttons['export'].pack(side=tk.LEFT, padx=2)
        
        self.toolbar_buttons['refresh'] = ttk.Button(
            toolbar, text=lang.get_text('btn_refresh'), command=self.refresh_view
        )
        self.toolbar_buttons['refresh'].pack(side=tk.LEFT, padx=2)
    
    def _change_language(self, lang_code: str):
        """切换语言"""
        self.lang_manager.language = lang_code
    
    def _on_language_changed(self, new_lang: str):
        """语言变更回调函数"""
        lang = self.lang_manager
        
        # 更新窗口标题
        self._update_window_title()
        
        # 重建菜单栏
        self.create_menu()
        
        # 更新工具栏按钮
        button_texts = {
            'open': 'btn_open_file',
            'create_group': 'btn_create_group',
            'export': 'btn_export',
            'refresh': 'btn_refresh',
            'add_to_group': 'btn_add_to_group',
            'remove_from_group': 'btn_remove_from_group',
            'delete_group': 'btn_delete_group'
        }
        for btn_name, text_key in button_texts.items():
            if btn_name in self.toolbar_buttons:
                self.toolbar_buttons[btn_name].config(text=lang.get_text(text_key))
        
        # 更新面板标题
        if self.left_panel:
            self.left_panel.update_title(lang)
        if self.right_panel:
            self.right_panel.update_title(lang)
        
        # 更新状态栏
        self.status_var.set(lang.get_text('status_ready'))
        
        # 更新语言变量
        self.language_var.set(new_lang)
        
        # 刷新节点信息显示
        if self.left_panel:
            selection = self.left_panel.get_selection()
            if selection:
                item_values = self.left_panel.get_item(selection[0]).get('values')
                if item_values:
                    self.show_node_info(item_values[0])
    
    def open_file(self):
        """打开文件对话框"""
        lang = self.lang_manager
        
        filetypes = [
            (lang.get_text('filetype_json'), "*.json"),
            (lang.get_text('filetype_safetensors'), "*.safetensors"),
            (lang.get_text('filetype_all'), "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title=lang.get_text('dialog_open_file_title'),
            filetypes=filetypes
        )
        
        if filename:
            self.load_file(filename)
    
    def load_file(self, filename: str):
        """加载文件"""
        lang = self.lang_manager
        
        try:
            self.parser = SafetensorsParser(filename)
            if self.parser.load():
                self.current_file = filename
                self.tensors = self.parser.index.tensors if self.parser.index else {}
                
                self.tree_builder = TreeBuilder()
                self.tree_root = self.tree_builder.build_from_tensors(self.tensors)
                
                self.update_tree_view()
                self.update_status(lang.get_text('status_file_loaded', filename=os.path.basename(filename)))
                
                output_dir = os.path.dirname(filename)
                self.exporter = SafetensorsExporter(output_dir)
            else:
                messagebox.showerror(lang.get_text('msg_error'), lang.get_text('msg_cannot_load_file'))
        except Exception as e:
            messagebox.showerror(lang.get_text('msg_error'), lang.get_text('msg_error_loading_file', error=str(e)))
    
    def update_tree_view(self):
        """更新树状图显示"""
        if self.left_panel:
            self.left_panel.update_tree(self.tree_root, format_size)
    
    def on_tree_select(self, event):
        """树状图选择事件处理"""
        if not self.left_panel:
            return
        
        selection = self.left_panel.get_selection()
        if not selection:
            return
        
        item_values = self.left_panel.get_item(selection[0]).get('values')
        if item_values:
            node_path = item_values[0]
            self.show_node_info(node_path)
    
    def show_node_info(self, node_path: str):
        """显示节点信息"""
        lang = self.lang_manager
        
        if not self.tree_builder or not self.left_panel:
            return
        
        node = self.tree_builder.find_node_by_path(node_path)
        if not node:
            return
        
        info_lines = [
            lang.get_text('info_path', path=node.full_path),
            lang.get_text('info_name', name=node.name),
            lang.get_text('info_tensor_count', count=node.tensor_count),
            lang.get_text('info_total_size', size=format_size(node.total_size)),
            lang.get_text('info_is_leaf', yes_or_no=lang.get_text('info_yes') if node.is_leaf else lang.get_text('info_no'))
        ]
        
        if node.tensors:
            info_lines.append("\n" + lang.get_text('info_contained_tensors'))
            for tensor in node.tensors:
                info_lines.append(f"  - {tensor.name}: {tensor.dtype} {tensor.shape}")
        
        self.left_panel.update_info(info_lines)
    
    def create_group(self):
        """创建新分组"""
        lang = self.lang_manager
        dialog = GroupDialog(self.root, lang)
        
        if dialog.result:
            group_id, name, description = dialog.result
            try:
                self.group_manager.create_group(group_id, name, description)
                self.update_group_list()
                self.update_status(lang.get_text('status_group_created', name=name))
            except ValueError as e:
                messagebox.showerror(lang.get_text('msg_error'), str(e))
    
    def add_to_group(self):
        """添加选中的tensor到分组"""
        lang = self.lang_manager
        
        # 获取选中的树节点
        tree_selection = self.left_panel.get_selection() if self.left_panel else []
        if not tree_selection:
            messagebox.showwarning(lang.get_text('msg_warning'), lang.get_text('msg_select_node_first'))
            return
        
        # 获取选中的分组
        group_selection = self.right_panel.get_selection() if self.right_panel else []
        if not group_selection:
            messagebox.showwarning(lang.get_text('msg_warning'), lang.get_text('msg_select_group_first'))
            return
        
        # 获取节点路径
        item_values = self.left_panel.get_item(tree_selection[0]).get('values')
        if not item_values:
            return
        
        node_path = item_values[0]
        
        # 获取分组ID
        group_node_id = find_group_node(self.right_panel.group_tree, group_selection[0])
        if not group_node_id:
            return
        
        group_item = self.right_panel.get_item(group_node_id)
        group_id = group_item['values'][0]
        
        # 获取节点及其所有tensor
        node = self.tree_builder.find_node_by_path(node_path)
        if not node:
            return
        
        # 收集所有tensor名称
        tensor_names = []
        self._collect_tensor_names(node, tensor_names)
        
        # 添加到分组
        for tensor_name in tensor_names:
            self.group_manager.add_tensor_to_group(group_id, tensor_name)
        
        self.update_group_list()
        self.update_status(lang.get_text('status_tensors_added', count=len(tensor_names)))
    
    def _collect_tensor_names(self, node: TreeNode, names: List[str]):
        """递归收集tensor名称"""
        for tensor in node.tensors:
            names.append(tensor.name)
        for child in node.children.values():
            self._collect_tensor_names(child, names)
    
    def remove_from_group(self):
        """从分组中移除选中的tensor"""
        lang = self.lang_manager
        
        group_selection = self.right_panel.get_selection() if self.right_panel else []
        if not group_selection:
            messagebox.showwarning(lang.get_text('msg_warning'), lang.get_text('msg_select_group_first'))
            return
        
        group_item = self.right_panel.get_item(group_selection[0])
        item_tags = group_item.get('tags', [])
        
        if 'tensor' not in item_tags:
            messagebox.showwarning(lang.get_text('msg_warning'), lang.get_text('msg_select_tensor_to_remove'))
            return
        
        tensor_name = group_item['values'][0]
        parent_id = self.right_panel.parent(group_selection[0])
        if parent_id:
            parent_item = self.right_panel.get_item(parent_id)
            group_node_id = find_group_node(self.right_panel.group_tree, parent_id)
            if group_node_id:
                group_id = self.right_panel.get_item(group_node_id)['values'][0]
                self.group_manager.remove_tensor_from_group(group_id, tensor_name)
                self.update_group_list()
                self.update_status(lang.get_text('status_tensor_removed', name=tensor_name))
    
    def on_group_select(self, event):
        """分组树选择事件处理"""
        if not self.right_panel:
            return
        
        selection = self.right_panel.get_selection()
        if not selection:
            return
        
        item = self.right_panel.get_item(selection[0])
        item_tags = item.get('tags', [])
        
        info_lines = get_node_info_text(
            item_tags, item['values'],
            self.group_manager, self.tensors,
            self.lang_manager, self.right_panel.group_tree, selection[0]
        )
        
        self.right_panel.update_detail(info_lines)
    
    def delete_group(self):
        """删除选中的分组"""
        lang = self.lang_manager
        
        selection = self.right_panel.get_selection() if self.right_panel else []
        if not selection:
            messagebox.showwarning(lang.get_text('msg_warning'), lang.get_text('msg_select_group_first'))
            return
        
        group_node_id = find_group_node(self.right_panel.group_tree, selection[0])
        if not group_node_id:
            return
        
        group_item = self.right_panel.get_item(group_node_id)
        group_id = group_item['values'][0]
        group_name = group_item['text']
        
        if messagebox.askyesno(lang.get_text('msg_confirm'), lang.get_text('msg_confirm_delete_group', name=group_name)):
            self.group_manager.delete_group(group_id)
            self.update_group_list()
            self.update_status(lang.get_text('status_group_deleted', name=group_name))
    
    def export_groups(self):
        """导出分组"""
        lang = self.lang_manager
        
        if not self.exporter:
            messagebox.showwarning(lang.get_text('msg_warning'), lang.get_text('msg_no_file_loaded'))
            return
        
        groups = self.group_manager.get_all_groups()
        if not groups:
            messagebox.showwarning(lang.get_text('msg_warning'), lang.get_text('msg_no_groups_to_export'))
            return
        
        output_dir = filedialog.askdirectory(title=lang.get_text('dialog_export_dir_title'))
        if not output_dir:
            return
        
        self.exporter = SafetensorsExporter(output_dir)
        
        success_count = 0
        for group in groups:
            if self.exporter.export_group(group, self.tensors, os.path.dirname(self.current_file)):
                success_count += 1
        
        messagebox.showinfo(lang.get_text('msg_info'), lang.get_text('msg_export_success', count=success_count, dir=output_dir))
        self.update_status(lang.get_text('status_export_complete', count=success_count))
    
    def save_groups(self):
        """保存分组到文件"""
        lang = self.lang_manager
        
        filename = filedialog.asksaveasfilename(
            title=lang.get_text('dialog_save_groups_title'),
            defaultextension=".json",
            filetypes=[(lang.get_text('filetype_json'), "*.json")]
        )
        
        if filename:
            self.group_manager.save_to_file(filename)
            self.update_status(lang.get_text('status_groups_saved', filename=os.path.basename(filename)))
    
    def load_groups(self):
        """从文件加载分组"""
        lang = self.lang_manager
        
        filename = filedialog.askopenfilename(
            title=lang.get_text('dialog_load_groups_title'),
            filetypes=[(lang.get_text('filetype_json'), "*.json")]
        )
        
        if filename:
            if self.group_manager.load_from_file(filename):
                self.update_group_list()
                self.update_status(lang.get_text('status_groups_loaded', filename=os.path.basename(filename)))
            else:
                messagebox.showerror(lang.get_text('msg_error'), lang.get_text('msg_cannot_load_groups'))
    
    def refresh_view(self):
        """刷新视图"""
        lang = self.lang_manager
        
        if self.tree_root:
            self.update_tree_view()
        self.update_group_list()
        self.update_status(lang.get_text('status_view_refreshed'))
    
    def update_group_list(self):
        """更新分组列表显示（树形结构）"""
        lang = self.lang_manager
        
        if not self.right_panel:
            return
        
        # 清空现有项目
        self.right_panel.clear()
        
        # 添加分组
        for group in self.group_manager.get_all_groups():
            # 计算分组大小
            total_size = 0
            valid_tensors = {}
            for tensor_name in group.tensor_names:
                if tensor_name in self.tensors:
                    total_size += self.tensors[tensor_name].size_bytes
                    valid_tensors[tensor_name] = self.tensors[tensor_name]
            
            # 插入分组节点
            group_text = lang.get_text('group_node_info', 
                                       name=group.name, 
                                       count=len(group.tensor_names),
                                       size=format_size(total_size))
            
            group_id = self.right_panel.insert('', 'end', 
                                               text=group_text,
                                               values=(group.group_id,),
                                               tags=('group',),
                                               open=True)
            
            # 构建分组内的tensor树形结构
            tree = build_group_tensor_tree(valid_tensors)
            self._insert_tree_nodes(group_id, tree)
    
    def _insert_tree_nodes(self, parent_id: str, tree: Dict):
        """递归插入树节点"""
        lang = self.lang_manager
        
        for name, subtree in tree.items():
            has_children = bool(subtree.get('__children__', {}))
            has_tensors = bool(subtree.get('__tensors__', {}))
            
            if has_children:
                tensor_count = count_tensors_in_tree(subtree)
                prefix_text = lang.get_text('prefix_node_info', name=name, count=tensor_count)
                prefix_id = self.right_panel.insert(parent_id, 'end',
                                                    text=prefix_text,
                                                    values=(name,),
                                                    tags=('prefix',),
                                                    open=True)
                
                self._insert_tree_nodes(prefix_id, subtree.get('__children__', {}))
                
                for tensor_name, tensor_info in subtree.get('__tensors__', {}).items():
                    self._insert_tensor_node(prefix_id, tensor_name, tensor_info)
            elif has_tensors:
                if len(subtree['__tensors__']) == 1:
                    tensor_name, tensor_info = list(subtree['__tensors__'].items())[0]
                    self._insert_tensor_node(parent_id, tensor_name, tensor_info)
                else:
                    prefix_text = lang.get_text('prefix_node_info', name=name, count=len(subtree['__tensors__']))
                    prefix_id = self.right_panel.insert(parent_id, 'end',
                                                        text=prefix_text,
                                                        values=(name,),
                                                        tags=('prefix',),
                                                        open=True)
                    
                    for tensor_name, tensor_info in subtree['__tensors__'].items():
                        self._insert_tensor_node(prefix_id, tensor_name, tensor_info)
    
    def _insert_tensor_node(self, parent_id: str, tensor_name: str, tensor_info: TensorInfo):
        """插入tensor节点"""
        lang = self.lang_manager
        
        short_name = tensor_name.split('.')[-1]
        tensor_text = lang.get_text('tensor_node_info',
                                    name=short_name,
                                    dtype=tensor_info.dtype,
                                    shape=tensor_info.shape)
        
        self.right_panel.insert(parent_id, 'end',
                                text=tensor_text,
                                values=(tensor_name,),
                                tags=('tensor',))
    
    def show_about(self):
        """显示关于对话框"""
        lang = self.lang_manager
        messagebox.showinfo(lang.get_text('dialog_about_title'), lang.get_text('about_text'))
    
    def update_status(self, message: str):
        """更新状态栏"""
        self.status_var.set(message)
    
    def run(self):
        """运行应用程序"""
        self.root.mainloop()