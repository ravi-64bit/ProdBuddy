"""Centralised visual design system and themed dialogs for ProdBuddy."""

import tkinter as tk
from tkinter import ttk


LIGHT = {
    "bg": "#F7F8FA",
    "panel": "#FFFFFF",
    "sidebar": "#F1F3F6",
    "fg": "#20242C",
    "muted": "#737D8C",
    "accent": "#456FE8",
    "accent_hover": "#345ED0",
    "input": "#FFFFFF",
    "border": "#E3E7ED",
    "selected": "#E8EEFC",
    "success": "#23845B",
    "danger": "#D84B4B",
}

DARK = {
    "bg": "#171A21",
    "panel": "#20242D",
    "sidebar": "#1C2028",
    "fg": "#E9EDF4",
    "muted": "#9AA4B3",
    "accent": "#7799FF",
    "accent_hover": "#91AAFF",
    "input": "#292F3A",
    "border": "#343B48",
    "selected": "#303D5B",
    "success": "#55B88A",
    "danger": "#F07878",
}

_SCALE = 1.0
_CURRENT_COLORS = LIGHT.copy()


def px(value):
    return int(round(value * _SCALE))


def setup(root):
    global _SCALE
    try:
        dpi = root.winfo_fpixels("1i")
        _SCALE = max(1.0, dpi / 96.0)
        root.tk.call("tk", "scaling", dpi / 72.0)
    except tk.TclError:
        _SCALE = 1.0


def apply(root, dark=False):
    global _CURRENT_COLORS
    colors = DARK.copy() if dark else LIGHT.copy()
    _CURRENT_COLORS = colors

    root.configure(bg=colors["bg"])

    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(
        ".",
        font=("Segoe UI", 10),
        foreground=colors["fg"],
        background=colors["bg"],
    )

    style.configure("TFrame", background=colors["bg"])
    style.configure("Panel.TFrame", background=colors["panel"])
    style.configure("Sidebar.TFrame", background=colors["sidebar"])

    style.configure(
        "TLabel",
        background=colors["bg"],
        foreground=colors["fg"],
    )
    style.configure(
        "Muted.TLabel",
        background=colors["bg"],
        foreground=colors["muted"],
    )
    style.configure(
        "Heading.TLabel",
        font=("Segoe UI", 20, "bold"),
        background=colors["bg"],
        foreground=colors["fg"],
    )
    style.configure(
        "SidebarBrand.TLabel",
        font=("Segoe UI", 16, "bold"),
        background=colors["sidebar"],
        foreground=colors["fg"],
    )
    style.configure(
        "SidebarSection.TLabel",
        font=("Segoe UI", 9, "bold"),
        background=colors["sidebar"],
        foreground=colors["muted"],
    )

    style.configure(
        "TButton",
        padding=(px(10), px(6)),
        borderwidth=1,
        relief="flat",
        background=colors["panel"],
        foreground=colors["fg"],
        bordercolor=colors["border"],
        lightcolor=colors["panel"],
        darkcolor=colors["panel"],
        focuscolor=colors["selected"],
    )
    style.map(
        "TButton",
        background=[
            ("active", colors["selected"]),
            ("pressed", colors["border"]),
        ],
        foreground=[("disabled", colors["muted"])],
        bordercolor=[("active", colors["accent"])],
    )

    style.configure(
        "Primary.TButton",
        padding=(px(14), px(6)),
        borderwidth=0,
        relief="flat",
        background=colors["accent"],
        foreground="#FFFFFF",
        font=("Segoe UI", 10, "bold"),
        focuscolor=colors["accent_hover"],
    )
    style.map(
        "Primary.TButton",
        background=[
            ("active", colors["accent_hover"]),
            ("pressed", colors["accent_hover"]),
        ],
        foreground=[("disabled", colors["muted"])],
    )

    style.configure(
        "Danger.TButton",
        padding=(px(10), px(6)),
        borderwidth=1,
        relief="flat",
        background=colors["panel"],
        foreground=colors["danger"],
        bordercolor=colors["border"],
    )
    style.map(
        "Danger.TButton",
        background=[
            ("active", colors["danger"]),
            ("pressed", colors["danger"]),
        ],
        foreground=[
            ("active", "#FFFFFF"),
            ("pressed", "#FFFFFF"),
        ],
    )

    style.configure(
        "Nav.TButton",
        padding=(px(10), px(7)),
        borderwidth=0,
        relief="flat",
        anchor="w",
        background=colors["sidebar"],
        foreground=colors["fg"],
        font=("Segoe UI", 10),
    )
    style.map(
        "Nav.TButton",
        background=[
            ("active", colors["selected"]),
            ("pressed", colors["selected"]),
        ],
    )

    style.configure(
        "NavActive.TButton",
        padding=(px(10), px(7)),
        borderwidth=0,
        relief="flat",
        anchor="w",
        background=colors["selected"],
        foreground=colors["accent"],
        font=("Segoe UI", 10, "bold"),
    )
    style.map(
        "NavActive.TButton",
        background=[
            ("active", colors["selected"]),
            ("pressed", colors["selected"]),
        ],
    )

    style.configure(
        "Sidebar.TButton",
        padding=(px(8), px(5)),
        borderwidth=1,
        relief="flat",
        background=colors["panel"],
        foreground=colors["fg"],
        bordercolor=colors["border"],
        font=("Segoe UI", 9),
    )
    style.map(
        "Sidebar.TButton",
        background=[
            ("active", colors["selected"]),
            ("pressed", colors["border"]),
        ],
        bordercolor=[("active", colors["accent"])],
    )

    style.configure(
        "TEntry",
        padding=(px(8), px(6)),
        fieldbackground=colors["input"],
        foreground=colors["fg"],
        bordercolor=colors["border"],
        lightcolor=colors["border"],
        darkcolor=colors["border"],
        insertcolor=colors["fg"],
    )
    style.map(
        "TEntry",
        bordercolor=[("focus", colors["accent"])],
        lightcolor=[("focus", colors["accent"])],
        darkcolor=[("focus", colors["accent"])],
    )

    style.configure(
        "TCombobox",
        padding=(px(6), px(5)),
        fieldbackground=colors["input"],
        foreground=colors["fg"],
        background=colors["panel"],
        bordercolor=colors["border"],
        arrowcolor=colors["fg"],
    )

    style.configure(
        "Treeview",
        background=colors["panel"],
        fieldbackground=colors["panel"],
        foreground=colors["fg"],
        rowheight=px(36),
        borderwidth=1,
        relief="solid",
        bordercolor=colors["border"],
        lightcolor=colors["border"],
        darkcolor=colors["border"],
        font=("Segoe UI", 10),
    )
    style.configure(
        "Treeview.Heading",
        background=colors["sidebar"],
        foreground=colors["muted"],
        relief="flat",
        borderwidth=0,
        padding=(px(8), px(8)),
        font=("Segoe UI", 9, "bold"),
    )
    style.map(
        "Treeview.Heading",
        background=[("active", colors["selected"])],
    )
    style.map(
        "Treeview",
        background=[("selected", colors["selected"])],
        foreground=[("selected", colors["fg"])],
    )

    style.configure(
        "Vertical.TScrollbar",
        background=colors["sidebar"],
        troughcolor=colors["panel"],
        borderwidth=0,
        arrowsize=px(12),
    )

    return colors


