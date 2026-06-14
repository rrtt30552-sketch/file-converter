# 🔄 万能文件转换工具

一个开箱即用的文件格式转换工具，支持 PDF / Word / 图片 / Excel 常见格式互转。

提供 **命令行版** 和 **图形界面版**，图形界面版可打包为 `.exe` 双击即用。

## ✨ 支持的转换

| 转换方向 | 说明 |
|---------|------|
| 图片 → PDF | 多张图片合并为一个 PDF |
| PDF → 图片 | 每页导出为 PNG/JPG |
| 图片格式转换 | PNG / JPG / WEBP / BMP / TIFF 互转 |
| Word → PDF | .docx 转 PDF |
| PDF → 文本 | 提取 PDF 中的文字 |
| 合并 PDF | 多个 PDF 合为一个 |
| 拆分 PDF | 按页码拆分 PDF |
| Excel → CSV | .xlsx 转 .csv |
| CSV → Excel | .csv 转 .xlsx |

## 🚀 使用方式

### 方式一：下载 .exe（推荐，双击即用）

1. 去 [Releases](https://github.com/rrtt30552-sketch/file-converter/releases) 下载最新的 `文件转换工具.exe`
2. 双击运行，无需安装 Python

> 如果没有 Release，参考下方「自己打包」

### 方式二：命令行使用

```bash
# 安装依赖
pip install -r requirements.txt

# 使用
python convert.py pdf2img document.pdf ./pages/
python convert.py img2pdf a.jpg b.png -o out.pdf
python convert.py imgconv photo.png result.webp --quality 80
python convert.py mergepdf a.pdf b.pdf -o merged.pdf
```

### 方式三：自己打包成 .exe

**Windows：**
```bash
# 双击运行 build.bat，或在命令行执行：
build.bat
```

**Linux / Mac：**
```bash
chmod +x build.sh
./build.sh
```

打包完成后，`dist/文件转换工具.exe` 就是独立的可执行文件。

## 📋 系统要求

- Python 3.10+（仅源码运行/打包时需要）
- Windows 7+ / macOS / Linux

## 📁 项目结构

```
file-converter/
├── gui.py                  # 图形界面主程序
├── convert.py              # 命令行主程序
├── converter/              # 转换引擎模块
│   ├── image_converter.py
│   ├── pdf_converter.py
│   ├── word_converter.py
│   └── excel_converter.py
├── file-converter.spec     # PyInstaller 打包配置
├── build.bat               # Windows 打包脚本
├── build.sh                # Linux/Mac 打包脚本
├── requirements.txt
└── README.md
```

## 📝 许可证

MIT License
