"""Main task workspace for ProdBuddy."""
import time
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont

import db
import logic
import theme


def _effective_seconds(task, now=None):
    if now is None:
        now = time.time()
    base = int(task.get("seconds") or 0)
    timer_start = task.get("timer_start")
    if timer_start is not None and not task.get("done"):
        try:
            base += max(0, int(now - float(timer_start)))
        except (TypeError, ValueError):
            pass
    return base


class TasksPanel(tk.Frame):
    def __init__(self, master, on_change=None):
        super().__init__(master, padx=theme.px(24), pady=theme.px(20))
        self.on_change = on_change or (lambda: None)
        self.view = "today"
        self._rows = []
        self._selected_task_id = None
        self._colors = None
        self._tick_job = None
        self._last_status_toggle_at = 0.0
        self._strike_font = tkfont.Font(family="Segoe UI", size=10, overstrike=True)
        self._running_font = tkfont.Font(family="Segoe UI", size=10, weight="bold")

        # Header
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, theme.px(14)))
        self.heading = ttk.Label(header, text="Today", style="Heading.TLabel")
        self.heading.pack(side="left")
        self.summary = ttk.Label(header, text="", style="Muted.TLabel")
        self.summary.pack(side="right", anchor="s", pady=(0, theme.px(4)))

        # Quick add + Tags + Search row
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", pady=(0, theme.px(12)))
        toolbar.columnconfigure(0, weight=3)
        toolbar.columnconfigure(2, weight=1)
        toolbar.columnconfigure(4, weight=2)

        self.quick_entry = ttk.Entry(toolbar)
        self.quick_entry.grid(row=0, column=0, sticky="ew")
        self.quick_entry.bind("<Return>", lambda _e: self.add_task())

        ttk.Button(
            toolbar, text="Add task", style="Primary.TButton", command=self.add_task
        ).grid(row=0, column=1, padx=(theme.px(8), theme.px(12)))

        ttk.Label(toolbar, text="Tags:", style="Muted.TLabel").grid(
            row=0, column=2, sticky="e", padx=(0, theme.px(4))
        )
        self.tags_entry = ttk.Entry(toolbar, width=14)
        self.tags_entry.grid(row=0, column=3, sticky="ew", padx=(0, theme.px(12)))
        self.tags_entry.bind("<Return>", lambda _e: self.add_task())

        search_frame = ttk.Frame(toolbar)
        search_frame.grid(row=0, column=4, sticky="ew")
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

        columns = ("status", "project", "title", "due", "tags", "time")
        self.tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", selectmode="browse"
        )
        col_specs = [
            ("status", "Done", theme.px(60), False, "center"),
            ("project", "Project", theme.px(120), False, "w"),
            ("title", "Task", theme.px(300), True, "w"),
            ("due", "Due date", theme.px(110), False, "center"),
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
        self.tree.bind("<Double-1>", self._double_click_row)

        # Action bar
        controls = ttk.Frame(self)
        controls.pack(fill="x", pady=(theme.px(12), theme.px(6)))

        actions = [
            ("Complete / reopen", self.toggle_done, "TButton"),
            ("+ Subtask", self.add_subtask, "TButton"),
            ("Set due date", self.edit_due_date, "TButton"),
            ("Edit / tags", self.edit_task, "TButton"),
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
        self._schedule_tick()

    def _schedule_tick(self):
        if self._tick_job is not None:
            try:
                self.after_cancel(self._tick_job)
            except tk.TclError:
                pass
        try:
            self._tick_job = self.after(1000, self._on_tick)
        except tk.TclError:
            self._tick_job = None

    def stop_live_updates(self):
        if self._tick_job is not None:
            try:
                self.after_cancel(self._tick_job)
            except tk.TclError:
                pass
            self._tick_job = None

    def _on_tick(self):
        self._tick_job = None
        running = db.running_task()
        if running is not None:
            self._refresh_live_timer_cells()
        self._refresh_timer_label()
        self._schedule_tick()

    def _refresh_live_timer_cells(self):
        if not hasattr(self, "tree"):
            return
        now = time.time()
        for task in self._rows:
            iid = str(task["id"])
            if self.tree.exists(iid):
                formatted = logic.format_duration(_effective_seconds(task, now=now))
                self.tree.set(iid, "time", formatted)

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
            elapsed = logic.format_duration(_effective_seconds(dict(running)))
            self.timer_label.configure(
                text=f"Timer running: {running['title']} ({elapsed})"
            )
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

    def _ordered_project_tasks(self, project_id, project_name):
        rows = [dict(r) for r in db.get_tasks(project_id)]
        for r in rows:
            r["project_name"] = project_name
        children_by_parent = {}
        roots = []
        row_ids = {r["id"] for r in rows}
        for r in rows:
            pid = r.get("parent_id")
            if pid is None or pid not in row_ids:
                roots.append(r)
            else:
                children_by_parent.setdefault(pid, []).append(r)

        ordered = []
        for root in roots:
            root["_depth"] = 0
            ordered.append(root)
            for child in children_by_parent.get(root["id"], []):
                child["_depth"] = 1
                ordered.append(child)
        return ordered

    def _get_rows(self):
        projects = {p["id"]: p["name"] for p in db.get_projects()}
        if self.view == "today":
            due_rows = []
            for r in db.get_due_tasks(logic.today_iso()):
                item = dict(r)
                item["project_name"] = item.get("project_name") or projects.get(item["project_id"], "")
                item["_depth"] = 1 if item.get("parent_id") is not None else 0
                due_rows.append(item)
            return due_rows
        if self.view == "all":
            result = []
            for p in db.get_projects():
                result.extend(self._ordered_project_tasks(p["id"], p["name"]))
            return result
        pid = int(self.view)
        return self._ordered_project_tasks(pid, projects.get(pid, ""))

    def load(self):
        if not hasattr(self, "tree"):
            return
        query = self.search_entry.get().strip().lower() if hasattr(self, "search_entry") else ""
        self.tree.delete(*self.tree.get_children())
        self._rows = []
        now = time.time()
        for task in self._get_rows():
            haystack = " ".join(
                str(task.get(k) or "") for k in ("title", "notes", "tags", "due", "project_name")
            ).lower()
            if query and query not in haystack:
                continue
            task_id = task["id"]
            self._rows.append(task)

            is_done = bool(task.get("done"))
            is_running = task.get("timer_start") is not None and not is_done
            row_tags = []
            if is_done:
                row_tags.append("done")
            if is_running:
                row_tags.append("running")

            prefix = "  ↳ " if task.get("_depth", 0) > 0 else ""
            title_display = f"{prefix}{task.get('title') or ''}"
            formatted_tags = ", ".join(
                f"#{t}" for t in (task.get("tags") or "").split(",") if t
            )

            self.tree.insert(
                "",
                "end",
                iid=str(task_id),
                tags=tuple(row_tags),
                values=(
                    "✓" if is_done else "○",
                    task.get("project_name") or "",
                    title_display,
                    task.get("due") or "—",
                    formatted_tags,
                    logic.format_duration(_effective_seconds(task, now=now)),
                ),
            )
        count = len(self._rows)
        self.summary.configure(text=f"{count} task" if count == 1 else f"{count} tasks")
        if self._selected_task_id is not None and self.tree.exists(str(self._selected_task_id)):
            self.tree.selection_set(str(self._selected_task_id))
        self._refresh_timer_label()

    def _current_task(self):
        if self._selected_task_id is None:
            theme.show_message(self, "Select a task", "Choose a task first.")
            return None
        return db.get_task(self._selected_task_id)

    def _resolve_project_for_new_task(self):
        if self.view not in ("today", "all"):
            return int(self.view)
        projects = db.get_projects()
        if not projects:
            theme.show_message(
                self, "Create a project", "Create a project before adding tasks."
            )
            return None
        if len(projects) == 1:
            return projects[0]["id"]
        names = [p["name"] for p in projects]
        idx = theme.ask_choice(
            self, "Choose project", "Select project for this task:", names, default_index=0
        )
        if idx is None:
            return None
        return projects[idx]["id"]

    def add_task(self):
        title = self.quick_entry.get().strip()
        if not title:
            return
        project_id = self._resolve_project_for_new_task()
        if project_id is None:
            return
        raw_tags = self.tags_entry.get() if hasattr(self, "tags_entry") else ""
        try:
            tags = logic.parse_tags(raw_tags)
        except ValueError as exc:
            theme.show_message(self, "Invalid tags", str(exc), kind="error")
            return
        db.add_task(
            project_id,
            title,
            due=logic.today_iso() if self.view == "today" else None,
            tags=tags,
        )
        self.quick_entry.delete(0, tk.END)
        if hasattr(self, "tags_entry"):
            self.tags_entry.delete(0, tk.END)
        self.load()
        self.on_change()

    def add_subtask(self):
        parent = self._current_task()
        if not parent:
            return
        parent_id = parent["parent_id"] if parent["parent_id"] is not None else parent["id"]
        sub_title = theme.ask_text(self, "New subtask", f"Subtask for '{parent['title']}':")
        if not sub_title or not sub_title.strip():
            return
        db.add_task(
            parent["project_id"],
            sub_title.strip(),
            parent_id=parent_id,
            due=parent["due"],
            tags=parent["tags"] or "",
        )
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
        now = time.monotonic()
        if now - self._last_status_toggle_at < 0.25:
            return "break"
        self._last_status_toggle_at = now
        try:
            self._selected_task_id = int(item)
        except (ValueError, TypeError):
            return
        self.tree.selection_set(item)
        db.toggle_task(self._selected_task_id)
        self.load()
        self.on_change()
        return "break"

    def _double_click_row(self, event):
        if self.tree.identify_column(event.x) == "#1":
            return "break"
        self.edit_task()

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
        value = theme.ask_text(
            self,
            "Set due date",
            "Enter due date (YYYY-MM-DD). Leave blank to clear it:",
            initialvalue=task["due"] or "",
        )
        if value is None:
            return
        try:
            due = logic.valid_date(value)
        except ValueError as exc:
            theme.show_message(self, "Invalid date", str(exc), kind="error")
            return
        db.update_task(task["id"], due=due)
        self.load()
        self.on_change()

    def edit_task(self):
        task = self._current_task()
        if not task:
            return
        title = theme.ask_text(
            self, "Edit task", "Task title:", initialvalue=task["title"]
        )
        if title is None:
            return
        if not title.strip():
            return
        raw_tags = theme.ask_text(
            self,
            "Edit tags",
            "Tags (comma-separated, e.g. work, urgent):",
            initialvalue=task["tags"] or "",
        )
        if raw_tags is None:
            db.update_task(task["id"], title=title.strip())
            self.load()
            return
        try:
            tags = logic.parse_tags(raw_tags)
        except ValueError as exc:
            theme.show_message(self, "Invalid tags", str(exc), kind="error")
            return
        db.update_task(task["id"], title=title.strip(), tags=tags)
        self.load()

    def edit_notes(self):
        task = self._current_task()
        if not task:
            return
        notes = theme.ask_notes(
            self, "Task notes", f"Notes for '{task['title']}':", initialvalue=task["notes"] or ""
        )
        if notes is not None:
            db.update_task(task["id"], notes=notes)

    def delete_task(self):
        task = self._current_task()
        if task and theme.ask_yes_no(
            self, "Delete task", f"Delete '{task['title']}' and its subtasks?"
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
        return None

    def apply_colors(self, colors):
        self._colors = colors
        self.configure(bg=colors["bg"])
        self.tree.tag_configure("done", foreground=colors["muted"], font=self._strike_font)
        self.tree.tag_configure("running", foreground=colors["success"], font=self._running_font)
        self._refresh_timer_label()