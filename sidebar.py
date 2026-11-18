"""Navigation sidebar for ProdBuddy."""
import tkinter as tk
from tkinter import simpledialog, messagebox

import db
import logic


class Sidebar(tk.Frame):
    def __init__(self, master, on_select, on_export, on_import, on_theme, dark=False):
        super().__init__(master, width=230, padx=12, pady=14)
        self.pack_propagate(False)
        self.on_select = on_select
        self.on_export = on_export
        self.on_import = on_import
        self.on_theme = on_theme
        self.dark = dark
        self.colors = None

        tk.Label(self, text="ProdBuddy", font=("Segoe UI", 17, "bold")).pack(anchor="w", pady=(2, 18))
        tk.Button(self, text="Today", anchor="w", command=lambda: self.select("today")).pack(fill="x", pady=2)
        tk.Button(self, text="All tasks", anchor="w", command=lambda: self.select("all")).pack(fill="x", pady=2)
        tk.Label(self, text="PROJECTS", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(20, 6))
        self.projects = tk.Listbox(self, height=15, activestyle="none", borderwidth=0, highlightthickness=0)
        self.projects.pack(fill="both", expand=True)
        self.projects.bind("<<ListboxSelect>>", self._project_selected)
        actions = tk.Frame(self)
        actions.pack(fill="x", pady=(8, 4))
        tk.Button(actions, text="+ Project", command=self.add_project).pack(side="left", fill="x", expand=True)
        tk.Button(actions, text="Rename", command=self.rename_project).pack(side="left", padx=(5, 0))
        tk.Button(actions, text="Delete", command=self.delete_project).pack(side="left", padx=(5, 0))
        tk.Button(self, text="Export data", command=self.on_export).pack(fill="x", pady=(12, 3))
        tk.Button(self, text="Import data", command=self.on_import).pack(fill="x", pady=3)
        self.theme_button = tk.Button(self, text="Use light theme" if dark else "Use dark theme",
                                       command=self.toggle_theme)
        self.theme_button.pack(fill="x", pady=(3, 0))
        self._project_ids = []
        self.refresh()

    def select(self, view):
        self.projects.selection_clear(0, tk.END)
        self.on_select(view)

    def _project_selected(self, _event=None):
        selection = self.projects.curselection()
        if selection:
            index = selection[0]
            if index < len(self._project_ids):
                self.on_select(self._project_ids[index])

    def refresh(self, select=None):
        self.projects.delete(0, tk.END)
        rows = db.get_projects()
        self._project_ids = []
        for project in rows:
            self._project_ids.append(project["id"])
            self.projects.insert(tk.END, project["name"])
        if select not in (None, "today", "all"):
            try:
                index = self._project_ids.index(int(select))
                self.projects.selection_set(index)
            except (ValueError, TypeError):
                pass

    def refresh_today(self):
        # Kept as a small hook for the task panel after task changes.
        return None

    def add_project(self):
        name = simpledialog.askstring("New project", "Project name:", parent=self)
        if name and name.strip():
            project_id = db.add_project(name.strip())
            self.refresh(select=project_id)
            self.on_select(project_id)

    def _selected_project_id(self):
        selected = self.projects.curselection()
        return self._project_ids[selected[0]] if selected else None

    def rename_project(self):
        project_id = self._selected_project_id()
        if project_id is None:
            messagebox.showinfo("Select a project", "Choose a project first.", parent=self)
            return
        project = db.get_project(project_id)
        name = simpledialog.askstring("Rename project", "New name:", initialvalue=project["name"], parent=self)
        if name and name.strip():
            db.rename_project(project_id, name.strip())
            self.refresh(select=project_id)

    def delete_project(self):
        project_id = self._selected_project_id()
        if project_id is None:
            messagebox.showinfo("Select a project", "Choose a project first.", parent=self)
            return
        project = db.get_project(project_id)
        if messagebox.askyesno("Delete project", f"Delete '{project['name']}' and all its tasks?", parent=self):
            db.delete_project(project_id)
            self.refresh()
            self.on_select("today")

    def toggle_theme(self):
        self.dark = not self.dark
        self.theme_button.configure(text="Use light theme" if self.dark else "Use dark theme")
        self.on_theme(self.dark)

    def apply_colors(self, colors):
        self.colors = colors
        self.configure(bg=colors["panel"])
        for child in self.winfo_children():
            try:
                child.configure(bg=colors["panel"], fg=colors["fg"])
            except tk.TclError:
                pass
