"""Main task workspace for ProdBuddy."""
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

import db
import logic


class TasksPanel(tk.Frame):
    def __init__(self, master, on_change=None):
        super().__init__(master, padx=18, pady=16)
        self.on_change = on_change or (lambda: None)
        self.view = "today"
        self._rows = []
        self._selected_task_id = None
        self._colors = None

        header = ttk.Frame(self)
        header.pack(fill="x")
        self.heading = ttk.Label(header, text="Today", font=("Segoe UI", 20, "bold"))
        self.heading.pack(side="left")
        self.summary = ttk.Label(header, text="", style="Muted.TLabel")
        self.summary.pack(side="right", padx=8)

        addrow = ttk.Frame(self)
        addrow.pack(fill="x", pady=(16, 8))
        self.quick_entry = ttk.Entry(addrow)
        self.quick_entry.pack(side="left", fill="x", expand=True)
        self.quick_entry.insert(0, "")
        self.quick_entry.bind("<Return>", lambda _e: self.add_task())
        ttk.Button(addrow, text="Add task", command=self.add_task).pack(side="left", padx=(8, 0))
        ttk.Button(addrow, text="Search", command=self.focus_search).pack(side="left", padx=(6, 0))

        self.search_entry = ttk.Entry(self)
        self.search_entry.pack(fill="x", pady=(0, 8))
        self.search_entry.insert(0, "")
        self.search_entry.bind("<KeyRelease>", lambda _e: self.load())

        columns = ("status", "title", "due", "tags", "time")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        for col, label, width in [
            ("status", "Done", 65), ("title", "Task", 360), ("due", "Due date", 115),
            ("tags", "Tags", 150), ("time", "Tracked", 100)
        ]:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="w")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._selection_changed)
        self.tree.bind("<Double-1>", lambda _e: self.edit_task())

        controls = ttk.Frame(self)
        controls.pack(fill="x", pady=(10, 4))
        for label, command in [
            ("Complete / reopen", self.toggle_done), ("Edit", self.edit_task),
            ("Delete", self.delete_task), ("Start / stop timer", self.toggle_timer),
            ("Task notes", self.edit_notes),
        ]:
            ttk.Button(controls, text=label, command=command).pack(side="left", padx=(0, 6))

        self.timer_label = ttk.Label(self, text="Select a task to manage it.", style="Muted.TLabel")
        self.timer_label.pack(anchor="w", pady=(5, 0))
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
            haystack = " ".join(str(task.get(k) or "") for k in ("title", "notes", "tags", "due")).lower()
            if query and query not in haystack:
                continue
            task_id = task["id"]
            self._rows.append(task)
            self.tree.insert("", "end", iid=str(task_id), values=(
                "✓" if task.get("done") else "○",
                task.get("title") or "",
                task.get("due") or "—",
                task.get("tags") or "",
                logic.format_duration(task.get("seconds", 0)),
            ))
        self.summary.configure(text=f"{len(self._rows)} tasks")
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
                messagebox.showinfo("Create a project", "Create a project before adding tasks.", parent=self)
                return
            if len(projects) == 1:
                project_id = projects[0]["id"]
            else:
                names = "\n".join(f"{p['id']}: {p['name']}" for p in projects)
                choice = simpledialog.askinteger("Choose project", f"Enter project ID:\n{names}", parent=self)
                if choice not in [p["id"] for p in projects]:
                    return
                project_id = choice
        else:
            project_id = int(self.view)
        db.add_task(project_id, title, due=logic.today_iso() if self.view == "today" else None)
        self.quick_entry.delete(0, tk.END)
        self.load()
        self.on_change()

    def toggle_done(self):
        task = self._current_task()
        if task:
            db.toggle_task(task["id"])
            self.load()
            self.on_change()

    def edit_task(self):
        task = self._current_task()
        if not task:
            return
        title = simpledialog.askstring("Edit task", "Task title:", initialvalue=task["title"], parent=self)
        if title and title.strip():
            db.update_task(task["id"], title=title.strip())
            self.load()

    def edit_notes(self):
        task = self._current_task()
        if not task:
            return
        notes = simpledialog.askstring("Task notes", "Notes:", initialvalue=task["notes"] or "", parent=self)
        if notes is not None:
            db.update_task(task["id"], notes=notes)

    def delete_task(self):
        task = self._current_task()
        if task and messagebox.askyesno("Delete task", f"Delete '{task['title']}' and its subtasks?", parent=self):
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
        self._refresh_timer_label()
