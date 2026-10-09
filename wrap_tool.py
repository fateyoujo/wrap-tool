# -*- coding: utf-8 -*-
"""
文章自动换行工具（图形界面）

功能：
  - 把粘贴进来的文章按固定字符数自动换行；
  - 忽略原文换行，整篇文章连续排版，每行正好等于设定字数；
  - 最后不足的一行自动用空格补足；
  - 每行字数可在窗口中随时调整；
  - 可选开关：标点转半角（保留中文符号）、标点不计字数、数字不计字数；
  - 输入内容一变化，右侧立即实时刷新输出结果；
  - 一键复制输出结果。

运行：python wrap_tool.py
"""

import tkinter as tk
from tkinter import ttk


# 全角标点 -> 半角标点 映射（保留中文独有符号：。、·《》【】 不转换）
FULLWIDTH_TO_HALFWIDTH = {
    '，': ',', '！': '!', '？': '?', '；': ';', '：': ':',
    '（': '(', '）': ')',
    '“': '"', '”': '"', '‘': "'", '’': "'",
    '—': '-', '～': '~', '…': '...',
}

# 视为“标点”的字符；开启“标点不计字数”时它们不占每行字数
PUNCT_CHARS = set(
    ",.!?;:()[]{}<>\"'`~-"
    "，。！？；：（）【】《》“”‘’—～…"
    "、·"
)

# 视为“数字”的字符；开启“数字不计字数”时它们不占每行字数
DIGIT_CHARS = set("0123456789０１２３４５６７８９")


def wrap_text(text, width, punct_halfwidth=False,
              punct_no_count=False, digit_no_count=False):
    """把 text 按每行 width 个字符换行，不足的行用空格补足到 width。

    说明：
      - 默认中文、英文、数字、标点都算 1 个字符；
      - 忽略原文中的换行与空行，把整篇文章当作连续文字重新排版；
      - punct_halfwidth：全角标点自动转半角（保留中文独有符号）；
      - punct_no_count：标点不计入每行字数；
      - digit_no_count：数字不计入每行字数；
      - 每行正好等于 width 个“计数字符”，最后不足的一行用空格补足。
    """
    fill = " "
    width = max(1, int(width)) if width else 1

    # 去掉所有换行/回车，整篇作为连续文字
    continuous = text.replace("\r", "").replace("\n", "")

    # 全角标点转半角（保留中文独有符号）
    if punct_halfwidth:
        for full, half in FULLWIDTH_TO_HALFWIDTH.items():
            continuous = continuous.replace(full, half)

    def is_no_count(ch):
        if punct_no_count and ch in PUNCT_CHARS:
            return True
        if digit_no_count and ch in DIGIT_CHARS:
            return True
        return False

    # 没有任何“不计字数”开关时，直接按字符硬切
    if not (punct_no_count or digit_no_count):
        out_lines = []
        for i in range(0, len(continuous), width):
            chunk = continuous[i:i + width]
            if len(chunk) < width:
                chunk += fill * (width - len(chunk))
            out_lines.append(chunk)
        return "\n".join(out_lines)

    # 存在“不计字数”开关：只统计“计数字符”，不计数的字符紧跟在前一行尾部
    lines = []
    buf = []
    count = 0
    for ch in continuous:
        if count >= width and not is_no_count(ch):
            lines.append("".join(buf))
            buf = []
            count = 0
        buf.append(ch)
        if not is_no_count(ch):
            count += 1
    if buf:
        pad = width - count
        if pad > 0:
            buf.append(fill * pad)
        lines.append("".join(buf))
    return "\n".join(lines)


