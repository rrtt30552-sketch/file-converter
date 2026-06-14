"""
调试版 - 测试文件选择和转换
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

def main():
    root = tk.Tk()
    root.title("调试测试")
    root.geometry("500x400")

    result_text = tk.Text(root, font=("Consolas", 10))
    result_text.pack(fill="both", expand=True, padx=10, pady=10)

    def log(msg):
        result_text.insert(tk.END, msg + "\n")
        result_text.see(tk.END)
        root.update()

    def test_select():
        log("=== 测试文件选择 ===")
        f = filedialog.askopenfilename(
            title="选一张图片",
            filetypes=[("图片", "*.png"), ("图片", "*.jpg"), ("所有文件", "*.*")]
        )
        log(f"返回值类型: {type(f)}")
        log(f"返回值: [{f}]")
        log(f"返回值长度: {len(f) if f else 0}")

        if f:
            log(f"repr: {repr(f)}")
            log(f"os.path.exists: {os.path.exists(f)}")
            if os.path.exists(f):
                log(f"文件大小: {os.path.getsize(f)} bytes")
                log("尝试用 PIL 打开...")
                try:
                    from PIL import Image
                    img = Image.open(f)
                    log(f"成功！尺寸: {img.size}, 模式: {img.mode}")
                    img.close()
                except Exception as e:
                    log(f"PIL 打开失败: {e}")
            else:
                log("文件不存在！逐字符检查:")
                for i, c in enumerate(f):
                    log(f"  [{i}] = {repr(c)} (ord={ord(c)})")

    def test_convert():
        log("\n=== 测试完整转换流程 ===")
        f = filedialog.askopenfilename(
            title="选一张图片",
            filetypes=[("图片", "*.png"), ("图片", "*.jpg"), ("所有文件", "*.*")]
        )
        if not f:
            log("取消选择")
            return

        log(f"原始路径: [{f}]")

        # 规范化
        norm = os.path.normpath(f)
        log(f"规范化后: [{norm}]")
        log(f"存在: {os.path.exists(norm)}")

        if not os.path.exists(norm):
            log("文件不存在，停止")
            return

        # 选择输出
        out = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile="test_output.pdf",
            filetypes=[("PDF", "*.pdf")]
        )
        if not out:
            log("取消输出选择")
            return

        log(f"输出路径: [{out}]")

        try:
            from PIL import Image
            img = Image.open(norm)
            if img.mode in ("RGBA", "P", "LA"):
                img = img.convert("RGB")
            img.save(out, "PDF", save_all=True, quality=95)
            log(f"✅ 转换成功！输出: {out}")
            log(f"输出文件大小: {os.path.getsize(out)} bytes")
        except Exception as e:
            log(f"❌ 转换失败: {e}")
            import traceback
            log(traceback.format_exc())

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=5)

    tk.Button(btn_frame, text="测试选择文件", command=test_select,
              font=("Arial", 11), padx=10).pack(side="left", padx=5)
    tk.Button(btn_frame, text="测试完整转换", command=test_convert,
              font=("Arial", 11), padx=10).pack(side="left", padx=5)

    root.mainloop()

if __name__ == "__main__":
    main()
