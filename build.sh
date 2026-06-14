#!/bin/bash
# 万能文件转换工具 - Linux/Mac 打包脚本

set -e
echo "========================================"
echo "  万能文件转换工具 - 打包脚本"
echo "========================================"
echo

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3"
    exit 1
fi

# 安装依赖
echo "📦 安装依赖..."
pip3 install -r requirements.txt
pip3 install pyinstaller

echo
echo "🔨 开始打包..."
pyinstaller --onefile --windowed \
    --name "file-converter" \
    --add-data "converter:converter" \
    --noconfirm \
    --clean \
    gui.py

echo
if [ -f "dist/file-converter" ]; then
    echo "✅ 打包成功！"
    echo "📄 输出文件: dist/file-converter"
else
    echo "❌ 打包失败"
fi