def _colors_for(parent):
    if parent is not None and hasattr(parent, "winfo_toplevel"):
        top = parent.winfo_toplevel()
        if hasattr(top, "colors") and isinstance(top.colors, dict):
            return top.colors
    return _CURRENT_COLORS


class _BaseDialog(tk.Toplevel):
    def __init__(self, parent, title, width=380, height=180):
        super().__init__(parent)
        self.title(title)
        self.colors = _colors_for(parent)
        self.configure(bg=self.colors["bg"])
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)
        self.result = None

        if parent is not None:
            try:
                px_x = parent.winfo_rootx()
                px_y = parent.winfo_rooty()
                pw = parent.winfo_width()
                ph = parent.winfo_height()
                x = px_x + max(0, (pw - px(width)) // 2)
                y = px_y + max(0, (ph - px(height)) // 2)
                self.geometry(f"{px(width)}x{px(height)}+{x}+{y}")
            except tk.TclError:
                self.geometry(f"{px(width)}x{px(height)}")
        else:
            self.geometry(f"{px(width)}x{px(height)}")

        self.protocol("WM_DELETE_WINDOW", self._cancel)

    def _cancel(self):
        self.result = None
        self.destroy()

    def run(self):
        self.wait_window()
        return self.result


def ask_text(parent, title, prompt, initialvalue=""):
    dlg = _BaseDialog(parent, title, width=400, height=165)

    frame = ttk.Frame(dlg)
    frame.pack(fill="both", expand=True, padx=px(16), pady=px(14))

    ttk.Label(frame, text=prompt).pack(anchor="w", pady=(0, px(8)))
    entry = ttk.Entry(frame)
    entry.pack(fill="x")
    if initialvalue:
        entry.insert(0, initialvalue)
    entry.focus_set()
    entry.select_range(0, tk.END)

    def confirm(_e=None):
        dlg.result = entry.get()
        dlg.destroy()

    entry.bind("<Return>", confirm)
    dlg.bind("<Escape>", lambda _e: dlg._cancel())

    btns = ttk.Frame(frame)
    btns.pack(fill="x", pady=(px(14), 0))
    ttk.Button(btns, text="Cancel", command=dlg._cancel).pack(side="right", padx=(px(6), 0))
    ttk.Button(btns, text="OK", style="Primary.TButton", command=confirm).pack(side="right")

    return dlg.run()


def ask_notes(parent, title, prompt, initialvalue=""):
    dlg = _BaseDialog(parent, title, width=460, height=280)
    c = dlg.colors

    frame = ttk.Frame(dlg)
    frame.pack(fill="both", expand=True, padx=px(16), pady=px(14))

    ttk.Label(frame, text=prompt).pack(anchor="w", pady=(0, px(6)))

    text_box = tk.Text(
        frame,
        height=7,
        wrap="word",
        font=("Segoe UI", 10),
        bg=c["input"],
        fg=c["fg"],
        insertbackground=c["fg"],
        selectbackground=c["selected"],
        selectforeground=c["fg"],
        relief="solid",
        borderwidth=1,
        highlightthickness=1,
        highlightbackground=c["border"],
        highlightcolor=c["accent"],
        padx=px(8),
        pady=px(6),
    )
    text_box.pack(fill="both", expand=True)
    if initialvalue:
        text_box.insert("1.0", initialvalue)
    text_box.focus_set()

    def confirm(_e=None):
        dlg.result = text_box.get("1.0", "end-1c")
        dlg.destroy()

    dlg.bind("<Control-Return>", confirm)
    dlg.bind("<Escape>", lambda _e: dlg._cancel())

    btns = ttk.Frame(frame)
    btns.pack(fill="x", pady=(px(12), 0))
    ttk.Label(btns, text="Ctrl+Enter to save", style="Muted.TLabel").pack(side="left")
    ttk.Button(btns, text="Cancel", command=dlg._cancel).pack(side="right", padx=(px(6), 0))
    ttk.Button(btns, text="Save", style="Primary.TButton", command=confirm).pack(side="right")

    return dlg.run()


def ask_choice(parent, title, prompt, choices, default_index=0):
    if not choices:
        return None
    dlg = _BaseDialog(parent, title, width=380, height=165)
    frame = ttk.Frame(dlg)
    frame.pack(fill="both", expand=True, padx=px(16), pady=px(14))

    ttk.Label(frame, text=prompt).pack(anchor="w", pady=(0, px(8)))
    combo = ttk.Combobox(frame, values=list(choices), state="readonly")
    combo.current(min(max(0, default_index), len(choices) - 1))
    combo.pack(fill="x")
    combo.focus_set()

    def confirm(_e=None):
        idx = combo.current()
        dlg.result = idx if idx >= 0 else None
        dlg.destroy()

    combo.bind("<Return>", confirm)
    dlg.bind("<Escape>", lambda _e: dlg._cancel())

    btns = ttk.Frame(frame)
    btns.pack(fill="x", pady=(px(14), 0))
    ttk.Button(btns, text="Cancel", command=dlg._cancel).pack(side="right", padx=(px(6), 0))
    ttk.Button(btns, text="Select", style="Primary.TButton", command=confirm).pack(side="right")

    return dlg.run()


def show_message(parent, title, message, kind="info"):
    dlg = _BaseDialog(parent, title, width=400, height=160)
    c = dlg.colors
    frame = ttk.Frame(dlg)
    frame.pack(fill="both", expand=True, padx=px(16), pady=px(14))

    accent_fg = c["danger"] if kind == "error" else c["fg"]
    msg_lbl = tk.Label(
        frame,
        text=message,
        justify="left",
        wraplength=px(360),
        font=("Segoe UI", 10),
        bg=c["bg"],
        fg=accent_fg,
    )
    msg_lbl.pack(anchor="w", fill="both", expand=True)

    def ok(_e=None):
        dlg.result = True
        dlg.destroy()

    dlg.bind("<Return>", ok)
    dlg.bind("<Escape>", ok)

    btns = ttk.Frame(frame)
    btns.pack(fill="x", pady=(px(10), 0))
    ttk.Button(btns, text="OK", style="Primary.TButton", command=ok).pack(side="right")
    dlg.run()


def ask_yes_no(parent, title, message):
    dlg = _BaseDialog(parent, title, width=400, height=165)
    frame = ttk.Frame(dlg)
    frame.pack(fill="both", expand=True, padx=px(16), pady=px(14))

    msg_lbl = tk.Label(
        frame,
        text=message,
        justify="left",
        wraplength=px(360),
        font=("Segoe UI", 10),
        bg=dlg.colors["bg"],
        fg=dlg.colors["fg"],
    )
    msg_lbl.pack(anchor="w", fill="both", expand=True)

    def yes(_e=None):
        dlg.result = True
        dlg.destroy()

    def no(_e=None):
        dlg.result = False
        dlg.destroy()

    dlg.bind("<Return>", yes)
    dlg.bind("<Escape>", no)

    btns = ttk.Frame(frame)
    btns.pack(fill="x", pady=(px(10), 0))
    ttk.Button(btns, text="No", command=no).pack(side="right", padx=(px(6), 0))
    ttk.Button(btns, text="Yes", style="Danger.TButton", command=yes).pack(side="right")

    return bool(dlg.run())