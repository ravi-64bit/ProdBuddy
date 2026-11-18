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


def px(value):
    return int(value)


def setup(root):
    try:
        root.tk.call("tk", "scaling", root.winfo_fpixels("1i") / 72.0)
    except tk.TclError:
        pass


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
        font=("Segoe UI", 24, "bold"),
        background=colors["bg"],
        foreground=colors["fg"],
    )

    style.configure(
        "TButton",
        padding=(12, 8),
        borderwidth=0,
        background=colors["panel"],
        foreground=colors["fg"],
    )
    style.map(
        "TButton",
        background=[
            ("active", colors["selected"]),
            ("pressed", colors["border"]),
        ],
    )

    style.configure(
        "Primary.TButton",
        padding=(14, 8),
        background=colors["accent"],
        foreground="#FFFFFF",
        font=("Segoe UI", 10, "bold"),
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
        "TEntry",
        padding=9,
        fieldbackground=colors["input"],
        foreground=colors["fg"],
        bordercolor=colors["border"],
        insertcolor=colors["fg"],
    )

    style.configure(
        "Treeview",
        background=colors["panel"],
        fieldbackground=colors["panel"],
        foreground=colors["fg"],
        rowheight=40,
        borderwidth=0,
        font=("Segoe UI", 10),
    )
    style.configure(
        "Treeview.Heading",
        background=colors["bg"],
        foreground=colors["muted"],
        relief="flat",
        padding=(10, 10),
        font=("Segoe UI", 9, "bold"),
    )
    style.map(
        "Treeview",
        background=[("selected", colors["selected"])],
        foreground=[("selected", colors["fg"])],
    )

    return colors
