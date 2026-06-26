"""
导出器
负责将tensor分组导出为safetensors文件
支持两种导出模式：
1. 单独导出：导出单个分组
2. 整体导出：导出所有分组
"""

import json
import os
import torch
from typing import Dict, List, Any, Optional
from pathlib import Path
from safetensors.torch import save_file, load_file
from .parser import TensorInfo
from .group_manager import TensorGroup


class SafetensorsExporter:
    """safetensors导出器"""
    
    def __init__(self, output_dir: str, source_dir: str):
        """
        初始化导出器
        
        Args:
            output_dir: 输出目录
            source_dir: 源safetensors文件所在目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.source_dir = Path(source_dir)
    
    def export_single_group(self, group: TensorGroup, tensors: Dict[str, TensorInfo],
                           weight_map: Dict[str, str]) -> bool:
        """
        单独导出：导出单个分组为safetensors文件和index.json
        
        Args:
            group: 要导出的分组
            tensors: 所有tensor信息
            weight_map: tensor名称到文件名的映射
            
        Returns:
            是否成功
        """
        if not group.tensor_names:
            return False
        
        # 收集分组中的tensor数据
        tensor_data = {}
        export_weight_map = {}
        
        for tensor_name in group.tensor_names:
            if tensor_name in tensors:
                tensor_info = tensors[tensor_name]
                # 从源文件读取tensor数据
                data = self._read_tensor_data(tensor_name, tensor_info, weight_map)
                if data is not None:
                    tensor_data[tensor_name] = data
                    export_weight_map[tensor_name] = f"{group.name}.safetensors"
        
        if not tensor_data:
            return False
        
        # 保存safetensors文件
        safetensors_path = self.output_dir / f"{group.name}.safetensors"
        try:
            save_file(tensor_data, str(safetensors_path))
        except Exception as e:
            print(f"保存safetensors文件失败: {e}")
            return False
        
        # 创建index.json
        index_data = {
            "metadata": {
                "total_size": sum(tensors[name].size_bytes for name in tensor_data.keys())
            },
            "weight_map": export_weight_map
        }
        
        index_path = self.output_dir / f"{group.name}.index.json"
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
        
        return True
    
    def export_all_groups(self, groups: List[TensorGroup], tensors: Dict[str, TensorInfo],
                         weight_map: Dict[str, str]) -> bool:
        """
        整体导出：导出所有分组，每个分组一个safetensors文件，一个总的index.json
        
        Args:
            groups: 所有分组列表
            tensors: 所有tensor信息
            weight_map: tensor名称到文件名的映射
            
        Returns:
            是否成功
        """
        if not groups:
            return False
        
        all_weight_map = {}
        exported_count = 0
        
        for group in groups:
            if not group.tensor_names:
                continue
            
            # 收集分组中的tensor数据
            tensor_data = {}
            
            for tensor_name in group.tensor_names:
                if tensor_name in tensors:
                    tensor_info = tensors[tensor_name]
                    # 从源文件读取tensor数据
                    data = self._read_tensor_data(tensor_name, tensor_info, weight_map)
                    if data is not None:
                        tensor_data[tensor_name] = data
                        all_weight_map[tensor_name] = f"{group.name}.safetensors"
            
            if not tensor_data:
                continue
            
            # 保存safetensors文件
            safetensors_path = self.output_dir / f"{group.name}.safetensors"
            try:
                save_file(tensor_data, str(safetensors_path))
                exported_count += 1
            except Exception as e:
                print(f"保存safetensors文件 '{group.name}' 失败: {e}")
                continue
        
        if exported_count == 0:
            return False
        
        # 创建总的index.json
        index_data = {
            "metadata": {
                "total_size": sum(
                    tensors[name].size_bytes 
                    for name in all_weight_map.keys() 
                    if name in tensors
                )
            },
            "weight_map": all_weight_map
        }
        
        index_path = self.output_dir / "model.safetensors.index.json"
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
        
        return True
    
    def _read_tensor_data(self, tensor_name: str, tensor_info: TensorInfo,
                         weight_map: Dict[str, str]) -> Optional[torch.Tensor]:
        """
        从源safetensors文件中读取tensor数据
        
        Args:
            tensor_name: tensor名称
            tensor_info: tensor信息
            weight_map: tensor名称到文件名的映射
            
        Returns:
            tensor数据，如果读取失败返回None
        """
        # 获取源文件名
        source_file = weight_map.get(tensor_name)
        if not source_file:
            print(f"警告: 找不到tensor '{tensor_name}' 的源文件")
            return None
        
        source_path = self.source_dir / source_file
        if not source_path.exists():
            print(f"警告: 源文件不存在: {source_path}")
            return None
        
        try:
            # 加载源文件并获取指定tensor
            tensors_in_file = load_file(str(source_path))
            if tensor_name in tensors_in_file:
                return tensors_in_file[tensor_name]
            else:
                print(f"警告: 在文件 '{source_file}' 中找不到tensor '{tensor_name}'")
                return None
        except Exception as e:
            print(f"读取tensor '{tensor_name}' 失败: {e}")
            return None
    
    def get_single_export_preview(self, group: TensorGroup, tensors: Dict[str, TensorInfo]) -> Dict[str, Any]:
        """获取单个分组的导出预览信息"""
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
            'group_name': group.name,
            'tensor_count': len(tensor_info_list),
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'tensors': tensor_info_list,
            'output_files': [
                f"{group.name}.safetensors",
                f"{group.name}.index.json"
            ]
        }
    
    def get_all_export_preview(self, groups: List[TensorGroup], tensors: Dict[str, TensorInfo]) -> Dict[str, Any]:
        """获取整体导出的预览信息"""
        group_previews = []
        total_tensor_count = 0
        total_size = 0
        
        for group in groups:
            if not group.tensor_names:
                continue
            
            group_size = 0
            group_tensor_count = 0
            for tensor_name in group.tensor_names:
                if tensor_name in tensors:
                    group_size += tensors[tensor_name].size_bytes
                    group_tensor_count += 1
            
            group_previews.append({
                'group_name': group.name,
                'tensor_count': group_tensor_count,
                'size_bytes': group_size,
                'size_mb': group_size / (1024 * 1024),
                'output_file': f"{group.name}.safetensors"
            })
            
            total_tensor_count += group_tensor_count
            total_size += group_size
        
        return {
            'group_count': len(group_previews),
            'total_tensor_count': total_tensor_count,
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'groups': group_previews,
            'output_files': [g['output_file'] for g in group_previews] + ["model.safetensors.index.json"]
        }
