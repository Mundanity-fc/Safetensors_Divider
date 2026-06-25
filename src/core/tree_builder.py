"""
树状图构建器
负责将tensor信息转换为树状结构
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from .parser import TensorInfo

@dataclass
class TreeNode:
    """树节点"""
    name: str
    full_path: str
    tensors: List[TensorInfo]
    children: Dict[str, 'TreeNode']
    parent: Optional['TreeNode'] = None
    
    @property
    def is_leaf(self) -> bool:
        """是否为叶子节点"""
        return len(self.children) == 0
    
    @property
    def tensor_count(self) -> int:
        """获取tensor数量（包括子节点）"""
        count = len(self.tensors)
        for child in self.children.values():
            count += child.tensor_count
        return count
    
    @property
    def total_size(self) -> int:
        """获取总大小（字节）"""
        size = sum(t.size_bytes for t in self.tensors)
        for child in self.children.values():
            size += child.total_size
        return size
    
    def add_tensor(self, tensor_info: TensorInfo):
        """添加tensor到节点"""
        self.tensors.append(tensor_info)
    
    def get_child(self, name: str) -> Optional['TreeNode']:
        """获取子节点"""
        return self.children.get(name)
    
    def add_child(self, name: str, node: 'TreeNode'):
        """添加子节点"""
        self.children[name] = node
        node.parent = self
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典表示"""
        return {
            'name': self.name,
            'full_path': self.full_path,
            'tensor_count': self.tensor_count,
            'total_size': self.total_size,
            'is_leaf': self.is_leaf,
            'tensors': [
                {
                    'name': t.name,
                    'dtype': t.dtype,
                    'shape': t.shape,
                    'size_bytes': t.size_bytes
                }
                for t in self.tensors
            ],
            'children': {
                name: child.to_dict()
                for name, child in self.children.items()
            }
        }

class TreeBuilder:
    """树状图构建器"""
    
    def __init__(self, separator: str = '.'):
        self.separator = separator
        self.root = TreeNode(
            name='root',
            full_path='',
            tensors=[],
            children={}
        )
    
    def build_from_tensors(self, tensors: Dict[str, TensorInfo]) -> TreeNode:
        """从tensor字典构建树状结构"""
        self.root = TreeNode(
            name='root',
            full_path='',
            tensors=[],
            children={}
        )
        
        for tensor_name, tensor_info in tensors.items():
            self._add_tensor_to_tree(tensor_name, tensor_info)
        
        return self.root
    
    def _add_tensor_to_tree(self, tensor_name: str, tensor_info: TensorInfo):
        """将tensor添加到树中"""
        parts = tensor_name.split(self.separator)
        current_node = self.root
        current_path = ''
        
        # 遍历路径部分
        for i, part in enumerate(parts[:-1]):
            if current_path:
                current_path += self.separator + part
            else:
                current_path = part
            
            # 获取或创建子节点
            child_node = current_node.get_child(part)
            if child_node is None:
                child_node = TreeNode(
                    name=part,
                    full_path=current_path,
                    tensors=[],
                    children={}
                )
                current_node.add_child(part, child_node)
            
            current_node = child_node
        
        # 添加tensor到叶子节点
        leaf_name = parts[-1] if parts else tensor_name
        leaf_path = tensor_name
        
        leaf_node = current_node.get_child(leaf_name)
        if leaf_node is None:
            leaf_node = TreeNode(
                name=leaf_name,
                full_path=leaf_path,
                tensors=[],
                children={}
            )
            current_node.add_child(leaf_name, leaf_node)
        
        leaf_node.add_tensor(tensor_info)
    
    def get_tree_summary(self) -> Dict[str, Any]:
        """获取树状结构摘要"""
        return {
            'total_tensors': self.root.tensor_count,
            'total_size': self.root.total_size,
            'tree_structure': self.root.to_dict()
        }
    
    def find_node_by_path(self, path: str) -> Optional[TreeNode]:
        """根据路径查找节点"""
        if not path:
            return self.root
        
        parts = path.split(self.separator)
        current_node = self.root
        
        for part in parts:
            child_node = current_node.get_child(part)
            if child_node is None:
                return None
            current_node = child_node
        
        return current_node
    
    def get_all_nodes(self) -> List[TreeNode]:
        """获取所有节点"""
        nodes = []
        self._collect_nodes(self.root, nodes)
        return nodes
    
    def _collect_nodes(self, node: TreeNode, nodes: List[TreeNode]):
        """递归收集节点"""
        nodes.append(node)
        for child in node.children.values():
            self._collect_nodes(child, nodes)