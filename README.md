# Safetensors Visualization Split & Combine Tool

[中文文档](README_zh.md)

## Introduction

This is a visualization and management tool for large model safetensors files. It provides an intuitive graphical interface that allows users to:

1. **View Structure**: Display the tensor structure inside safetensors files in a tree view
2. **Manual Grouping**: Combine multiple tensors into custom groups as needed
3. **Export Modules**: Export grouped tensors as new safetensors files

## Features

### Core Features
- 📁 Support loading safetensors files and index.json files (both real and test formats)
- 🌳 Tree view visualization of tensor hierarchical structure (with natural sorting)
- 🏷️ Automatic tensor aggregation by prefix
- 📦 User-defined tensor grouping (with tree expansion support)
- 💾 Save and load group configurations
- 📤 Export groups as safetensors format (single export and batch export)
- 🌍 Support Chinese and English interface switching (English by default)

### Interface Features
- 🖥️ Left panel displays the original safetensors structure tree
- 📋 Right panel displays custom group management
- 📊 Nodes display tensor shape and size information
- 🔄 Support node collapse state memory
- 🎨 Support font selection dialog (lazy loading system fonts)
- 📜 Both left and right panels support vertical scrollbars

### Export Features
- **Single Export**: Select a group and export as an independent safetensors file and index.json
- **Batch Export**: Export all groups, each group as a safetensors file, with a total index.json
- Support bfloat16 data type (using PyTorch backend)

## Requirements

- Python 3.8+
- tkinter (usually installed with Python)
- safetensors library
- numpy
- PyTorch (for bfloat16 data export support)

## Installation

1. Clone or download the project
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   Or using uv:
   ```bash
   uv pip install -r requirements.txt
   ```

## Usage

### Launch Application

```bash
python main.py
```

### Basic Operations

1. **Open File**:
   - Click menu "File → Open File" or toolbar "Open File" button
   - Select a safetensors file or corresponding index.json file

2. **View Structure**:
   - Left panel displays the tensor tree structure
   - Leaf nodes display tensor shape and size (e.g., `weight [248320, 2560] (1.2 GB)`)
   - Click a node to view detailed information below

3. **Create Group**:
   - Click menu "Operation → Create Group" or toolbar "Create Group" button
   - Enter group ID, name, and description

4. **Add Tensor to Group**:
   - Select a node in the left tree (supports non-leaf nodes)
   - Select the target group in the right group tree
   - Click "Add to Group" button
   - Groups support tree expansion to view contained tensors

5. **Remove Tensor from Group**:
   - Select the node to remove in the right group tree (supports tensor nodes and non-leaf nodes)
   - Click "Remove from Group" button
   - When deleting a non-leaf node, all descendant tensors under that node will be removed

6. **Export Groups**:
   - **Single Export**: Select a group, click "Export Single Group" button
   - **Batch Export**: Click "Export All Groups" button to export all groups
   - Select export directory, confirm to start export

7. **Switch Interface Language**:
   - Click menu "Language"
   - Select "English" or "中文"
   - Interface will immediately switch to the selected language

8. **Select Font**:
   - Click menu "Font → Select Font"
   - Search and select fonts in the dialog
   - Support filtering by category (Chinese/Monospace/Other)
   - Click "Default" button to restore system default font

## File Structure

```
divide_tool_gui/
├── main.py                    # Main entry file
├── start.py                   # Quick start script
├── requirements.txt           # Dependency list
├── README.md                  # This file (English)
├── README_zh.md               # Chinese documentation
└── src/                       # Source code directory
    ├── __init__.py
    ├── core/                  # Core functionality modules
    │   ├── __init__.py
    │   ├── parser.py          # safetensors parser
    │   ├── tree_builder.py    # Tree builder
    │   ├── group_manager.py   # Group manager
    │   └── exporter.py        # Exporter
    └── gui/                   # GUI modules
        ├── __init__.py
        ├── app.py             # Main application
        ├── dialogs.py         # Dialog components (group creation, font selection)
        ├── language.py        # Language management module
        ├── panels.py          # Panel components (left and right panels)
        └── tree_utils.py      # Tree structure utilities
```

## Notes

- Large safetensors files may take longer to load
- It is recommended to save group configuration before exporting to prevent data loss
- Export functionality requires PyTorch support (for handling bfloat16 data type)

## Troubleshooting

### Chinese Characters Not Displaying

When using `uv` for Python management on Linux, you need to use the system Python to build the venv. The `tk` library downloaded by `uv` cannot call the system's fontconfig, so it only contains the x11 default fallback font `fixed`.

### Export Fails

If export errors occur, please check:
1. Whether PyTorch is installed: `pip install torch`
2. Whether the source file exists and is readable
3. Whether the output directory has write permissions

## License

This project is licensed under the MIT License.
