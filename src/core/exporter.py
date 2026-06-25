"""
导出器
负责将tensor分组导出为safetensors文件
"""

import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
from .parser import TensorInfo, SafetensorsIndex
from .group_manager import TensorGroup

class SafetensorsExporter:
    """safetensors导出器"""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_group(self, group: TensorGroup, tensors: Dict[str, TensorInfo], 
                    source_dir: str, prefix: str = "") -> bool:
        """导出单个分组为safetensors文件"""
        if not group.tensor_names:
            return False
        
        # 准备导出数据
        export_data = {}
        weight_map = {}
        
        for tensor_name in group.tensor_names:
            if tensor_name in tensors:
                tensor_info = tensors[tensor_name]
                # 这里需要实际读取tensor数据
                # 由于我们只有元数据，实际实现需要读取safetensors文件
                weight_map[tensor_name] = f"{prefix}{group.group_id}.safetensors"
        
        # 创建index.json
        index_data = {
            "metadata": {
                "group_id": group.group_id,
                "group_name": group.name,
                "description": group.description,
                "tensor_count": len(group.tensor_names)
            },
            "weight_map": weight_map,
            "tensors": {
                name: {
                    "dtype": tensors[name].dtype,
                    "shape": tensors[name].shape,
                    "data_offsets": tensors[name].data_offsets
                }
                for name in group.tensor_names if name in tensors
            }
        }
        
        # 保存index.json
        index_filename = f"{prefix}{group.group_id}.index.json"
        index_path = self.output_dir / index_filename
        
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
        
        # 创建空的safetensors文件（实际实现需要写入tensor数据）
        safetensors_filename = f"{prefix}{group.group_id}.safetensors"
        safetensors_path = self.output_dir / safetensors_filename
        
        # 这里应该使用safetensors库创建文件
        # 由于示例目的，我们创建一个占位文件
        with open(safetensors_path, 'wb') as f:
            # 写入空的safetensors头
            # 实际实现需要使用safetensors.torch.save_file()或类似方法
            pass
        
        return True
    
    def export_multiple_groups(self, groups: List[TensorGroup], 
                              tensors: Dict[str, TensorInfo],
                              source_dir: str) -> Dict[str, bool]:
        """导出多个分组"""
        results = {}
        for group in groups:
            success = self.export_group(group, tensors, source_dir)
            results[group.group_id] = success
        return results
    
    def create_merged_export(self, groups: List[TensorGroup], 
                           tensors: Dict[str, TensorInfo],
                           output_name: str) -> bool:
        """创建合并导出"""
        # 收集所有tensor
        all_tensors = {}
        for group in groups:
            for tensor_name in group.tensor_names:
                if tensor_name in tensors:
                    all_tensors[tensor_name] = tensors[tensor_name]
        
        if not all_tensors:
            return False
        
        # 创建合并的index
        weight_map = {name: f"{output_name}.safetensors" for name in all_tensors.keys()}
        
        index_data = {
            "metadata": {
                "merged_groups": [g.group_id for g in groups],
                "tensor_count": len(all_tensors)
            },
            "weight_map": weight_map,
            "tensors": {
                name: {
                    "dtype": info.dtype,
                    "shape": info.shape,
                    "data_offsets": info.data_offsets
                }
                for name, info in all_tensors.items()
            }
        }
        
        # 保存合并的index.json
        index_path = self.output_dir / f"{output_name}.index.json"
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
        
        # 创建空的safetensors文件
        safetensors_path = self.output_dir / f"{output_name}.safetensors"
        with open(safetensors_path, 'wb') as f:
            # 实际实现需要写入tensor数据
            pass
        
        return True
    
    def get_export_preview(self, group: TensorGroup, tensors: Dict[str, TensorInfo]) -> Dict[str, Any]:
        """获取导出预览信息"""
        tensor_info_list = []
        total_size = 0
        
        for tensor_name in group.tensor_names:
            if tensor_name in tensors:
                info = tensors[tensor_name]
                tensor_info_list.append({
                    'name': info.name,
                    'dtype': info.dtype,
                    'shape': info.shape,
                    'size_bytes': info.size_bytes
                })
                total_size += info.size_bytes
        
        return {
            'group_id': group.group_id,
            'group_name': group.name,
            'tensor_count': len(tensor_info_list),
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'tensors': tensor_info_list
        }