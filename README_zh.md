# Safetensors 可视化分割与组合工具

[English Documentation](README.md)

## 项目简介

这是一个用于大模型safetensors文件的可视化管理和分割工具。它提供了直观的图形界面，让用户能够：

1. **查看结构**：以树状图形式展示safetensors文件内部的tensor结构
2. **手动分组**：根据需要将多个tensor组合成自定义分组
3. **导出模块**：将分组后的tensor导出为新的safetensors文件

## 截图

![ZH_Screenshot](/screenshot/screenshot_zh.png)

## 功能特性

### 核心功能
- 📁 支持加载safetensors文件和index.json文件（支持真实格式和测试格式）
- 🌳 树状图可视化展示tensor层级结构（支持自然排序）
- 🏷️ 按前缀自动聚合tensor
- 📦 用户自定义tensor分组（支持树形展开）
- 📤 将分组导出为safetensors格式（支持单独导出和整体导出）
- 🌍 支持中英文界面切换（默认英文）

### 导出功能
- **单独导出**：选中一个分组，导出为独立的safetensors文件和index.json
- **整体导出**：导出所有分组，每个分组一个safetensors文件，一个总的index.json
- 支持bfloat16数据类型（使用PyTorch后端）

## 安装要求

- Python 3.8+
- tkinter
- safetensors库
- numpy
- PyTorch

## 安装步骤

1. 克隆或下载项目
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
   或使用uv：
   ```bash
   uv pip install -r requirements.txt
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
   - 叶子节点显示tensor的shape和大小（如 `weight [248320, 2560] (1.2 GB)`）
   - 点击节点可在下方查看详细信息

3. **创建分组**：
   - 点击菜单"操作 → 创建分组"或工具栏"创建分组"按钮
   - 输入分组ID、名称和描述

4. **添加tensor到分组**：
   - 在左侧树状图中选择节点（支持选择非叶节点）
   - 在右侧分组树中选择目标分组
   - 点击"添加到分组"按钮
   - 分组支持树形展开，可查看包含的tensor

5. **从分组移除tensor**：
   - 在右侧分组树中选择要移除的节点（支持tensor节点和非叶节点）
   - 点击"从分组移除"按钮
   - 删除非叶节点时，该节点下的所有子孙tensor都会被移除

6. **导出分组**：
   - **单独导出**：选中一个分组，点击"导出单个分组"按钮
   - **整体导出**：点击"导出所有分组"按钮，导出所有分组
   - 选择导出目录，确认后开始导出

7. **切换界面语言**：
   - 点击菜单"Language"（或"语言"）
   - 选择"English"或"中文"
   - 界面将立即切换到所选语言

8. **选择字体**：
   - 点击菜单"字体 → 选择字体"
   - 在弹出的对话框中搜索和选择字体
   - 支持按分类筛选（中文/等宽/其他）
   - 点击"默认"按钮恢复系统默认字体

## 文件结构

```
root/
├── main.py                    # 主入口文件
├── requirements.txt           # 依赖列表
├── README.md                  # 本说明文件
└── src/                       # 源代码目录
    ├── __init__.py
    ├── core/                  # 核心功能模块
    │   ├── __init__.py
    │   ├── parser.py          # safetensors解析器
    │   ├── tree_builder.py    # 树状图构建器
    │   ├── group_manager.py   # 分组管理器
    │   └── exporter.py        # 导出器
    └── gui/                   # GUI模块
        ├── __init__.py
        ├── app.py             # 主应用程序
        ├── dialogs.py         # 对话框组件（分组创建、字体选择）
        ├── language.py        # 语言管理模块
        ├── panels.py          # 面板组件（左右侧面板）
        └── tree_utils.py      # 树形结构工具

```

## 注意事项

- 大型safetensors文件可能需要较长的加载时间
- 建议在导出前保存分组配置，以防数据丢失
- 导出功能需要PyTorch支持（用于处理bfloat16数据类型）

## 故障排除

### 中文无法显示

在 Linux 下使用 `uv` 进行 Python 管理时，需要使用系统 Python 来构建 venv,由 `uv` 下载得到的 Python 附带的 `tk` 库无法调用系统的 fontconfig,因此只包含 x11 的默认 fallback 字体 `fixed`

### 导出失败

如果导出时出现错误，请检查：
1. 是否已安装PyTorch：`pip install torch`
2. 源文件是否存在且可读
3. 输出目录是否有写入权限

## 许可证

遵循 MIT 许可证。