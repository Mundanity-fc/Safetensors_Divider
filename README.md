# Safetensors 可视化分割与组合工具

## 项目简介

这是一个用于大模型safetensors文件的可视化管理和分割工具。它提供了直观的图形界面，让用户能够：

1. **查看结构**：以树状图形式展示safetensors文件内部的tensor结构
2. **手动分组**：根据需要将多个tensor组合成自定义分组
3. **导出模块**：将分组后的tensor导出为新的safetensors文件

## 功能特性

- 📁 支持加载safetensors文件和index.json文件
- 🌳 树状图可视化展示tensor层级结构
- 🏷️ 按前缀自动聚合tensor
- 📦 用户自定义tensor分组（支持树形展开）
- 💾 分组配置的保存和加载
- 📤 将分组导出为safetensors格式
- 🌍 支持中英文界面切换（默认英文）

## 安装要求

- Python 3.8+
- tkinter（通常随Python一起安装）
- safetensors库
- numpy
- 中文字体（如思源黑体、文泉驿微米黑等）

## 安装步骤

1. 克隆或下载项目
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 使用方法

### 启动应用程序

```bash
python main.py
```

### 基本操作

1. **打开文件**：
   - 点击菜单"文件 → 打开文件"或工具栏"打开文件"按钮
   - 选择safetensors文件或对应的index.json文件

2. **查看结构**：
   - 左侧面板显示tensor的树状结构
   - 点击节点可在下方查看详细信息

3. **创建分组**：
   - 点击菜单"操作 → 创建分组"或工具栏"创建分组"按钮
   - 输入分组ID、名称和描述

4. **添加tensor到分组**：
   - 在左侧树状图中选择节点
   - 在右侧分组树中选择目标分组
   - 点击"添加到分组"按钮
   - 分组支持树形展开，可查看包含的tensor

5. **从分组移除tensor**：
   - 在右侧分组树中选择要移除的tensor
   - 点击"从分组移除"按钮

5. **导出分组**：
   - 点击菜单"操作 → 导出分组"或工具栏"导出"按钮
   - 选择导出目录

6. **保存/加载分组配置**：
   - 使用"文件 → 保存分组"保存当前分组配置
   - 使用"文件 → 加载分组"加载之前的分组配置

7. **切换界面语言**：
   - 点击菜单"Language"（或"语言"）
   - 选择"English"或"中文"
   - 界面将立即切换到所选语言

## 文件结构

```
divide_tool_gui/
├── main.py                 # 主入口文件
├── start.py               # 快速启动脚本
├── requirements.txt        # 依赖列表
├── README.md              # 本说明文件
├── data/                  # 测试数据目录
│   └── test_model.index.json
├── src/                   # 源代码目录
│   ├── __init__.py
│   ├── core/              # 核心功能模块
│   │   ├── __init__.py
│   │   ├── parser.py      # safetensors解析器
│   │   ├── tree_builder.py # 树状图构建器
│   │   ├── group_manager.py # 分组管理器
│   │   └── exporter.py    # 导出器
│   └── gui/               # GUI模块
│       ├── __init__.py
│       ├── app.py         # 主应用程序
│       └── language.py    # 语言管理模块
└── tests/                 # 测试文件
    ├── test_core.py       # 核心功能测试
    └── test_language.py   # 语言功能测试
```

## 测试

运行核心功能测试：
```bash
python tests/test_core.py
```

运行语言功能测试：
```bash
python tests/test_language.py
```

## 示例数据

项目包含一个示例index.json文件（`data/test_model.index.json`），用于测试和演示功能。

## 注意事项

- 当前版本的导出功能仅创建占位文件，实际tensor数据写入需要进一步实现
- 大型safetensors文件可能需要较长的加载时间
- 建议在导出前保存分组配置，以防数据丢失

## 故障排除

### 中文无法显示

如果界面中的中文无法显示，请尝试以下解决方案：

1. **安装中文字体**：
   ```bash
   # Ubuntu/Debian
   sudo apt-get install fonts-noto-cjk fonts-wqy-microhei
   
   # CentOS/RHEL
   sudo yum install google-noto-sans-cjk-fonts wqy-microhei-fonts
   ```

2. **检查系统字体**：
   ```bash
   fc-list :lang=zh
   ```

3. **更新字体缓存**：
   ```bash
   sudo fc-cache -fv
   ```

4. **重启应用程序**：安装字体后，需要重启应用程序才能生效。

### tkinter字体问题

如果遇到tkinter字体相关问题，可以尝试：

1. **检查tkinter版本**：
   ```python
   import tkinter
   print(tkinter.TkVersion)
   ```

2. **使用系统字体**：应用程序会自动尝试使用系统中可用的中文字体，包括：
   - Source Han Sans SC (思源黑体)
   - Noto Sans CJK SC
   - WenQuanYi Micro Hei (文泉驿微米黑)
   - Microsoft YaHei (微软雅黑)
   - SimHei (黑体)
   - SimSun (宋体)

## 开发计划

- [ ] 实现完整的tensor数据读取和写入
- [ ] 添加拖放支持
- [ ] 实现分组的重命名和编辑
- [ ] 添加批量操作功能
- [ ] 支持多种导出格式
- [ ] 添加撤销/重做功能
- [ ] 优化大型文件的加载性能

## 许可证

本项目仅供学习和研究使用。