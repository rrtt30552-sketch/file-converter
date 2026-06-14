"""
File Converter - 万能文件转换工具 (GUI 版)
"""

import os
import sys
import threading
import traceback
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path


def get_base_dir():
    """Get base dir for bundled resources."""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


# ── 转换函数 ──

def do_images_to_pdf(files, output):
    from PIL import Image
    imgs = []
    for f in files:
        im = Image.open(f)
        if im.mode in ("RGBA", "P", "LA"):
            im = im.convert("RGB")
        imgs.append(im)
    if not imgs:
        raise ValueError("没有图片")
    imgs[0].save(output, "PDF", save_all=True, append_images=imgs[1:], quality=95)


def do_pdf_to_images(pdf_path, out_dir):
    from pdf2image import convert_from_path
    os.makedirs(out_dir, exist_ok=True)
    images = convert_from_path(pdf_path, dpi=200, fmt="png")
    stem = Path(pdf_path).stem
    for i, img in enumerate(images, 1):
        img.save(os.path.join(out_dir, f"{stem}_page{i}.png"))
    return len(images)


def do_image_convert(src, dst):
    from PIL import Image
    im = Image.open(src)
    ext = Path(dst).suffix.lower().lstrip(".")
    if ext in ("jpg", "jpeg") and im.mode in ("RGBA", "P", "LA"):
        im = im.convert("RGB")
    kw = {}
    if ext in ("jpg", "jpeg"):
        kw = {"quality": 95, "optimize": True}
    elif ext == "webp":
        kw = {"quality": 95}
    im.save(dst, **kw)


def do_word_to_pdf(src, dst):
    try:
        import subprocess
        subprocess.run(["libreoffice", "--headless", "--convert-to", "pdf",
                        "--outdir", str(Path(dst).parent), src],
                       capture_output=True, timeout=60)
        gen = Path(dst).parent / f"{Path(src).stem}.pdf"
        if gen.exists() and str(gen) != dst:
            gen.rename(dst)
        return
    except Exception:
        pass
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.units import mm
    from docx import Document as DocxDoc
    doc = DocxDoc(src)
    pdf = SimpleDocTemplate(dst, pagesize=A4,
                            leftMargin=25*mm, rightMargin=25*mm,
                            topMargin=25*mm, bottomMargin=25*mm)
    styles = getSampleStyleSheet()
    story = []
    for p in doc.paragraphs:
        t = p.text.strip()
        if not t:
            story.append(Spacer(1, 6*mm))
            continue
        sn = "Normal"
        if p.style and p.style.name:
            n = p.style.name.lower()
            if "heading 1" in n or "title" in n:
                sn = "Heading1"
            elif "heading 2" in n:
                sn = "Heading2"
            elif "heading 3" in n:
                sn = "Heading3"
        story.append(Paragraph(t, styles[sn]))
    pdf.build(story)


def do_pdf_to_text(src, dst):
    from pypdf import PdfReader
    r = PdfReader(src)
    text = "\n\n".join(p.extract_text() or "" for p in r.pages)
    Path(dst).write_text(text, encoding="utf-8")


def do_merge_pdfs(files, dst):
    from pypdf import PdfReader, PdfWriter
    w = PdfWriter()
    for f in files:
        for p in PdfReader(f).pages:
            w.add_page(p)
    with open(dst, "wb") as fh:
        w.write(fh)


def do_split_pdf(src, out_dir):
    from pypdf import PdfReader, PdfWriter
    os.makedirs(out_dir, exist_ok=True)
    r = PdfReader(src)
    stem = Path(src).stem
    for i, page in enumerate(r.pages, 1):
        w = PdfWriter()
        w.add_page(page)
        with open(os.path.join(out_dir, f"{stem}_page{i}.pdf"), "wb") as fh:
            w.write(fh)
    return len(r.pages)


def do_excel_to_csv(src, dst):
    import openpyxl, csv
    wb = openpyxl.load_workbook(src, read_only=True, data_only=True)
    ws = wb.active
    with open(dst, "w", newline="", encoding="utf-8-sig") as f:
        for row in ws.iter_rows(values_only=True):
            csv.writer(f).writerow(row)
    wb.close()


def do_csv_to_excel(src, dst):
    import csv, openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    with open(src, "r", encoding="utf-8-sig") as f:
        for row in csv.reader(f):
            ws.append(row)
    wb.save(dst)


# ── 转换类型配置 ──

TYPES = {
    "图片 → PDF": {
        "multi": True,
        "filetypes": [("图片", "*.png *.jpg *.jpeg *.webp *.bmp *.tiff *.gif")],
        "out_ext": ".pdf",
        "out_is_dir": False,
        "run": lambda ins, out: do_images_to_pdf(ins, out),
    },
    "PDF → 图片(每页PNG)": {
        "multi": False,
        "filetypes": [("PDF", "*.pdf")],
        "out_ext": None,
        "out_is_dir": True,
        "run": lambda ins, out: do_pdf_to_images(ins[0], out),
    },
    "图片格式转换": {
        "multi": False,
        "filetypes": [("图片", "*.png *.jpg *.jpeg *.webp *.bmp *.tiff *.gif")],
        "out_ext": ".png",
        "out_is_dir": False,
        "run": lambda ins, out: do_image_convert(ins[0], out),
        "exts": [".png", ".jpg", ".webp", ".bmp"],
    },
    "Word → PDF": {
        "multi": False,
        "filetypes": [("Word", "*.docx")],
        "out_ext": ".pdf",
        "out_is_dir": False,
        "run": lambda ins, out: do_word_to_pdf(ins[0], out),
    },
    "PDF → 文本": {
        "multi": False,
        "filetypes": [("PDF", "*.pdf")],
        "out_ext": ".txt",
        "out_is_dir": False,
        "run": lambda ins, out: do_pdf_to_text(ins[0], out),
    },
    "合并PDF": {
        "multi": True,
        "filetypes": [("PDF", "*.pdf")],
        "out_ext": ".pdf",
        "out_is_dir": False,
        "run": lambda ins, out: do_merge_pdfs(ins, out),
    },
    "拆分PDF": {
        "multi": False,
        "filetypes": [("PDF", "*.pdf")],
        "out_ext": None,
        "out_is_dir": True,
        "run": lambda ins, out: do_split_pdf(ins[0], out),
    },
    "Excel → CSV": {
        "multi": False,
        "filetypes": [("Excel", "*.xlsx *.xls")],
        "out_ext": ".csv",
        "out_is_dir": False,
        "run": lambda ins, out: do_excel_to_csv(ins[0], out),
    },
    "CSV → Excel": {
        "multi": False,
        "filetypes": [("CSV", "*.csv")],
        "out_ext": ".xlsx",
        "out_is_dir": False,
        "run": lambda ins, out: do_csv_to_excel(ins[0], out),
    },
}


