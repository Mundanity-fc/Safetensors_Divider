"""
safetensors文件解析器
负责读取index.json文件并解析tensor信息
支持两种index.json格式：
1. 包含tensors字段的完整格式（含dtype、shape、data_offsets）
2. 仅包含weight_map的真实格式（tensor元数据从safetensors文件中读取）
"""

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class TensorInfo:
    """tensor信息数据类"""
    name: str
    dtype: str
    shape: List[int]
    data_offsets: List[int] = None
    file_name: Optional[str] = None
    
    def __post_init__(self):
        if self.data_offsets is None:
            self.data_offsets = [0, 0]
    
    @property
    def size_bytes(self) -> int:
        """计算tensor大小（字节）"""
        # 根据dtype计算字节数
        dtype_sizes = {
            "F32": 4, "F16": 2, "BF16": 2,
            "I64": 8, "I32": 4, "I16": 2, "I8": 1,
            "U8": 1, "BOOL": 1
        }
        element_size = dtype_sizes.get(self.dtype, 4)
        total_elements = 1
        for dim in self.shape:
            total_elements *= dim
        return total_elements * element_size

@dataclass
class SafetensorsIndex:
    """safetensors索引信息"""
    metadata: Dict[str, Any]
    tensors: Dict[str, TensorInfo]
    weight_map: Dict[str, str]  # tensor_name -> file_name
    
    @classmethod
    def from_json(cls, json_path: str, source_dir: Optional[str] = None) -> 'SafetensorsIndex':
        """从index.json文件加载索引
        
        Args:
            json_path: index.json文件路径
            source_dir: safetensors文件所在目录，当index.json中没有tensors字段时需要
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        metadata = data.get('metadata', {})
        weight_map = data.get('weight_map', {})
        
        tensors = {}
        if 'tensors' in data:
            # 完整格式：直接从json中读取tensor信息
            for tensor_name, tensor_data in data['tensors'].items():
                tensor_info = TensorInfo(
                    name=tensor_name,
                    dtype=tensor_data.get('dtype', 'F32'),
                    shape=tensor_data.get('shape', []),
                    data_offsets=tensor_data.get('data_offsets', [0, 0]),
                    file_name=weight_map.get(tensor_name)
                )
                tensors[tensor_name] = tensor_info
        elif weight_map:
            # 真实格式：从safetensors文件中读取tensor元数据
            if source_dir is None:
                source_dir = str(Path(json_path).parent)
            tensors = cls._load_tensors_from_safetensors(weight_map, source_dir)
        
        return cls(
            metadata=metadata,
            tensors=tensors,
            weight_map=weight_map
        )
    
    @staticmethod
    def _load_tensors_from_safetensors(weight_map: Dict[str, str], source_dir: str) -> Dict[str, TensorInfo]:
        """从safetensors文件中加载tensor元数据
        
        Args:
            weight_map: tensor名称到文件名的映射
            source_dir: safetensors文件所在目录
        """
        from safetensors import safe_open
        
        tensors = {}
        # 按文件分组，避免重复打开同一文件
        file_to_tensors: Dict[str, List[str]] = {}
        for tensor_name, file_name in weight_map.items():
            if file_name not in file_to_tensors:
                file_to_tensors[file_name] = []
            file_to_tensors[file_name].append(tensor_name)
        
        for file_name, tensor_names in file_to_tensors.items():
            file_path = os.path.join(source_dir, file_name)
            if not os.path.exists(file_path):
                print(f"警告: safetensors文件不存在: {file_path}")
                # 创建占位tensor信息
                for tensor_name in tensor_names:
                    tensors[tensor_name] = TensorInfo(
                        name=tensor_name,
                        dtype='unknown',
                        shape=[],
                        data_offsets=[0, 0],
                        file_name=file_name
                    )
                continue
            
            try:
                with safe_open(file_path, framework='numpy') as f:
                    for tensor_name in tensor_names:
                        try:
                            slice_obj = f.get_slice(tensor_name)
                            shape = slice_obj.get_shape()
                            dtype = str(slice_obj.get_dtype())
                            tensors[tensor_name] = TensorInfo(
                                name=tensor_name,
                                dtype=dtype,
                                shape=shape,
                                data_offsets=[0, 0],
                                file_name=file_name
                            )
                        except Exception as e:
                            print(f"警告: 无法读取tensor '{tensor_name}' 的元数据: {e}")
                            tensors[tensor_name] = TensorInfo(
                                name=tensor_name,
                                dtype='unknown',
                                shape=[],
                                data_offsets=[0, 0],
                                file_name=file_name
                            )
            except Exception as e:
                print(f"警告: 无法打开safetensors文件 '{file_path}': {e}")
                for tensor_name in tensor_names:
                    tensors[tensor_name] = TensorInfo(
                        name=tensor_name,
                        dtype='unknown',
                        shape=[],
                        data_offsets=[0, 0],
                        file_name=file_name
                    )
        
        return tensors
    
    def get_tensor_groups_by_prefix(self, separator: str = '.') -> Dict[str, List[str]]:
        """根据前缀对tensor进行分组"""
        groups = {}
        for tensor_name in self.tensors.keys():
            parts = tensor_name.split(separator)
            if len(parts) > 1:
                prefix = separator.join(parts[:-1])
                if prefix not in groups:
                    groups[prefix] = []
                groups[prefix].append(tensor_name)
            else:
                # 没有前缀的tensor
                if '' not in groups:
                    groups[''] = []
                groups[''].append(tensor_name)
        return groups
    
    def get_file_mapping(self) -> Dict[str, List[str]]:
        """获取文件到tensor的映射"""
        file_mapping = {}
        for tensor_name, file_name in self.weight_map.items():
            if file_name not in file_mapping:
                file_mapping[file_name] = []
            file_mapping[file_name].append(tensor_name)
        return file_mapping

class SafetensorsParser:
    """safetensors解析器主类"""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.index: Optional[SafetensorsIndex] = None
        
    def load(self) -> bool:
        """加载safetensors文件或index.json"""
        if not self.file_path.exists():
            return False
        
        if self.file_path.suffix == '.json':
            # 直接加载index.json
            try:
                source_dir = str(self.file_path.parent)
                self.index = SafetensorsIndex.from_json(str(self.file_path), source_dir)
                return True
            except Exception as e:
                print(f"加载index.json失败: {e}")
                return False
        elif self.file_path.suffix == '.safetensors':
            # 查找对应的index.json
            index_path = self.file_path.with_suffix('.safetensors.index.json')
            if not index_path.exists():
                # 尝试查找其他index文件
                parent_dir = self.file_path.parent
                possible_indexes = list(parent_dir.glob('*.index.json'))
                if possible_indexes:
                    index_path = possible_indexes[0]
                else:
                    print("未找到index.json文件")
                    return False
            
            try:
                source_dir = str(index_path.parent)
                self.index = SafetensorsIndex.from_json(str(index_path), source_dir)
                return True
            except Exception as e:
                print(f"加载index.json失败: {e}")
                return False
        
        return False
    
    def get_tensor_tree(self) -> Dict[str, Any]:
        """构建tensor树状结构"""
        if not self.index:
            return {}
        
        tree = {}
        for tensor_name, tensor_info in self.index.tensors.items():
            parts = tensor_name.split('.')
            current = tree
            
            # 构建树状路径
            for i, part in enumerate(parts[:-1]):
                if part not in current:
                    current[part] = {'__tensors__': [], '__children__': {}}
                current = current[part]['__children__']
            
            # 添加tensor信息
            leaf_name = parts[-1] if parts else tensor_name
            if leaf_name not in current:
                current[leaf_name] = {'__tensors__': [], '__children__': {}}
            current[leaf_name]['__tensors__'].append(tensor_info)
        
        return tree
    
    def get_tensor_info(self, tensor_name: str) -> Optional[TensorInfo]:
        """获取指定tensor的信息"""
        if not self.index:
            return None
        return self.index.tensors.get(tensor_name)
    
    def get_all_tensor_names(self) -> List[str]:
        """获取所有tensor名称"""
        if not self.index:
            return []
        return list(self.index.tensors.keys())
    
    def get_tensors_by_prefix(self, prefix: str) -> List[TensorInfo]:
        """获取指定前缀的所有tensor"""
        if not self.index:
            return []
        
        result = []
        for tensor_name, tensor_info in self.index.tensors.items():
            if tensor_name.startswith(prefix):
                result.append(tensor_info)
        return result