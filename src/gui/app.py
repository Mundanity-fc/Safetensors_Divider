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
        
        # GUI组件引用（用于语言切换时更新）
        self.menu_bar = None
        self.toolbar_buttons = {}
        self.label_frames = {}
        self.tree_headings = {}
        self.group_headings = {}
        self.status_var = None
        self.info_text = None
        self.detail_text = None
        
        # 创建界面
        self.setup_ui()
    
    def _update_window_title(self):
        """更新窗口标题"""
        self.root.title(self.lang_manager.get_text('window_title'))
    
    def setup_chinese_font(self):
        """设置中文字体"""
        import tkinter.font as tkFont
        
        # 尝试使用的中文字体列表（按优先级排序）
        chinese_fonts = [
            "Source Han Sans SC",  # 思源黑体简体中文
            "Noto Sans CJK SC",
            "WenQuanYi Micro Hei",
            "Microsoft YaHei",
            "SimHei",
            "SimSun",
            "FangSong",
            "KaiTi"
        ]
        
        # 使用Tcl命令直接设置字体
        selected_font = None
        for font_name in chinese_fonts:
            try:
                # 使用Tcl命令设置字体
                self.root.tk.call('font', 'configure', 'TkDefaultFont', '-family', font_name, '-size', '10')
                self.root.tk.call('font', 'configure', 'TkTextFont', '-family', font_name, '-size', '10')
                self.root.tk.call('font', 'configure', 'TkFixedFont', '-family', font_name, '-size', '10')
                self.root.tk.call('font', 'configure', 'TkMenuFont', '-family', font_name, '-size', '10')
                self.root.tk.call('font', 'configure', 'TkHeadingFont', '-family', font_name, '-size', '10')
                
                # 检查字体是否真的被设置了
                actual_family = self.root.tk.call('font', 'configure', 'TkDefaultFont', '-family')
                if actual_family == font_name:
                    selected_font = font_name
                    break
            except Exception as e:
                print(f"设置字体 {font_name} 失败: {e}")
                continue
        
        if selected_font:
            print(f"已设置中文字体: {selected_font}")
        else:
            # 如果都失败，尝试使用sans-serif
            try:
                self.root.tk.call('font', 'configure', 'TkDefaultFont', '-family', 'sans-serif', '-size', '10')
                self.root.tk.call('font', 'configure', 'TkTextFont', '-family', 'sans-serif', '-size', '10')
                self.root.tk.call('font', 'configure', 'TkFixedFont', '-family', 'monospace', '-size', '10')
                self.root.tk.call('font', 'configure', 'TkMenuFont', '-family', 'sans-serif', '-size', '10')
                self.root.tk.call('font', 'configure', 'TkHeadingFont', '-family', 'sans-serif', '-size', '10')
                print("已设置字体: sans-serif")
            except Exception as e:
                print(f"设置字体失败: {e}")
                # 使用默认配置
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
        
        # 左侧面板 - 树状图显示
        self.label_frames['tree'] = ttk.LabelFrame(paned_window, text=lang.get_text('tree_panel_title'))
        paned_window.add(self.label_frames['tree'], weight=1)
        
        # 右侧面板 - 分组管理
        self.label_frames['group'] = ttk.LabelFrame(paned_window, text=lang.get_text('group_panel_title'))
        paned_window.add(self.label_frames['group'], weight=1)
        
        # 设置左侧面板
        self.setup_left_panel(self.label_frames['tree'])
        
        # 设置右侧面板
        self.setup_right_panel(self.label_frames['group'])
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set(lang.get_text('status_ready'))
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, pady=(5, 0))
    
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
        
        # 添加语言选项
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
        
        # 打开按钮
        self.toolbar_buttons['open'] = ttk.Button(
            toolbar, 
            text=lang.get_text('btn_open_file'), 
            command=self.open_file
        )
        self.toolbar_buttons['open'].pack(side=tk.LEFT, padx=2)
        
        # 创建分组按钮
        self.toolbar_buttons['create_group'] = ttk.Button(
            toolbar, 
            text=lang.get_text('btn_create_group'), 
            command=self.create_group
        )
        self.toolbar_buttons['create_group'].pack(side=tk.LEFT, padx=2)
        
        # 导出按钮
        self.toolbar_buttons['export'] = ttk.Button(
            toolbar, 
            text=lang.get_text('btn_export'), 
            command=self.export_groups
        )
        self.toolbar_buttons['export'].pack(side=tk.LEFT, padx=2)
        
        # 刷新按钮
        self.toolbar_buttons['refresh'] = ttk.Button(
            toolbar, 
            text=lang.get_text('btn_refresh'), 
            command=self.refresh_view
        )
        self.toolbar_buttons['refresh'].pack(side=tk.LEFT, padx=2)
    
    def setup_left_panel(self, parent):
        """设置左侧面板（树状图）"""
        lang = self.lang_manager
        
        # 树状图显示
        self.tree_frame = ttk.Frame(parent)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建树状图控件
        self.tree_view = ttk.Treeview(self.tree_frame)
        self.tree_view.pack(fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        tree_scroll = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.tree_view.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_view.configure(yscrollcommand=tree_scroll.set)
        
        # 绑定选择事件
        self.tree_view.bind('<<TreeviewSelect>>', self.on_tree_select)
        
        # 信息显示区域
        self.label_frames['info'] = ttk.LabelFrame(parent, text=lang.get_text('info_panel_title'))
        self.label_frames['info'].pack(fill=tk.X, pady=(5, 0))
        
        self.info_text = tk.Text(self.label_frames['info'], height=6, state=tk.DISABLED)
        self.info_text.pack(fill=tk.X, padx=5, pady=5)
    
    def setup_right_panel(self, parent):
        """设置右侧面板（分组管理）"""
        lang = self.lang_manager
        
        # 分组列表 - 使用树形结构
        self.label_frames['group_list'] = ttk.LabelFrame(parent, text=lang.get_text('group_list_title'))
        self.label_frames['group_list'].pack(fill=tk.BOTH, expand=True)
        
        # 创建分组树形视图
        self.group_tree = ttk.Treeview(self.label_frames['group_list'])
        self.group_tree.pack(fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        group_scroll = ttk.Scrollbar(self.label_frames['group_list'], orient=tk.VERTICAL, command=self.group_tree.yview)
        group_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.group_tree.configure(yscrollcommand=group_scroll.set)
        
        # 绑定选择事件
        self.group_tree.bind('<<TreeviewSelect>>', self.on_group_select)
        
        # 分组操作按钮
        group_ops_frame = ttk.Frame(parent)
        group_ops_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.toolbar_buttons['add_to_group'] = ttk.Button(
            group_ops_frame, 
            text=lang.get_text('btn_add_to_group'), 
            command=self.add_to_group
        )
        self.toolbar_buttons['add_to_group'].pack(side=tk.LEFT, padx=2)
        
        self.toolbar_buttons['remove_from_group'] = ttk.Button(
            group_ops_frame, 
            text=lang.get_text('btn_remove_from_group'), 
            command=self.remove_from_group
        )
        self.toolbar_buttons['remove_from_group'].pack(side=tk.LEFT, padx=2)
        
        self.toolbar_buttons['delete_group'] = ttk.Button(
            group_ops_frame, 
            text=lang.get_text('btn_delete_group'), 
            command=self.delete_group
        )
        self.toolbar_buttons['delete_group'].pack(side=tk.LEFT, padx=2)
        
        # 分组详情显示
        self.label_frames['group_detail'] = ttk.LabelFrame(parent, text=lang.get_text('group_detail_title'))
        self.label_frames['group_detail'].pack(fill=tk.X, pady=(5, 0))
        
        self.detail_text = tk.Text(self.label_frames['group_detail'], height=6, state=tk.DISABLED)
        self.detail_text.pack(fill=tk.X, padx=5, pady=5)
    
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
        if 'open' in self.toolbar_buttons:
            self.toolbar_buttons['open'].config(text=lang.get_text('btn_open_file'))
        if 'create_group' in self.toolbar_buttons:
            self.toolbar_buttons['create_group'].config(text=lang.get_text('btn_create_group'))
        if 'export' in self.toolbar_buttons:
            self.toolbar_buttons['export'].config(text=lang.get_text('btn_export'))
        if 'refresh' in self.toolbar_buttons:
            self.toolbar_buttons['refresh'].config(text=lang.get_text('btn_refresh'))
        if 'add_to_group' in self.toolbar_buttons:
            self.toolbar_buttons['add_to_group'].config(text=lang.get_text('btn_add_to_group'))
        if 'remove_from_group' in self.toolbar_buttons:
            self.toolbar_buttons['remove_from_group'].config(text=lang.get_text('btn_remove_from_group'))
        if 'delete_group' in self.toolbar_buttons:
            self.toolbar_buttons['delete_group'].config(text=lang.get_text('btn_delete_group'))
        
        # 更新LabelFrame标题
        if 'tree' in self.label_frames:
            self.label_frames['tree'].config(text=lang.get_text('tree_panel_title'))
        if 'group' in self.label_frames:
            self.label_frames['group'].config(text=lang.get_text('group_panel_title'))
        if 'info' in self.label_frames:
            self.label_frames['info'].config(text=lang.get_text('info_panel_title'))
        if 'group_list' in self.label_frames:
            self.label_frames['group_list'].config(text=lang.get_text('group_list_title'))
        if 'group_detail' in self.label_frames:
            self.label_frames['group_detail'].config(text=lang.get_text('group_detail_title'))
        
        # 更新状态栏
        self.status_var.set(lang.get_text('status_ready'))
        
        # 更新语言变量
        self.language_var.set(new_lang)
        
        # 刷新节点信息显示（如果有的话）
        if self.tree_builder:
            selection = self.tree_view.selection()
            if selection:
                item_values = self.tree_view.item(selection[0], 'values')
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
                
                # 构建树状结构
                self.tree_builder = TreeBuilder()
                self.tree_root = self.tree_builder.build_from_tensors(self.tensors)
                
                # 更新界面
                self.update_tree_view()
                self.update_status(lang.get_text('status_file_loaded', filename=os.path.basename(filename)))
                
                # 设置导出器
                output_dir = os.path.dirname(filename)
                self.exporter = SafetensorsExporter(output_dir)
            else:
                messagebox.showerror(lang.get_text('msg_error'), lang.get_text('msg_cannot_load_file'))
        except Exception as e:
            messagebox.showerror(lang.get_text('msg_error'), lang.get_text('msg_error_loading_file', error=str(e)))
    
    def update_tree_view(self):
        """更新树状图显示"""
        # 清空现有项目
        for item in self.tree_view.get_children():
            self.tree_view.delete(item)
        
        if not self.tree_root:
            return
        
        # 递归添加节点
        self._add_tree_nodes('', self.tree_root)
    
    def _add_tree_nodes(self, parent_id: str, node: TreeNode):
        """递归添加树节点"""
        if node.name == 'root':
            # 根节点，直接添加子节点
            for child_name, child_node in node.children.items():
                self._add_tree_nodes(parent_id, child_node)
        else:
            # 计算显示文本
            display_text = f"{node.name} ({node.tensor_count} tensors, {self.format_size(node.total_size)})"
            
            # 添加节点
            node_id = self.tree_view.insert(
                parent_id, 'end', 
                text=display_text,
                values=(node.full_path, node.tensor_count, self.format_size(node.total_size))
            )
            
            # 递归添加子节点
            for child_name, child_node in node.children.items():
                self._add_tree_nodes(node_id, child_node)
    
    def format_size(self, size_bytes: int) -> str:
        """格式化大小显示"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    def on_tree_select(self, event):
        """树状图选择事件处理"""
        selection = self.tree_view.selection()
        if not selection:
            return
        
        item_id = selection[0]
        item_values = self.tree_view.item(item_id, 'values')
        
        if item_values:
            node_path = item_values[0]
            self.show_node_info(node_path)
    
    def show_node_info(self, node_path: str):
        """显示节点信息"""
        lang = self.lang_manager
        
        if not self.tree_builder:
            return
        
        node = self.tree_builder.find_node_by_path(node_path)
        if not node:
            return
        
        # 更新信息文本
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        
        info_lines = [
            lang.get_text('info_path', path=node.full_path),
            lang.get_text('info_name', name=node.name),
            lang.get_text('info_tensor_count', count=node.tensor_count),
            lang.get_text('info_total_size', size=self.format_size(node.total_size)),
            lang.get_text('info_is_leaf', yes_or_no=lang.get_text('info_yes') if node.is_leaf else lang.get_text('info_no'))
        ]
        
        if node.tensors:
            info_lines.append("\n" + lang.get_text('info_contained_tensors'))
            for tensor in node.tensors:
                info_lines.append(f"  - {tensor.name}: {tensor.dtype} {tensor.shape}")
        
        self.info_text.insert(1.0, "\n".join(info_lines))
        self.info_text.config(state=tk.DISABLED)
    
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
        tree_selection = self.tree_view.selection()
        if not tree_selection:
            messagebox.showwarning(lang.get_text('msg_warning'), lang.get_text('msg_select_node_first'))
            return
        
        # 获取选中的分组
        group_selection = self.group_tree.selection()
        if not group_selection:
            messagebox.showwarning(lang.get_text('msg_warning'), lang.get_text('msg_select_group_first'))
            return
        
        # 获取节点路径
        item_values = self.tree_view.item(tree_selection[0], 'values')
        if not item_values:
            return
        
        node_path = item_values[0]
        
        # 获取分组ID - 检查选中的是分组节点还是tensor节点
        group_item = self.group_tree.item(group_selection[0])
        item_tags = group_item.get('tags', [])
        
        # 如果选中的是tensor节点，获取其父节点（分组节点）
        if 'tensor' in item_tags:
            parent_id = self.group_tree.parent(group_selection[0])
            if parent_id:
                group_item = self.group_tree.item(parent_id)
                group_id = group_item['values'][0]
            else:
                return
        else:
            # 选中的是分组节点
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
        
        # 获取选中的分组树节点
        group_selection = self.group_tree.selection()
        if not group_selection:
            messagebox.showwarning(lang.get_text('msg_warning'), lang.get_text('msg_select_group_first'))
            return
        
        # 获取选中项的信息
        group_item = self.group_tree.item(group_selection[0])
        item_tags = group_item.get('tags', [])
        
        # 只有选中tensor节点时才能移除
        if 'tensor' not in item_tags:
            messagebox.showwarning(lang.get_text('msg_warning'), lang.get_text('msg_select_tensor_to_remove'))
            return
        
        # 获取tensor名称和分组ID
        tensor_name = group_item['values'][0]
        parent_id = self.group_tree.parent(group_selection[0])
        if parent_id:
            parent_item = self.group_tree.item(parent_id)
            group_id = parent_item['values'][0]
            
            # 从分组中移除
            self.group_manager.remove_tensor_from_group(group_id, tensor_name)
            self.update_group_list()
            self.update_status(lang.get_text('status_tensor_removed', name=tensor_name))
    
    def on_group_select(self, event):
        """分组树选择事件处理"""
        selection = self.group_tree.selection()
        if not selection:
            return
        
        # 获取选中项的信息
        item = self.group_tree.item(selection[0])
        item_tags = item.get('tags', [])
        
        # 更新详情显示
        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.delete(1.0, tk.END)
        
        if 'group' in item_tags:
            # 选中的是分组节点
            group_id = item['values'][0]
            group = self.group_manager.groups.get(group_id)
            if group:
                lang = self.lang_manager
                total_size = 0
                for tensor_name in group.tensor_names:
                    if tensor_name in self.tensors:
                        total_size += self.tensors[tensor_name].size_bytes
                
                info_lines = [
                    f"Group ID: {group.group_id}",
                    f"{lang.get_text('label_group_name')} {group.name}",
                    f"{lang.get_text('label_description')} {group.description}",
                    f"{lang.get_text('col_tensor_count')} {len(group.tensor_names)}",
                    f"{lang.get_text('col_size')} {self.format_size(total_size)}"
                ]
                self.detail_text.insert(1.0, "\n".join(info_lines))
        elif 'tensor' in item_tags:
            # 选中的是tensor节点
            tensor_name = item['values'][0]
            if tensor_name in self.tensors:
                tensor_info = self.tensors[tensor_name]
                info_lines = [
                    f"Tensor: {tensor_name}",
                    f"Type: {tensor_info.dtype}",
                    f"Shape: {tensor_info.shape}",
                    f"Size: {self.format_size(tensor_info.size_bytes)}"
                ]
                self.detail_text.insert(1.0, "\n".join(info_lines))
        
        self.detail_text.config(state=tk.DISABLED)
    
    def delete_group(self):
        """删除选中的分组"""
        lang = self.lang_manager
        
        selection = self.group_tree.selection()
        if not selection:
            messagebox.showwarning(lang.get_text('msg_warning'), lang.get_text('msg_select_group_first'))
            return
        
        # 获取分组ID - 检查选中的是分组节点还是tensor节点
        group_item = self.group_tree.item(selection[0])
        item_tags = group_item.get('tags', [])
        
        # 如果选中的是tensor节点，获取其父节点（分组节点）
        if 'tensor' in item_tags:
            parent_id = self.group_tree.parent(selection[0])
            if parent_id:
                group_item = self.group_tree.item(parent_id)
            else:
                return
        
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
        
        # 选择导出目录
        output_dir = filedialog.askdirectory(title=lang.get_text('dialog_export_dir_title'))
        if not output_dir:
            return
        
        self.exporter = SafetensorsExporter(output_dir)
        
        # 导出每个分组
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
        
        # 清空现有项目
        for item in self.group_tree.get_children():
            self.group_tree.delete(item)
        
        # 添加分组（作为父节点）
        for group in self.group_manager.get_all_groups():
            # 计算分组大小
            total_size = 0
            for tensor_name in group.tensor_names:
                if tensor_name in self.tensors:
                    total_size += self.tensors[tensor_name].size_bytes
            
            # 插入分组节点
            group_text = lang.get_text('group_node_info', 
                                       name=group.name, 
                                       count=len(group.tensor_names),
                                       size=self.format_size(total_size))
            
            group_id = self.group_tree.insert('', 'end', 
                                              text=group_text,
                                              values=(group.group_id,),
                                              tags=('group',),
                                              open=True)  # 默认展开
            
            # 添加该分组下的tensor（作为子节点）
            for tensor_name in group.tensor_names:
                if tensor_name in self.tensors:
                    tensor_info = self.tensors[tensor_name]
                    tensor_text = lang.get_text('tensor_node_info',
                                               name=tensor_name,
                                               dtype=tensor_info.dtype,
                                               shape=tensor_info.shape)
                    
                    self.group_tree.insert(group_id, 'end',
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