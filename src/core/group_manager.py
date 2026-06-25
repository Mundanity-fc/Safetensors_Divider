"""
分组管理器
负责管理用户自定义的tensor分组
"""

import json
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path
from .parser import TensorInfo

@dataclass
class TensorGroup:
    """tensor分组"""
    group_id: str
    name: str
    description: str = ""
    tensor_names: List[str] = field(default_factory=list)
    
    def add_tensor(self, tensor_name: str):
        """添加tensor到分组"""
        if tensor_name not in self.tensor_names:
            self.tensor_names.append(tensor_name)
    
    def remove_tensor(self, tensor_name: str):
        """从分组中移除tensor"""
        if tensor_name in self.tensor_names:
            self.tensor_names.remove(tensor_name)
    
    def contains_tensor(self, tensor_name: str) -> bool:
        """检查分组是否包含指定tensor"""
        return tensor_name in self.tensor_names
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'group_id': self.group_id,
            'name': self.name,
            'description': self.description,
            'tensor_names': self.tensor_names
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TensorGroup':
        """从字典创建分组"""
        return cls(
            group_id=data.get('group_id', ''),
            name=data.get('name', ''),
            description=data.get('description', ''),
            tensor_names=data.get('tensor_names', [])
        )

class GroupManager:
    """分组管理器"""
    
    def __init__(self):
        self.groups: Dict[str, TensorGroup] = {}
        self.tensor_to_groups: Dict[str, Set[str]] = {}  # tensor_name -> set of group_ids
    
    def create_group(self, group_id: str, name: str, description: str = "") -> TensorGroup:
        """创建新分组"""
        if group_id in self.groups:
            raise ValueError(f"分组ID '{group_id}' 已存在")
        
        group = TensorGroup(
            group_id=group_id,
            name=name,
            description=description
        )
        self.groups[group_id] = group
        return group
    
    def delete_group(self, group_id: str) -> bool:
        """删除分组"""
        if group_id not in self.groups:
            return False
        
        group = self.groups[group_id]
        
        # 从tensor_to_groups映射中移除
        for tensor_name in group.tensor_names:
            if tensor_name in self.tensor_to_groups:
                self.tensor_to_groups[tensor_name].discard(group_id)
                if not self.tensor_to_groups[tensor_name]:
                    del self.tensor_to_groups[tensor_name]
        
        del self.groups[group_id]
        return True
    
    def add_tensor_to_group(self, group_id: str, tensor_name: str) -> bool:
        """将tensor添加到分组"""
        if group_id not in self.groups:
            return False
        
        group = self.groups[group_id]
        group.add_tensor(tensor_name)
        
        # 更新tensor_to_groups映射
        if tensor_name not in self.tensor_to_groups:
            self.tensor_to_groups[tensor_name] = set()
        self.tensor_to_groups[tensor_name].add(group_id)
        
        return True
    
    def remove_tensor_from_group(self, group_id: str, tensor_name: str) -> bool:
        """从分组中移除tensor"""
        if group_id not in self.groups:
            return False
        
        group = self.groups[group_id]
        group.remove_tensor(tensor_name)
        
        # 更新tensor_to_groups映射
        if tensor_name in self.tensor_to_groups:
            self.tensor_to_groups[tensor_name].discard(group_id)
            if not self.tensor_to_groups[tensor_name]:
                del self.tensor_to_groups[tensor_name]
        
        return True
    
    def get_tensor_groups(self, tensor_name: str) -> List[TensorGroup]:
        """获取包含指定tensor的所有分组"""
        if tensor_name not in self.tensor_to_groups:
            return []
        
        group_ids = self.tensor_to_groups[tensor_name]
        return [self.groups[gid] for gid in group_ids if gid in self.groups]
    
    def get_group_tensors(self, group_id: str) -> List[str]:
        """获取分组中的所有tensor名称"""
        if group_id not in self.groups:
            return []
        return self.groups[group_id].tensor_names.copy()
    
    def get_all_groups(self) -> List[TensorGroup]:
        """获取所有分组"""
        return list(self.groups.values())
    
    def get_ungrouped_tensors(self, all_tensor_names: List[str]) -> List[str]:
        """获取未分组的tensor"""
        grouped_tensors = set()
        for group in self.groups.values():
            grouped_tensors.update(group.tensor_names)
        
        return [name for name in all_tensor_names if name not in grouped_tensors]
    
    def save_to_file(self, file_path: str):
        """保存分组到文件"""
        data = {
            'groups': [group.to_dict() for group in self.groups.values()]
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_from_file(self, file_path: str) -> bool:
        """从文件加载分组"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 清空现有数据
            self.groups.clear()
            self.tensor_to_groups.clear()
            
            # 加载分组
            for group_data in data.get('groups', []):
                group = TensorGroup.from_dict(group_data)
                self.groups[group.group_id] = group
                
                # 更新tensor_to_groups映射
                for tensor_name in group.tensor_names:
                    if tensor_name not in self.tensor_to_groups:
                        self.tensor_to_groups[tensor_name] = set()
                    self.tensor_to_groups[tensor_name].add(group.group_id)
            
            return True
        except Exception as e:
            print(f"加载分组文件失败: {e}")
            return False
    
    def merge_groups(self, group_ids: List[str], new_group_id: str, new_name: str) -> Optional[TensorGroup]:
        """合并多个分组"""
        # 收集所有tensor
        all_tensors = set()
        for group_id in group_ids:
            if group_id in self.groups:
                all_tensors.update(self.groups[group_id].tensor_names)
        
        # 创建新分组
        new_group = self.create_group(new_group_id, new_name)
        for tensor_name in all_tensors:
            self.add_tensor_to_group(new_group_id, tensor_name)
        
        # 删除原分组
        for group_id in group_ids:
            self.delete_group(group_id)
        
        return new_group