#!/usr/bin/env python3
"""
File Converter - 万能文件转换工具

支持的转换:
  pdf2img    PDF 转图片
  img2pdf    图片转 PDF
  pdf2word   PDF 转 Word
  word2pdf   Word 转 PDF
  mergepdf   合并多个 PDF
  splitpdf   拆分 PDF
  imgconv    图片格式互转 (png/jpg/webp/bmp)
  xls2csv    Excel 转 CSV
  csv2xls    CSV 转 Excel

用法:
  python convert.py <command> <input> [output] [options]

示例:
  python convert.py pdf2img document.pdf ./pages/
  python convert.py img2pdf photo1.jpg photo2.png -o output.pdf
  python convert.py imgconv image.png result.webp --quality 80
  python convert.py mergepdf a.pdf b.pdf -o merged.pdf
  python convert.py splitpdf document.pdf ./pages/ --pages 1,3,5-7
  python convert.py word2pdf report.docx report.pdf
  python convert.py xls2csv data.xlsx data.csv
"""

import argparse
import sys
from pathlib import Path


def cmd_pdf2img(args):
    from converter.pdf_converter import pdf_to_images
    out_dir = args.output or str(Path(args.input).stem + "_pages")
    result = pdf_to_images(args.input, out_dir, fmt=args.format, dpi=args.dpi)
    print(f"✅ PDF → {len(result)} 张图片")
    for p in result:
        print(f"   📄 {p}")


def cmd_img2pdf(args):
    from converter.image_converter import images_to_pdf
    output = args.output or "output.pdf"
    result = images_to_pdf(args.input, output)
    print(f"✅ {len(args.input)} 张图片 → PDF")
    print(f"   📄 {result}")


def cmd_pdf2word(args):
    from converter.pdf_converter import pdf_to_images
    output = args.output or str(Path(args.input).stem) + "_text.txt"
    # PDF → Word 的最佳方案是 OCR，这里提供文本提取
    # 实际项目中建议集成 tesseract 或 paddleocr
    print("⚠️  PDF → Word 建议使用 OCR 工具获得最佳效果")
    print("   当前提供文本提取模式，复杂排版可能丢失格式")
    from pypdf import PdfReader
    reader = PdfReader(args.input)
    text = "\n\n".join(page.extract_text() or "" for page in reader.pages)
    Path(output).write_text(text, encoding="utf-8")
    print(f"✅ 文本已提取到 {output}")


def cmd_word2pdf(args):
    from converter.word_converter import word_to_pdf
    output = args.output or str(Path(args.input).stem) + ".pdf"
    result = word_to_pdf(args.input, output)
    print(f"✅ Word → PDF")
    print(f"   📄 {result}")


def cmd_mergepdf(args):
    from converter.pdf_converter import merge_pdfs
    output = args.output or "merged.pdf"
    result = merge_pdfs(args.input, output)
    print(f"✅ 合并 {len(args.input)} 个 PDF")
    print(f"   📄 {result}")


def cmd_splitpdf(args):
    from converter.pdf_converter import split_pdf
    out_dir = args.output or str(Path(args.input).stem) + "_split"
    result = split_pdf(args.input, out_dir, pages=args.pages)
    print(f"✅ 拆分为 {len(result)} 个 PDF")
    for p in result:
        print(f"   📄 {p}")


def cmd_imgconv(args):
    from converter.image_converter import convert_image
    output = args.output
    if not output:
        src = Path(args.input)
        output = str(src.parent / f"{src.stem}_converted.{args.format}")
    result = convert_image(args.input, output, quality=args.quality)
    print(f"✅ 图片格式转换完成")
    print(f"   📄 {result}")


def cmd_xls2csv(args):
    from converter.excel_converter import excel_to_csv
    output = args.output or str(Path(args.input).stem) + ".csv"
    result = excel_to_csv(args.input, output, sheet_name=args.sheet)
    print(f"✅ Excel → CSV")
    print(f"   📄 {result}")


def cmd_csv2xls(args):
    from converter.excel_converter import csv_to_excel
    output = args.output or str(Path(args.input).stem) + ".xlsx"
    result = csv_to_excel(args.input, output)
    print(f"✅ CSV → Excel")
    print(f"   📄 {result}")


def main():
    parser = argparse.ArgumentParser(
        description="🔄 File Converter - 万能文件转换工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    subparsers = parser.add_subparsers(dest="command", help="转换命令")

    # pdf2img
    p = subparsers.add_parser("pdf2img", help="PDF 转图片")
    p.add_argument("input", help="输入 PDF 文件")
    p.add_argument("output", nargs="?", help="输出目录")
    p.add_argument("--format", default="png", choices=["png", "jpg"], help="图片格式")
    p.add_argument("--dpi", type=int, default=200, help="分辨率 DPI")
    p.set_defaults(func=cmd_pdf2img)

    # img2pdf
    p = subparsers.add_parser("img2pdf", help="图片转 PDF")
    p.add_argument("input", nargs="+", help="输入图片文件（可多个）")
    p.add_argument("-o", "--output", help="输出 PDF 文件")
    p.set_defaults(func=cmd_img2pdf)

    # pdf2word
    p = subparsers.add_parser("pdf2word", help="PDF 转 Word（文本提取）")
    p.add_argument("input", help="输入 PDF 文件")
    p.add_argument("output", nargs="?", help="输出文件")
    p.set_defaults(func=cmd_pdf2word)

    # word2pdf
    p = subparsers.add_parser("word2pdf", help="Word 转 PDF")
    p.add_argument("input", help="输入 .docx 文件")
    p.add_argument("output", nargs="?", help="输出 PDF 文件")
    p.set_defaults(func=cmd_word2pdf)

    # mergepdf
    p = subparsers.add_parser("mergepdf", help="合并多个 PDF")
    p.add_argument("input", nargs="+", help="输入 PDF 文件")
    p.add_argument("-o", "--output", help="输出 PDF 文件")
    p.set_defaults(func=cmd_mergepdf)

    # splitpdf
    p = subparsers.add_parser("splitpdf", help="拆分 PDF")
    p.add_argument("input", help="输入 PDF 文件")
    p.add_argument("output", nargs="?", help="输出目录")
    p.add_argument("--pages", help="页码范围，如 1,3,5-7")
    p.set_defaults(func=cmd_splitpdf)

    # imgconv
    p = subparsers.add_parser("imgconv", help="图片格式互转")
    p.add_argument("input", help="输入图片文件")
    p.add_argument("output", nargs="?", help="输出图片文件")
    p.add_argument("--format", default="png", choices=["png", "jpg", "jpeg", "webp", "bmp", "tiff"], help="目标格式")
    p.add_argument("--quality", type=int, default=95, help="质量 (1-100)")
    p.set_defaults(func=cmd_imgconv)

    # xls2csv
    p = subparsers.add_parser("xls2csv", help="Excel 转 CSV")
    p.add_argument("input", help="输入 .xlsx 文件")
    p.add_argument("output", nargs="?", help="输出 .csv 文件")
    p.add_argument("--sheet", help="工作表名称")
    p.set_defaults(func=cmd_xls2csv)

    # csv2xls
    p = subparsers.add_parser("csv2xls", help="CSV 转 Excel")
    p.add_argument("input", help="输入 .csv 文件")
    p.add_argument("output", nargs="?", help="输出 .xlsx 文件")
    p.set_defaults(func=cmd_csv2xls)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        args.func(args)
    except FileNotFoundError as e:
        print(f"❌ 文件不存在: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 转换失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