class WrapToolApp:
    def __init__(self, root):
        self.root = root
        root.title("文章自动换行工具")
        root.geometry("1080x640")
        root.minsize(720, 420)

        # ---- 控制栏 ----
        bar = ttk.Frame(root, padding=(10, 8, 10, 6))
        bar.pack(side=tk.TOP, fill=tk.X)

        self.width_var = tk.StringVar(value="40")
        self.punct_halfwidth_var = tk.BooleanVar(value=False)
        self.punct_nocount_var = tk.BooleanVar(value=False)
        self.digit_nocount_var = tk.BooleanVar(value=False)

        ttk.Label(bar, text="每行字数:").pack(side=tk.LEFT)
        self.width_spin = ttk.Spinbox(
            bar, from_=1, to=1000, increment=1,
            textvariable=self.width_var, width=6)
        self.width_spin.pack(side=tk.LEFT, padx=(2, 16))

        self.punct_halfwidth_check = ttk.Checkbutton(
            bar, text="标点转半角(保留中文符号)", variable=self.punct_halfwidth_var)
        self.punct_halfwidth_check.pack(side=tk.LEFT, padx=(0, 16))

        self.punct_nocount_check = ttk.Checkbutton(
            bar, text="标点符号不计字数", variable=self.punct_nocount_var)
        self.punct_nocount_check.pack(side=tk.LEFT, padx=(0, 16))

        self.digit_nocount_check = ttk.Checkbutton(
            bar, text="数字不计字数", variable=self.digit_nocount_var)
        self.digit_nocount_check.pack(side=tk.LEFT, padx=(0, 16))

        self.copy_btn = ttk.Button(bar, text="复制结果", command=self.copy_result)
        self.copy_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.clear_btn = ttk.Button(bar, text="清空输入", command=self.clear_input)
        self.clear_btn.pack(side=tk.LEFT)

        # ---- 主区域：左右两个文本框 ----
        main = ttk.Frame(root, padding=(10, 0, 10, 0))
        main.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        main.columnconfigure(0, weight=1, uniform="col")
        main.columnconfigure(1, weight=1, uniform="col")
        main.rowconfigure(1, weight=1)

        ttk.Label(main, text="输入（粘贴文章到这里）").grid(
            row=0, column=0, sticky=tk.W, pady=(0, 4))
        ttk.Label(main, text="输出（实时结果）").grid(
            row=0, column=1, sticky=tk.W, pady=(0, 4))

        # 输入框
        in_frame = ttk.Frame(main)
        in_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        in_frame.rowconfigure(0, weight=1)
        in_frame.columnconfigure(0, weight=1)

        self.input_text = tk.Text(in_frame, wrap="none", undo=True,
                                  font=("Microsoft YaHei UI", 11))
        in_sb = ttk.Scrollbar(in_frame, orient="vertical",
                              command=self.input_text.yview)
        self.input_text.configure(yscrollcommand=in_sb.set)
        self.input_text.grid(row=0, column=0, sticky="nsew")
        in_sb.grid(row=0, column=1, sticky="ns")

        # 输出框（只读）
        out_frame = ttk.Frame(main)
        out_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 0))
        out_frame.rowconfigure(0, weight=1)
        out_frame.columnconfigure(0, weight=1)

        self.output_text = tk.Text(out_frame, wrap="none", state="disabled",
                                   font=("Consolas", 11))
        out_sb = ttk.Scrollbar(out_frame, orient="vertical",
                               command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=out_sb.set)
        self.output_text.grid(row=0, column=0, sticky="nsew")
        out_sb.grid(row=0, column=1, sticky="ns")

        # ---- 状态栏 ----
        self.status_var = tk.StringVar(value="就绪：粘贴文字到左侧，右侧实时换行。")
        status = ttk.Label(root, textvariable=self.status_var,
                           anchor=tk.W, padding=(10, 4))
        status.pack(side=tk.BOTTOM, fill=tk.X)

        # ---- 事件绑定：任何输入/设置变化都实时刷新 ----
        self.input_text.bind("<<Modified>>", self.on_input_modified)
        self.width_var.trace_add("write", lambda *a: self.recompute())
        self.punct_halfwidth_var.trace_add("write", lambda *a: self.recompute())
        self.punct_nocount_var.trace_add("write", lambda *a: self.recompute())
        self.digit_nocount_var.trace_add("write", lambda *a: self.recompute())

        # ---- 右键菜单：支持右键粘贴等操作 ----
        self.input_menu = tk.Menu(root, tearoff=0)
        self.input_menu.add_command(label="剪切", accelerator="Ctrl+X",
                                    command=lambda: self.input_text.event_generate("<<Cut>>"))
        self.input_menu.add_command(label="复制", accelerator="Ctrl+C",
                                    command=lambda: self.input_text.event_generate("<<Copy>>"))
        self.input_menu.add_command(label="粘贴", accelerator="Ctrl+V",
                                    command=self._paste_input)
        self.input_menu.add_separator()
        self.input_menu.add_command(label="全选", accelerator="Ctrl+A",
                                    command=self._select_all_input)
        self.input_menu.add_command(label="清空", command=self.clear_input)
        self.input_text.bind("<Button-3>", self._show_input_menu)

        self.recompute()

    def _show_input_menu(self, event):
        """在鼠标点击处显示右键菜单。"""
        try:
            self.input_text.mark_set("insert", f"@{event.x},{event.y}")
            self.input_text.focus_set()
        except tk.TclError:
            pass
        self.input_menu.tk_popup(event.x_root, event.y_root)

    def _paste_input(self):
        """把剪贴板内容粘贴到输入框光标处。"""
        self.input_text.focus_set()
        self.input_text.event_generate("<<Paste>>")

    def _select_all_input(self):
        self.input_text.tag_add("sel", "1.0", "end-1c")
        self.input_text.mark_set("insert", "1.0")
        self.input_text.focus_set()

    def on_input_modified(self, event=None):
        if self.input_text.edit_modified():
            self.input_text.edit_modified(False)
            self.recompute()

    def _safe_width(self):
        try:
            w = int(self.width_var.get())
        except (ValueError, TypeError):
            w = 0
        return max(1, min(1000, w))

    def recompute(self):
        text = self.input_text.get("1.0", "end-1c")
        width = self._safe_width()
        punct_halfwidth = self.punct_halfwidth_var.get()
        punct_no_count = self.punct_nocount_var.get()
        digit_no_count = self.digit_nocount_var.get()

        result = wrap_text(text, width, punct_halfwidth,
                           punct_no_count, digit_no_count)

        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", result)
        self.output_text.configure(state="disabled")

        in_chars = len(text.replace("\n", "").replace("\r", ""))
        out_lines = result.count("\n") + (1 if result else 0)
        opts = []
        if punct_halfwidth:
            opts.append("标点转半角")
        if punct_no_count:
            opts.append("标点不计字数")
        if digit_no_count:
            opts.append("数字不计字数")
        opt_text = "、".join(opts) if opts else "无"
        self.status_var.set(
            f"每行 {width} 字 | 输入 {in_chars} 字 | 输出 {out_lines} 行 | "
            f"开启: {opt_text} | 末行已自动补足")

    def copy_result(self):
        content = self.output_text.get("1.0", "end-1c")
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self.status_var.set("结果已复制到剪贴板。")

    def clear_input(self):
        self.input_text.delete("1.0", "end")


def main():
    root = tk.Tk()
    WrapToolApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
