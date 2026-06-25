#!/usr/bin/env python3
"""
测试核心功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.parser import SafetensorsParser
from src.core.tree_builder import TreeBuilder
from src.core.group_manager import GroupManager

def test_parser():
    """测试解析器"""
    print("测试解析器...")
    
    # 测试加载index.json
    parser = SafetensorsParser("data/test_model.index.json")
    if parser.load():
        print(f"✓ 成功加载文件")
        print(f"  - Tensor数量: {len(parser.get_all_tensor_names())}")
        
        # 测试获取tensor信息
        tensor_name = "model.embeddings.word_embeddings.weight"
        tensor_info = parser.get_tensor_info(tensor_name)
        if tensor_info:
            print(f"✓ 成功获取tensor信息: {tensor_name}")
            print(f"  - 数据类型: {tensor_info.dtype}")
            print(f"  - 形状: {tensor_info.shape}")
            print(f"  - 大小: {tensor_info.size_bytes} 字节")
        
        # 测试前缀分组
        groups = parser.index.get_tensor_groups_by_prefix()
        print(f"✓ 前缀分组数量: {len(groups)}")
        for prefix, tensors in list(groups.items())[:3]:
            print(f"  - {prefix}: {len(tensors)} 个tensor")
    else:
        print("✗ 加载文件失败")

def test_tree_builder():
    """测试树状图构建器"""
    print("\n测试树状图构建器...")
    
    parser = SafetensorsParser("data/test_model.index.json")
    if parser.load():
        tree_builder = TreeBuilder()
        root = tree_builder.build_from_tensors(parser.index.tensors)
        
        print(f"✓ 成功构建树状结构")
        print(f"  - 根节点tensor数量: {root.tensor_count}")
        print(f"  - 根节点总大小: {root.total_size} 字节")
        
        # 测试查找节点
        node = tree_builder.find_node_by_path("model.encoder.layer.0")
        if node:
            print(f"✓ 成功查找节点: model.encoder.layer.0")
            print(f"  - 节点tensor数量: {node.tensor_count}")
        
        # 获取所有节点
        all_nodes = tree_builder.get_all_nodes()
        print(f"✓ 总节点数量: {len(all_nodes)}")

def test_group_manager():
    """测试分组管理器"""
    print("\n测试分组管理器...")
    
    group_manager = GroupManager()
    
    # 创建分组
    group1 = group_manager.create_group("embeddings", "嵌入层", "词嵌入和位置嵌入")
    group2 = group_manager.create_group("layer0", "第0层", "第一层编码器")
    
    print(f"✓ 成功创建分组: {group1.name}, {group2.name}")
    
    # 添加tensor到分组
    group_manager.add_tensor_to_group("embeddings", "model.embeddings.word_embeddings.weight")
    group_manager.add_tensor_to_group("embeddings", "model.embeddings.position_embeddings.weight")
    group_manager.add_tensor_to_group("layer0", "model.encoder.layer.0.attention.self.query.weight")
    
    print(f"✓ 成功添加tensor到分组")
    
    # 测试获取分组tensor
    embeddings_tensors = group_manager.get_group_tensors("embeddings")
    print(f"✓ 嵌入层分组tensor数量: {len(embeddings_tensors)}")
    
    # 测试保存和加载
    group_manager.save_to_file("test_groups.json")
    print(f"✓ 成功保存分组到文件")
    
    # 重新加载
    new_manager = GroupManager()
    if new_manager.load_from_file("test_groups.json"):
        print(f"✓ 成功加载分组文件")
        print(f"  - 分组数量: {len(new_manager.get_all_groups())}")

def main():
    """主测试函数"""
    print("开始测试核心功能...\n")
    
    test_parser()
    test_tree_builder()
    test_group_manager()
    
    print("\n测试完成!")

if __name__ == "__main__":
    main()