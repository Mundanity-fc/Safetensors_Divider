# 可视化大模型 safetensors 内部结构分割与组合工具

## 项目描述

本项目旨在为大模型的 safetensors 再分割提供一个可视化的操作工具，实现对 safetensors 内部的各 tensor 结构的展示（通过`index.json`文件）、默认聚合（通过`index.json`文件，按照共有前缀名称进行树状图合并）、手动分组（按照用户自定义的分组对多个 tensor 进行组合）、组合保存（对默认或者用户自定义后的组合 tensor 模块进行 safetensors 导出）

## 项目功能

- 结构展示：按照树状图形式展示 safetensors 内的各 tensor 的父子关系
- 手动分组：用户根据自身需求将多个 tensor 聚类合并成一个模块
- 模块导出：将合并后的模块导出为 safetensors