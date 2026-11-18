"""Centralised Tk/ttk theme helpers."""
import tkinter as tk
from tkinter import ttk


def px(value):
    """Scale logical pixels using Tk's current scaling factor."""
    return int(value)


def setup(root):
    try:
        root.tk.call("tk", "scaling", root.winfo_fpixels("1i") / 72.0)
    except tk.TclError:
        pass


def apply(root, dark=False):
    colors = ({"bg": "#17191f", "panel": "#20232b", "fg": "#edf0f5", "muted": "#a5adba",
               "accent": "#78a9ff", "input": "#292d37", "selected": "#354968"}
              if dark else
              {"bg": "#f5f6f8", "panel": "#ffffff", "fg": "#20242c", "muted": "#687080",
               "accent": "#245fbd", "input": "#ffffff", "selected": "#dce8fb"})
    root.configure(background=colors["bg"])
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure(".", background=colors["bg"], foreground=colors["fg"], fieldbackground=colors["input"])
    style.configure("TFrame", background=colors["bg"])
    style.configure("Panel.TFrame", background=colors["panel"])
    style.configure("TLabel", background=colors["bg"], foreground=colors["fg"])
    style.configure("Muted.TLabel", background=colors["bg"], foreground=colors["muted"])
    style.configure("TButton", padding=(10, 6))
    style.configure("TEntry", fieldbackground=colors["input"], foreground=colors["fg"])
    style.configure("Treeview", background=colors["panel"], fieldbackground=colors["panel"],
                    foreground=colors["fg"], rowheight=29)
    style.configure("Treeview.Heading", background=colors["bg"], foreground=colors["fg"])
    style.map("Treeview", background=[("selected", colors["selected"])],
              foreground=[("selected", colors["fg"])])
    return colors
