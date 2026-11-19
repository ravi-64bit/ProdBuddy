import sys
import tkinter as tk
from tkinter import filedialog, messagebox

import db
import os
import errors
import logic
import settings
import theme
import transfer
from sidebar import Sidebar
from tasks_panel import TasksPanel


def shortcut(widget, key, func):
    """Bind Ctrl+<key>, also when Caps Lock is on."""
    for k in (key.lower(), key.upper()):
        widget.bind(f"<Control-{k}>", lambda event: func())


class App(tk.Tk):
    # tkinter calls this when any button/event handler crashes.
    # Without it, errors print to a console and the user sees nothing.
    def report_callback_exception(self, exc_type, exc, tb):
        errors.report(exc_type, exc, tb)

    def __init__(self):
        super().__init__()
        theme.setup(self)
        self.title("ProdBuddy")
        self.logo_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "assets",
            "logo.png"
        )
        self.logo_image=tk.PhotoImage(file=self.logo_path)
        self.iconphoto(True, self.logo_image)
        self.geometry(f"{theme.px(1100)}x{theme.px(720)}")
        self.minsize(theme.px(920), theme.px(560))

        self.settings = settings.load()
        self.colors = theme.apply(self, self.settings["dark"])

        self.sidebar = Sidebar(
            self,
            on_select=self.show,
            on_export=self.export_data,
            on_import=self.import_data,
            on_theme=self.set_dark,
            dark=self.settings["dark"],
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.apply_colors(self.colors)

        self.panel = TasksPanel(self, on_change=self.sidebar.refresh_today)
        self.panel.pack(side="left", fill="both", expand=True)
        self.panel.apply_colors(self.colors)

        start = self.first_view()
        self.sidebar.refresh(select=start)
        self.panel.show(start)

        shortcut(self, "n", self.panel.focus_quick_add)
        shortcut(self, "f", self.panel.focus_search)
        shortcut(self, "d", self.panel.toggle_done)
        shortcut(self, "t", self.panel.toggle_timer)
        shortcut(self, "e", self.panel.edit_task)
        self.bind("<F2>", lambda event: self.panel.edit_task())
        self.protocol("WM_DELETE_WINDOW", self.close)

    def first_view(self):
        """Open on Today if something is due, otherwise on the first project."""
        projects = db.get_projects()
        if projects and not db.get_due_tasks(logic.today_iso()):
            return projects[0]["id"]
        return "today"

    def show(self, view):
        self.panel.show(view)

    def set_dark(self, dark):
        self.settings["dark"] = dark
        settings.save(self.settings)
        self.colors = theme.apply(self, dark)
        self.sidebar.apply_colors(self.colors)
        self.panel.apply_colors(self.colors)

    def close(self):
        try:
            self.panel.save_notes()
            db.stop_timer()  # a running timer is counted up to now
        except Exception:
            errors.log(*sys.exc_info())  # never block the window from closing
        self.destroy()

    # ---------- export / import ----------
    def export_data(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
            initialfile="prodbuddy-export.json",
        )
        if path:
            transfer.export_json(path)
            messagebox.showinfo("Exported", f"Saved to:\n{path}")

    def import_data(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not path:
            return
        try:
            count = transfer.import_json(path)
        except ValueError as e:  # bad file: friendly message, nothing was imported
            messagebox.showerror("Import failed", str(e))
            return
        self.sidebar.refresh()
        self.panel.load()
        messagebox.showinfo("Imported", f"Added {count} project(s).")
