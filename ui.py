import sys
import tkinter as tk

import config
import db
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


def load_scaled_icon(rel_path, target_px=24):
    """Load a PNG with tk.PhotoImage and subsample cleanly without external deps."""
    path = config.resource_path(rel_path)
    try:
        img = tk.PhotoImage(file=path)
    except tk.TclError:
        return None
    w = max(1, img.width())
    factor = max(1, round(w / max(1, target_px)))
    if factor > 1:
        img = img.subsample(factor, factor)
    return img


class App(tk.Tk):
    def report_callback_exception(self, exc_type, exc, tb):
        errors.report(exc_type, exc, tb)

    def __init__(self):
        super().__init__()
        theme.setup(self)
        self.title("ProdBuddy")
        self.geometry(f"{theme.px(1160)}x{theme.px(740)}")
        self.minsize(theme.px(960), theme.px(580))

        self.icon_image = load_scaled_icon("assets/logo.png", target_px=theme.px(32))
        if self.icon_image is not None:
            try:
                self.iconphoto(True, self.icon_image)
            except tk.TclError:
                pass

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
        self.colors = theme.apply(self, dark)
        self.sidebar.apply_colors(self.colors)
        self.panel.apply_colors(self.colors)
        try:
            settings.save(self.settings)
        except Exception as exc:
            errors.log(*sys.exc_info())
            theme.show_message(
                self,
                "Settings not saved",
                f"Theme was applied, but saving settings failed:\n{exc}",
                kind="error",
            )

    def close(self):
        try:
            self.panel.stop_live_updates()
            self.panel.save_notes()
            db.stop_timer()
        except Exception:
            errors.log(*sys.exc_info())
        self.destroy()

    # ---------- export / import ----------
    def export_data(self):
        path = filedialog_save_json()
        if path:
            transfer.export_json(path)
            theme.show_message(self, "Exported", f"Saved to:\n{path}")

    def import_data(self):
        path = filedialog_open_json()
        if not path:
            return
        try:
            count = transfer.import_json(path)
        except ValueError as e:
            theme.show_message(self, "Import failed", str(e), kind="error")
            return
        self.sidebar.refresh()
        self.panel.load()
        theme.show_message(self, "Imported", f"Added {count} project(s).")


def filedialog_save_json():
    from tkinter import filedialog

    return filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON", "*.json")],
        initialfile="prodbuddy-export.json",
    )


def filedialog_open_json():
    from tkinter import filedialog

    return filedialog.askopenfilename(filetypes=[("JSON", "*.json")])