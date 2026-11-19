"""Centralised visual design system for ProdBuddy."""

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
    colors = DARK.copy() if dark else LIGHT.copy()

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
