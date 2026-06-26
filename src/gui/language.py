"""
语言管理模块
支持中英文切换
"""

from typing import Dict, Any

class LanguageManager:
    """语言管理器"""
    
    # 支持的语言
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'zh': '中文'
    }
    
    # 默认语言
    DEFAULT_LANGUAGE = 'en'
    
    # 翻译文本
    TRANSLATIONS = {
        'en': {
            # 窗口标题
            'window_title': 'Safetensors Visualization Split & Combine Tool',
            
            # 菜单
            'menu_file': 'File',
            'menu_edit': 'Edit',
            'menu_operation': 'Operation',
            'menu_help': 'Help',
            'menu_language': 'Language',
            
            # 文件菜单
            'menu_open_file': 'Open File',
            'menu_save_groups': 'Save Groups',
            'menu_load_groups': 'Load Groups',
            'menu_exit': 'Exit',
            
            # 操作菜单
            'menu_create_group': 'Create Group',
            'menu_export_groups': 'Export Groups',
            'menu_refresh_view': 'Refresh View',
            
            # 帮助菜单
            'menu_about': 'About',
            
            # 工具栏按钮
            'btn_open_file': 'Open File',
            'btn_create_group': 'Create Group',
            'btn_export_single': 'Export Single',
            'btn_export_all': 'Export All',
            'btn_refresh': 'Refresh',
            
            # 左侧面板
            'tree_panel_title': 'Tensor Structure Tree',
            'info_panel_title': 'Details',
            
            # 右侧面板
            'group_panel_title': 'Group Management',
            'group_list_title': 'Group List',
            'group_detail_title': 'Group Details',
            
            # 分组列表列标题
            'col_group_name': 'Group Name',
            'col_tensor_count': 'Tensor Count',
            'col_size': 'Size',
            
            # 分组操作按钮
            'btn_add_to_group': 'Add to Group',
            'btn_remove_from_group': 'Remove from Group',
            'btn_delete_group': 'Delete Group',
            
            # 状态栏
            'status_ready': 'Ready',
            'status_file_loaded': 'File loaded: {filename}',
            'status_group_created': 'Group created: {name}',
            'status_tensors_added': 'Added {count} tensors to group',
            'status_tensor_removed': 'Removed: {name}',
            'status_group_deleted': 'Group deleted: {name}',
            'status_export_single_complete': "Exported group '{name}'",
            'status_export_all_complete': 'Exported all {count} groups',
            'status_groups_saved': 'Groups saved to: {filename}',
            'status_groups_loaded': 'Groups loaded: {filename}',
            'status_view_refreshed': 'View refreshed',
            
            # 文件对话框
            'dialog_open_file_title': 'Select safetensors file or index.json',
            'dialog_save_groups_title': 'Save groups file',
            'dialog_load_groups_title': 'Load groups file',
            'dialog_export_dir_title': 'Select export directory',
            
            # 文件类型
            'filetype_json': 'JSON Files',
            'filetype_safetensors': 'Safetensors Files',
            'filetype_all': 'All Files',
            
            # 对话框标题
            'dialog_create_group_title': 'Create New Group',
            'dialog_about_title': 'About',
            
            # 对话框标签
            'label_group_id': 'Group ID:',
            'label_group_name': 'Group Name:',
            'label_description': 'Description:',
            'label_ok': 'OK',
            'label_cancel': 'Cancel',
            
            # 消息框
            'msg_error': 'Error',
            'msg_warning': 'Warning',
            'msg_info': 'Info',
            'msg_confirm': 'Confirm',
            'msg_cannot_load_file': 'Cannot load file',
            'msg_error_loading_file': 'Error loading file: {error}',
            'msg_select_node_first': 'Please select a node first',
            'msg_select_group_first': 'Please select a group first',
            'msg_select_tensor_to_remove': 'Please select a tensor to remove',
            'msg_confirm_delete_group': "Are you sure you want to delete group '{name}'?",
            'msg_no_file_loaded': 'Please load a file first',
            'msg_no_groups_to_export': 'No groups to export',
            'msg_export_success': 'Successfully exported {count} groups to:\n{dir}',
            'msg_export_single_success': "Successfully exported group '{name}' to:\n{dir}",
            'msg_export_all_success': 'Successfully exported all groups ({count}) to:\n{dir}',
            'msg_confirm_export_single': "Export group '{name}'?\n\n{count} tensors, {size}",
            'msg_confirm_export_all': 'Export all {count} groups?\n\nTotal: {tensor_count} tensors, {size}',
            'msg_cannot_load_groups': 'Cannot load groups file',
            'msg_group_id_name_empty': 'Group ID and name cannot be empty',
            'msg_select_group_for_export': 'Please select a group to export',
            'msg_export_failed': 'Export failed',
            
            # 关于对话框
            'about_text': 'Safetensors Visualization Split & Combine Tool\n\nFor visual management and splitting of large model safetensors files',
            
            # 节点信息
            'info_path': 'Path: {path}',
            'info_name': 'Name: {name}',
            'info_tensor_count': 'Tensor Count: {count}',
            'info_total_size': 'Total Size: {size}',
            'info_is_leaf': 'Is Leaf Node: {yes_or_no}',
            'info_yes': 'Yes',
            'info_no': 'No',
            'info_contained_tensors': 'Directly Contained Tensors:',
            
            # 分组树形显示
            'group_node_info': '{name} ({count} tensors, {size})',
            'tensor_node_info': '{name} {shape} ({size})',
            'prefix_node_info': '{name} ({count} tensors)',
            
            # 语言切换
            'language_changed': 'Language changed to {language}',
        },
        'zh': {
            # 窗口标题
            'window_title': 'Safetensors 可视化分割与组合工具',
            
            # 菜单
            'menu_file': '文件',
            'menu_edit': '编辑',
            'menu_operation': '操作',
            'menu_help': '帮助',
            'menu_language': '语言',
            
            # 文件菜单
            'menu_open_file': '打开文件',
            'menu_save_groups': '保存分组',
            'menu_load_groups': '加载分组',
            'menu_exit': '退出',
            
            # 操作菜单
            'menu_create_group': '创建分组',
            'menu_export_groups': '导出分组',
            'menu_refresh_view': '刷新视图',
            
            # 帮助菜单
            'menu_about': '关于',
            
            # 工具栏按钮
            'btn_open_file': '打开文件',
            'btn_create_group': '创建分组',
            'btn_export_single': '单独导出',
            'btn_export_all': '整体导出',
            'btn_refresh': '刷新',
            
            # 左侧面板
            'tree_panel_title': 'Tensor 结构树',
            'info_panel_title': '详细信息',
            
            # 右侧面板
            'group_panel_title': '分组管理',
            'group_list_title': '分组列表',
            'group_detail_title': '分组详情',
            
            # 分组列表列标题
            'col_group_name': '分组名称',
            'col_tensor_count': 'Tensor数量',
            'col_size': '大小',
            
            # 分组操作按钮
            'btn_add_to_group': '添加到分组',
            'btn_remove_from_group': '从分组移除',
            'btn_delete_group': '删除分组',
            
            # 状态栏
            'status_ready': '就绪',
            'status_file_loaded': '已加载文件: {filename}',
            'status_group_created': '创建分组: {name}',
            'status_tensors_added': '已添加 {count} 个tensor到分组',
            'status_tensor_removed': '已移除tensor: {name}',
            'status_group_deleted': '删除分组: {name}',
            'status_export_single_complete': "已导出分组 '{name}'",
            'status_export_all_complete': '已导出所有 {count} 个分组',
            'status_groups_saved': '分组已保存到: {filename}',
            'status_groups_loaded': '已加载分组: {filename}',
            'status_view_refreshed': '视图已刷新',
            
            # 文件对话框
            'dialog_open_file_title': '选择safetensors文件或index.json',
            'dialog_save_groups_title': '保存分组文件',
            'dialog_load_groups_title': '加载分组文件',
            'dialog_export_dir_title': '选择导出目录',
            
            # 文件类型
            'filetype_json': 'JSON文件',
            'filetype_safetensors': 'Safetensors文件',
            'filetype_all': '所有文件',
            
            # 对话框标题
            'dialog_create_group_title': '创建新分组',
            'dialog_about_title': '关于',
            
            # 对话框标签
            'label_group_id': '分组ID:',
            'label_group_name': '分组名称:',
            'label_description': '描述:',
            'label_ok': '确定',
            'label_cancel': '取消',
            
            # 消息框
            'msg_error': '错误',
            'msg_warning': '警告',
            'msg_info': '信息',
            'msg_confirm': '确认',
            'msg_cannot_load_file': '无法加载文件',
            'msg_error_loading_file': '加载文件时出错: {error}',
            'msg_select_node_first': '请先选择一个节点',
            'msg_select_group_first': '请先选择一个分组',
            'msg_select_tensor_to_remove': '请先选择要移除的tensor',
            'msg_confirm_delete_group': "确定要删除分组 '{name}' 吗？",
            'msg_no_file_loaded': '请先加载文件',
            'msg_no_groups_to_export': '没有可导出的分组',
            'msg_export_success': '成功导出 {count} 个分组到:\n{dir}',
            'msg_export_single_success': "成功导出分组 '{name}' 到:\n{dir}",
            'msg_export_all_success': '成功导出所有分组 ({count} 个) 到:\n{dir}',
            'msg_confirm_export_single': "导出分组 '{name}'？\n\n{count} 个tensor，{size}",
            'msg_confirm_export_all': '导出所有 {count} 个分组？\n\n共 {tensor_count} 个tensor，{size}',
            'msg_cannot_load_groups': '无法加载分组文件',
            'msg_group_id_name_empty': '分组ID和名称不能为空',
            'msg_select_group_for_export': '请先选择要导出的分组',
            'msg_export_failed': '导出失败',
            
            # 关于对话框
            'about_text': 'Safetensors 可视化分割与组合工具\n\n用于大模型safetensors文件的可视化管理和分割',
            
            # 节点信息
            'info_path': '路径: {path}',
            'info_name': '名称: {name}',
            'info_tensor_count': 'Tensor数量: {count}',
            'info_total_size': '总大小: {size}',
            'info_is_leaf': '是否为叶子节点: {yes_or_no}',
            'info_yes': '是',
            'info_no': '否',
            'info_contained_tensors': '直接包含的Tensor:',
            
            # 分组树形显示
            'group_node_info': '{name} ({count} 个tensor, {size})',
            'tensor_node_info': '{name} {shape} ({size})',
            'prefix_node_info': '{name} ({count} 个tensor)',
            
            # 语言切换
            'language_changed': '语言已切换为 {language}',
        }
    }
    
    def __init__(self, default_language: str = None):
        """
        初始化语言管理器
        
        Args:
            default_language: 默认语言代码，如果为None则使用类常量DEFAULT_LANGUAGE
        """
        self.current_language = default_language or self.DEFAULT_LANGUAGE
        self._callbacks = []  # 语言变更回调函数列表
    
    @property
    def language(self) -> str:
        """获取当前语言代码"""
        return self.current_language
    
    @language.setter
    def language(self, lang_code: str):
        """设置当前语言"""
        if lang_code in self.SUPPORTED_LANGUAGES:
            if self.current_language != lang_code:
                self.current_language = lang_code
                self._notify_callbacks()
    
    def get_text(self, key: str, **kwargs) -> str:
        """
        获取翻译文本
        
        Args:
            key: 文本键名
            **kwargs: 格式化参数
            
        Returns:
            翻译后的文本
        """
        translations = self.TRANSLATIONS.get(self.current_language, {})
        text = translations.get(key, key)  # 如果找不到翻译，返回键名
        
        if kwargs:
            try:
                return text.format(**kwargs)
            except (KeyError, IndexError):
                return text
        return text
    
    def get_language_name(self, lang_code: str = None) -> str:
        """获取语言名称"""
        code = lang_code or self.current_language
        return self.SUPPORTED_LANGUAGES.get(code, code)
    
    def get_supported_languages(self) -> Dict[str, str]:
        """获取支持的语言列表"""
        return self.SUPPORTED_LANGUAGES.copy()
    
    def register_callback(self, callback):
        """注册语言变更回调函数"""
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def unregister_callback(self, callback):
        """注销语言变更回调函数"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def _notify_callbacks(self):
        """通知所有回调函数语言已变更"""
        for callback in self._callbacks:
            try:
                callback(self.current_language)
            except Exception as e:
                print(f"Language callback error: {e}")