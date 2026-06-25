"""
树形结构工具模块
包含分组树形结构的构建和操作方法
"""

from typing import Dict, List, Any
from ..core.parser import TensorInfo


def build_group_tensor_tree(tensors: Dict[str, TensorInfo]) -> Dict:
    """
    构建分组内的tensor树形结构
    
    Args:
        tensors: tensor字典 {name: TensorInfo}
        
    Returns:
        树形结构字典
    """
    tree = {}
    
    for tensor_name, tensor_info in tensors.items():
        parts = tensor_name.split('.')
        current = tree
        
        # 构建树状路径
        for i, part in enumerate(parts[:-1]):
            if part not in current:
                current[part] = {'__children__': {}, '__tensors__': {}}
            current = current[part]['__children__']
        
        # 添加tensor信息
        leaf_name = parts[-1] if parts else tensor_name
        if leaf_name not in current:
            current[leaf_name] = {'__children__': {}, '__tensors__': {}}
        current[leaf_name]['__tensors__'][tensor_name] = tensor_info
    
    return tree


def count_tensors_in_tree(tree: Dict) -> int:
    """
    统计树中的tensor数量
    
    Args:
        tree: 树形结构字典
        
    Returns:
        tensor数量
    """
    count = len(tree.get('__tensors__', {}))
    for subtree in tree.get('__children__', {}).values():
        count += count_tensors_in_tree(subtree)
    return count


def get_node_info_text(node_tags: List[str], node_values: tuple, 
                       group_manager, tensors: Dict[str, TensorInfo],
                       lang_manager, tree_widget, node_id: str) -> List[str]:
    """
    获取节点信息文本
    
    Args:
        node_tags: 节点标签列表
        node_values: 节点值
        group_manager: 分组管理器
        tensors: tensor字典
        lang_manager: 语言管理器
        tree_widget: 树形控件
        node_id: 节点ID
        
    Returns:
        信息文本行列表
    """
    info_lines = []
    lang = lang_manager
    
    if 'group' in node_tags:
        # 分组节点
        group_id = node_values[0]
        group = group_manager.groups.get(group_id)
        if group:
            total_size = 0
            for tensor_name in group.tensor_names:
                if tensor_name in tensors:
                    total_size += tensors[tensor_name].size_bytes
            
            info_lines = [
                f"Group ID: {group.group_id}",
                f"{lang.get_text('label_group_name')} {group.name}",
                f"{lang.get_text('label_description')} {group.description}",
                f"{lang.get_text('col_tensor_count')} {len(group.tensor_names)}",
                f"{lang.get_text('col_size')} {format_size(total_size)}"
            ]
    elif 'prefix' in node_tags:
        # 前缀节点
        prefix_name = node_values[0]
        tensor_count, total_size = count_tensors_and_size_in_node(tree_widget, node_id, tensors)
        
        info_lines = [
            f"Prefix: {prefix_name}",
            f"{lang.get_text('col_tensor_count')} {tensor_count}",
            f"{lang.get_text('col_size')} {format_size(total_size)}"
        ]
    elif 'tensor' in node_tags:
        # tensor节点
        tensor_name = node_values[0]
        if tensor_name in tensors:
            tensor_info = tensors[tensor_name]
            info_lines = [
                f"Tensor: {tensor_name}",
                f"Type: {tensor_info.dtype}",
                f"Shape: {tensor_info.shape}",
                f"Size: {format_size(tensor_info.size_bytes)}"
            ]
    
    return info_lines


def count_tensors_and_size_in_node(tree_widget, node_id: str, 
                                    tensors: Dict[str, TensorInfo]) -> tuple:
    """
    统计节点下的tensor数量和大小
    
    Args:
        tree_widget: 树形控件
        node_id: 节点ID
        tensors: tensor字典
        
    Returns:
        (tensor数量, 总大小)
    """
    tensor_count = 0
    total_size = 0
    
    def count_recursive(current_id):
        nonlocal tensor_count, total_size
        for child_id in tree_widget.get_children(current_id):
            child_item = tree_widget.item(child_id)
            child_tags = child_item.get('tags', [])
            if 'tensor' in child_tags:
                tensor_name = child_item['values'][0]
                if tensor_name in tensors:
                    tensor_count += 1
                    total_size += tensors[tensor_name].size_bytes
            else:
                count_recursive(child_id)
    
    count_recursive(node_id)
    return tensor_count, total_size


def find_group_node(tree_widget, node_id: str) -> str:
    """
    向上查找到分组节点
    
    Args:
        tree_widget: 树形控件
        node_id: 当前节点ID
        
    Returns:
        分组节点ID，如果未找到返回None
    """
    current_id = node_id
    while current_id:
        item = tree_widget.item(current_id)
        tags = item.get('tags', [])
        if 'group' in tags:
            return current_id
        current_id = tree_widget.parent(current_id)
    return None


def format_size(size_bytes: int) -> str:
    """
    格式化大小显示
    
    Args:
        size_bytes: 字节大小
        
    Returns:
        格式化后的字符串
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"