# ── GUI ──

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("万能文件转换工具")
        self.root.geometry("650x500")
        self.root.resizable(False, False)
        self.files = []

        # 标题
        hdr = tk.Frame(root, bg="#4a90d9", height=55)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="万能文件转换工具", font=("Microsoft YaHei UI", 16, "bold"),
                 fg="white", bg="#4a90d9").pack(expand=True)

        body = tk.Frame(root, padx=25, pady=10)
        body.pack(fill="both", expand=True)

        # 转换类型
        tk.Label(body, text="转换类型：", font=("Microsoft YaHei UI", 10)).pack(anchor="w")
        self.type_var = tk.StringVar(value=list(TYPES.keys())[0])
        cb = ttk.Combobox(body, textvariable=self.type_var, values=list(TYPES.keys()),
                          state="readonly", width=28, font=("Microsoft YaHei UI", 10))
        cb.pack(anchor="w", pady=(2, 10))

        # 文件选择
        row1 = tk.Frame(body)
        row1.pack(fill="x")
        self.file_lbl = tk.Label(row1, text="未选择文件", fg="#999",
                                 font=("Microsoft YaHei UI", 9), anchor="w")
        self.file_lbl.pack(side="left", fill="x", expand=True)
        tk.Button(row1, text="选择文件", bg="#4a90d9", fg="white",
                  font=("Microsoft YaHei UI", 10), relief="flat", padx=12,
                  command=self.pick_files).pack(side="right")

        # 格式选择（图片转换用）
        self.ext_frame = tk.Frame(body)
        tk.Label(self.ext_frame, text="输出格式：", font=("Microsoft YaHei UI", 10)).pack(side="left")
        self.ext_var = tk.StringVar(value=".png")
        ttk.Combobox(self.ext_frame, textvariable=self.ext_var, state="readonly",
                      width=8, font=("Microsoft YaHei UI", 10)).pack(side="left", padx=5)

        # 文件列表
        lf = tk.Frame(body, relief="solid", bd=1, bg="white")
        lf.pack(fill="both", expand=True, pady=10)
        self.lb = tk.Listbox(lf, font=("Consolas", 9), bd=0, highlightthickness=0)
        sb = ttk.Scrollbar(lf, orient="vertical", command=self.lb.yview)
        self.lb.configure(yscrollcommand=sb.set)
        self.lb.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # 转换按钮
        tk.Button(body, text="开始转换", font=("Microsoft YaHei UI", 13, "bold"),
                  bg="#4caf50", fg="white", relief="flat", padx=25, pady=6,
                  command=self.start).pack(pady=5)

        # 状态
        self.status = tk.StringVar(value="就绪")
        tk.Label(body, textvariable=self.status, fg="#666",
                 font=("Microsoft YaHei UI", 9), anchor="w").pack(fill="x")

    def pick_files(self):
        t = TYPES[self.type_var.get()]
        ft = t["filetypes"] + [("所有文件", "*.*")]
        if t["multi"]:
            sel = filedialog.askopenfilenames(filetypes=ft)
        else:
            f = filedialog.askopenfilename(filetypes=ft)
            sel = [f] if f else []

        if sel:
            self.files = [os.path.normpath(str(s)) for s in sel if s]
            self.lb.delete(0, tk.END)
            for f in self.files:
                self.lb.insert(tk.END, f)
            self.file_lbl.config(
                text=f"已选 {len(self.files)} 个文件" if len(self.files) > 1 else self.files[0],
                fg="#333")

    def start(self):
        if not self.files:
            messagebox.showwarning("提示", "请先选择文件！")
            return

        t = TYPES[self.type_var.get()]

        if t["out_is_dir"]:
            out = filedialog.askdirectory(title="选择输出目录")
            if not out:
                return
        else:
            ext = self.ext_var.get() if t.get("exts") else t["out_ext"]
            fn = Path(self.files[0]).stem + ext
            out = filedialog.asksaveasfilename(
                defaultextension=ext, initialfile=fn,
                filetypes=[(f"*{ext}", f"*{ext}"), ("所有文件", "*.*")])
            if not out:
                return

        out = os.path.normpath(str(out))
        ins = [os.path.normpath(str(f)) for f in self.files]

        self.status.set("转换中...")
        self.root.update()

        try:
            t["run"](ins, out)
            self.status.set(f"完成！ → {out}")
            messagebox.showinfo("成功", f"转换完成！\n{out}")
        except Exception as e:
            self.status.set("失败")
            messagebox.showerror("失败", f"错误：{e}\n\n{traceback.format_exc()}")


def main():
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use("clam")
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
