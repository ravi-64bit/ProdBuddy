"""Navigation sidebar for ProdBuddy."""
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

import db
import os
import theme


class Sidebar(tk.Frame):
    def __init__(self, master, on_select, on_export, on_import, on_theme, dark=False):
        super().__init__(
            master,
            width=theme.px(250),
            padx=theme.px(14),
            pady=theme.px(16),
            highlightthickness=1,
        )
        self.pack_propagate(False)
        self.on_select = on_select
        self.on_export = on_export
        self.on_import = on_import
        self.on_theme = on_theme
        self.dark = dark
        self.colors = None
        self._active_view = "today"
        self._project_ids = []

                # ---------- Brand / Logo ----------
        brand_frame = ttk.Frame(self, style="Sidebar.TFrame")
        brand_frame.pack(anchor="w", fill="x", pady=(0, theme.px(18)))

        logo_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "assets",
            "logo.png"
        )

        try:
            from PIL import Image, ImageTk

            logo_img = Image.open(logo_path)
            logo_img = logo_img.resize((36, 36), Image.Resampling.LANCZOS)

            self.logo_image = ImageTk.PhotoImage(logo_img)

            self.logo_label = ttk.Label(
                brand_frame,
                image=self.logo_image,
                style="SidebarBrand.TLabel"
            )
            self.logo_label.pack(side="left", padx=(0, theme.px(10)))

        except Exception as e:
            print(f"Could not load logo: {e}")

        self.brand_label = ttk.Label(
            brand_frame,
            text="ProdBuddy",
            style="SidebarBrand.TLabel"
        )
        self.brand_label.pack(side="left", pady=theme.px(5))

        self.today_btn = ttk.Button(
            self, text="Today", style="NavActive.TButton", command=lambda: self.select("today")
        )
        self.today_btn.pack(fill="x", pady=theme.px(2))

        self.all_btn = ttk.Button(
            self, text="All tasks", style="Nav.TButton", command=lambda: self.select("all")
        )
        self.all_btn.pack(fill="x", pady=theme.px(2))

        self.projects_label = ttk.Label(self, text="PROJECTS", style="SidebarSection.TLabel")
        self.projects_label.pack(anchor="w", pady=(theme.px(18), theme.px(6)))

        list_frame = ttk.Frame(self, style="Sidebar.TFrame")
        list_frame.pack(fill="both", expand=True)

        self.projects = tk.Listbox(
            list_frame,
            height=10,
            activestyle="none",
            borderwidth=0,
            highlightthickness=1,
            relief="flat",
            font=("Segoe UI", 10),
            exportselection=False,
        )
        self.projects.pack(fill="both", expand=True)
        self.projects.bind("<<ListboxSelect>>", self._project_selected)

        actions = ttk.Frame(self, style="Sidebar.TFrame")
        actions.pack(fill="x", pady=(theme.px(8), theme.px(10)))
        actions.columnconfigure(0, weight=1)
        actions.columnconfigure(1, weight=1)
        actions.columnconfigure(2, weight=1)

        ttk.Button(actions, text="+ New", style="Sidebar.TButton", command=self.add_project).grid(
            row=0, column=0, sticky="ew", padx=(0, theme.px(3))
        )
        ttk.Button(actions, text="Rename", style="Sidebar.TButton", command=self.rename_project).grid(
            row=0, column=1, sticky="ew", padx=theme.px(3)
        )
        ttk.Button(actions, text="Delete", style="Sidebar.TButton", command=self.delete_project).grid(
            row=0, column=2, sticky="ew", padx=(theme.px(3), 0)
        )

        footer = ttk.Frame(self, style="Sidebar.TFrame")
        footer.pack(fill="x", side="bottom")
        footer.columnconfigure(0, weight=1)
        footer.columnconfigure(1, weight=1)

        ttk.Button(footer, text="Export", style="Sidebar.TButton", command=self.on_export).grid(
            row=0, column=0, sticky="ew", padx=(0, theme.px(3)), pady=(0, theme.px(6))
        )
        ttk.Button(footer, text="Import", style="Sidebar.TButton", command=self.on_import).grid(
            row=0, column=1, sticky="ew", padx=(theme.px(3), 0), pady=(0, theme.px(6))
        )

        self.theme_button = ttk.Button(
            footer,
            text="Light theme" if dark else "Dark theme",
            style="Sidebar.TButton",
            command=self.toggle_theme,
        )
        self.theme_button.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.refresh(select="today")

    def _update_nav_styles(self):
        self.today_btn.configure(
            style="NavActive.TButton" if self._active_view == "today" else "Nav.TButton"
        )
        self.all_btn.configure(
            style="NavActive.TButton" if self._active_view == "all" else "Nav.TButton"
        )

    def select(self, view):
        self._active_view = view
        self.projects.selection_clear(0, tk.END)
        self._update_nav_styles()
        self.on_select(view)

    def _project_selected(self, _event=None):
        selection = self.projects.curselection()
        if selection:
            index = selection[0]
            if index < len(self._project_ids):
                project_id = self._project_ids[index]
                self._active_view = project_id
                self._update_nav_styles()
                self.on_select(project_id)

    def refresh(self, select=None):
        if select is not None:
            self._active_view = select
        self.projects.delete(0, tk.END)
        rows = db.get_projects()
        self._project_ids = []
        for project in rows:
            self._project_ids.append(project["id"])
            self.projects.insert(tk.END, f"  {project['name']}")
        if self._active_view not in (None, "today", "all"):
            try:
                index = self._project_ids.index(int(self._active_view))
                self.projects.selection_set(index)
            except (ValueError, TypeError):
                pass
        self._update_nav_styles()

    def refresh_today(self):
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
        name = simpledialog.askstring(
            "Rename project", "New name:", initialvalue=project["name"], parent=self
        )
        if name and name.strip():
            db.rename_project(project_id, name.strip())
            self.refresh(select=project_id)
            self.on_select(project_id)

    def delete_project(self):
        project_id = self._selected_project_id()
        if project_id is None:
            messagebox.showinfo("Select a project", "Choose a project first.", parent=self)
            return
        project = db.get_project(project_id)
        if messagebox.askyesno(
            "Delete project", f"Delete '{project['name']}' and all its tasks?", parent=self
        ):
            db.delete_project(project_id)
            self.refresh(select="today")
            self.on_select("today")

    def toggle_theme(self):
        self.dark = not self.dark
        self.theme_button.configure(text="Light theme" if self.dark else "Dark theme")
        self.on_theme(self.dark)

    def apply_colors(self, colors):
        self.colors = colors
        self.configure(
            bg=colors["sidebar"],
            highlightbackground=colors["border"],
            highlightcolor=colors["border"],
        )
        self.projects.configure(
            bg=colors["panel"],
            fg=colors["fg"],
            selectbackground=colors["selected"],
            selectforeground=colors["accent"],
            highlightbackground=colors["border"],
            highlightcolor=colors["accent"],
        )
        self._update_nav_styles()
