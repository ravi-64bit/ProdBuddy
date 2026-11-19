"""Main task workspace for ProdBuddy."""
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

import db
import logic
import theme


class TasksPanel(tk.Frame):
    def __init__(self, master, on_change=None):
        super().__init__(master, padx=theme.px(24), pady=theme.px(20))
        self.on_change = on_change or (lambda: None)
        self.view = "today"
        self._rows = []
        self._selected_task_id = None
        self._colors = None

        # Header
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, theme.px(14)))
        self.heading = ttk.Label(header, text="Today", style="Heading.TLabel")
        self.heading.pack(side="left")
        self.summary = ttk.Label(header, text="", style="Muted.TLabel")
        self.summary.pack(side="right", anchor="s", pady=(0, theme.px(4)))

        # Quick add + Search row
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", pady=(0, theme.px(12)))
        toolbar.columnconfigure(0, weight=3)
        toolbar.columnconfigure(2, weight=2)

        self.quick_entry = ttk.Entry(toolbar)
        self.quick_entry.grid(row=0, column=0, sticky="ew")
        self.quick_entry.bind("<Return>", lambda _e: self.add_task())

        ttk.Button(
            toolbar, text="Add task", style="Primary.TButton", command=self.add_task
        ).grid(row=0, column=1, padx=(theme.px(8), theme.px(16)))

        search_frame = ttk.Frame(toolbar)
        search_frame.grid(row=0, column=2, sticky="ew")
        search_frame.columnconfigure(1, weight=1)

        ttk.Label(search_frame, text="Filter:", style="Muted.TLabel").grid(
            row=0, column=0, padx=(0, theme.px(6))
        )
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.grid(row=0, column=1, sticky="ew")
        self.search_entry.bind("<KeyRelease>", lambda _e: self.load())

        # Task table with scrollbar
        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True)

        columns = ("status", "title", "due", "tags", "time")
        self.tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", selectmode="browse"
        )
        col_specs = [
            ("status", "Done", theme.px(64), False, "center"),
            ("title", "Task", theme.px(320), True, "w"),
            ("due", "Due date", theme.px(115), False, "center"),
            ("tags", "Tags", theme.px(140), False, "w"),
            ("time", "Tracked", theme.px(95), False, "e"),
        ]
        for col, label, width, stretch, anchor in col_specs:
            self.tree.heading(col, text=label, anchor=anchor)
            self.tree.column(
                col, width=width, minwidth=width, stretch=stretch, anchor=anchor
            )

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self._selection_changed)
        self.tree.bind("<Button-1>", self._click_status)
        self.tree.bind("<Double-1>", lambda _e: self.edit_task())

        # Action bar
        controls = ttk.Frame(self)
        controls.pack(fill="x", pady=(theme.px(12), theme.px(6)))

        actions = [
            ("Complete / reopen", self.toggle_done, "TButton"),
            ("Set due date", self.edit_due_date, "TButton"),
            ("Edit", self.edit_task, "TButton"),
            ("Task notes", self.edit_notes, "TButton"),
            ("Start / stop timer", self.toggle_timer, "TButton"),
            ("Delete", self.delete_task, "Danger.TButton"),
        ]
        for idx, (label, command, btn_style) in enumerate(actions):
            controls.columnconfigure(idx, weight=1)
            padx = (0, theme.px(6)) if idx < len(actions) - 1 else (0, 0)
            ttk.Button(controls, text=label, style=btn_style, command=command).grid(
                row=0, column=idx, sticky="ew", padx=padx
            )

        # Status bar
        status_bar = ttk.Frame(self)
        status_bar.pack(fill="x", pady=(theme.px(4), 0))
        self.timer_label = ttk.Label(
            status_bar, text="Select a task to manage it.", style="Muted.TLabel"
        )
        self.timer_label.pack(side="left")

        self.load()

    def _selection_changed(self, _event=None):
        selection = self.tree.selection()
        if not selection:
            self._selected_task_id = None
            return
        try:
            self._selected_task_id = int(selection[0])
        except (ValueError, TypeError):
            self._selected_task_id = None
        self._refresh_timer_label()

    def _refresh_timer_label(self):
        running = db.running_task()
        if running:
            self.timer_label.configure(text=f"Timer running: {running['title']}")
        else:
            self.timer_label.configure(text="No timer running.")

    def show(self, view):
        self.view = view
        if view == "today":
            self.heading.configure(text="Today")
        elif view == "all":
            self.heading.configure(text="All tasks")
        else:
            project = db.get_project(view)
            self.heading.configure(text=project["name"] if project else "Project")
        self.load()

    def _get_rows(self):
        if self.view == "today":
            return list(db.get_due_tasks(logic.today_iso()))
        if self.view == "all":
            result = []
            for project in db.get_projects():
                for task in db.get_tasks(project["id"]):
                    result.append(task)
            return result
        return list(db.get_tasks(self.view))

    def load(self):
        if not hasattr(self, "tree"):
            return
        query = self.search_entry.get().strip().lower() if hasattr(self, "search_entry") else ""
        self.tree.delete(*self.tree.get_children())
        self._rows = []
        for row in self._get_rows():
            task = dict(row)
            haystack = " ".join(
                str(task.get(k) or "") for k in ("title", "notes", "tags", "due")
            ).lower()
            if query and query not in haystack:
                continue
            task_id = task["id"]
            self._rows.append(task)
            tags = ("done",) if task.get("done") else ()
            self.tree.insert(
                "",
                "end",
                iid=str(task_id),
                tags=tags,
                values=(
                    "✓" if task.get("done") else "○",
                    task.get("title") or "",
                    task.get("due") or "—",
                    task.get("tags") or "",
                    logic.format_duration(task.get("seconds", 0)),
                ),
            )
        count = len(self._rows)
        self.summary.configure(text=f"{count} task" if count == 1 else f"{count} tasks")
        if self._selected_task_id is not None and self.tree.exists(str(self._selected_task_id)):
            self.tree.selection_set(str(self._selected_task_id))
        self._refresh_timer_label()

    def _current_task(self):
        if self._selected_task_id is None:
            messagebox.showinfo("Select a task", "Choose a task first.", parent=self)
            return None
        return db.get_task(self._selected_task_id)

    def add_task(self):
        title = self.quick_entry.get().strip()
        if not title:
            return
        if self.view in ("today", "all"):
            projects = db.get_projects()
            if not projects:
                messagebox.showinfo(
                    "Create a project", "Create a project before adding tasks.", parent=self
                )
                return
            if len(projects) == 1:
                project_id = projects[0]["id"]
            else:
                names = "\n".join(f"{p['id']}: {p['name']}" for p in projects)
                choice = simpledialog.askinteger(
                    "Choose project", f"Enter project ID:\n{names}", parent=self
                )
                if choice not in [p["id"] for p in projects]:
                    return
                project_id = choice
        else:
            project_id = int(self.view)
        db.add_task(project_id, title, due=logic.today_iso() if self.view == "today" else None)
        self.quick_entry.delete(0, tk.END)
        self.load()
        self.on_change()

    def _click_status(self, event):
        """Allow the status circle in the first column to act like a checkbox."""
        if self.tree.identify_region(event.x, event.y) != "cell":
            return
        if self.tree.identify_column(event.x) != "#1":
            return
        item = self.tree.identify_row(event.y)
        if not item:
            return
        self._selected_task_id = int(item)
        db.toggle_task(self._selected_task_id)
        self.load()
        self.on_change()
        return "break"

    def toggle_done(self):
        task = self._current_task()
        if task:
            db.toggle_task(task["id"])
            self.load()
            self.on_change()

    def edit_due_date(self):
        task = self._current_task()
        if not task:
            return
        value = simpledialog.askstring(
            "Set due date",
            "Enter due date (YYYY-MM-DD). Leave blank to clear it:",
            initialvalue=task["due"] or "",
            parent=self,
        )
        if value is None:
            return
        try:
            due = logic.valid_date(value)
        except ValueError as exc:
            messagebox.showerror("Invalid date", str(exc), parent=self)
            return
        db.update_task(task["id"], due=due)
        self.load()
        self.on_change()

    def edit_task(self):
        task = self._current_task()
        if not task:
            return
        title = simpledialog.askstring(
            "Edit task", "Task title:", initialvalue=task["title"], parent=self
        )
        if title and title.strip():
            db.update_task(task["id"], title=title.strip())
            self.load()

    def edit_notes(self):
        task = self._current_task()
        if not task:
            return
        notes = simpledialog.askstring(
            "Task notes", "Notes:", initialvalue=task["notes"] or "", parent=self
        )
        if notes is not None:
            db.update_task(task["id"], notes=notes)

    def delete_task(self):
        task = self._current_task()
        if task and messagebox.askyesno(
            "Delete task", f"Delete '{task['title']}' and its subtasks?", parent=self
        ):
            db.delete_task(task["id"])
            self._selected_task_id = None
            self.load()
            self.on_change()

    def toggle_timer(self):
        task = self._current_task()
        if not task:
            return
        running = db.running_task()
        if running and running["id"] == task["id"]:
            db.stop_timer()
        else:
            db.start_timer(task["id"])
        self.load()

    def focus_quick_add(self):
        self.quick_entry.focus_set()

    def focus_search(self):
        self.search_entry.focus_set()
        self.search_entry.select_range(0, tk.END)

    def save_notes(self):
        # Notes are saved immediately by edit_notes; retained for clean shutdown API.
        return None

    def apply_colors(self, colors):
        self._colors = colors
        self.configure(bg=colors["bg"])
        self.tree.tag_configure("done", foreground=colors["muted"])
        self._refresh_timer_label()
