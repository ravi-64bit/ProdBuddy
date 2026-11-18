import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
from tkinter import font as tkfont

import db
import errors
import transfer


class App(tk.Tk):
    # tkinter calls this when any button/event handler crashes.
    # Without it, errors print to a console and the user sees nothing.
    def report_callback_exception(self, exc_type, exc, tb):
        errors.report(exc_type, exc, tb)

    def __init__(self):
        super().__init__()
        self.title("Project Tracker")
        self.geometry("700x450")

        self.project_ids = []   # project_ids[i] is the db id of listbox row i
        self.current_project = None

        self.build_projects_panel()
        self.build_tasks_panel()
        self.load_projects()

    # ---------- layout ----------
    def build_projects_panel(self):
        left = tk.Frame(self)
        left.pack(side="left", fill="y", padx=10, pady=10)

        tk.Label(left, text="Projects").pack()
        self.project_list = tk.Listbox(left, width=25, exportselection=False)
        self.project_list.pack(fill="y", expand=True)
        self.project_list.bind("<<ListboxSelect>>", self.on_project_select)

        tk.Button(left, text="Add Project", command=self.add_project).pack(fill="x")
        tk.Button(left, text="Delete Project", command=self.delete_project).pack(fill="x")
        tk.Button(left, text="Export JSON", command=self.export_data).pack(fill="x", pady=(10, 0))
        tk.Button(left, text="Import JSON", command=self.import_data).pack(fill="x")

    def build_tasks_panel(self):
        right = tk.Frame(self)
        right.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        tk.Label(right, text="Tasks (double-click to strike off)").pack()

        self.task_tree = ttk.Treeview(right, show="tree")
        self.task_tree.pack(fill="both", expand=True)
        self.task_tree.bind("<Double-1>", lambda e: self.toggle_task())

        # A "done" tag = grey text with a line through it
        strike = tkfont.Font(family="Segoe UI", size=10, overstrike=True)
        self.task_tree.tag_configure("done", font=strike, foreground="gray")

        tk.Button(right, text="Add Task", command=self.add_task).pack(side="left")
        tk.Button(right, text="Toggle Done", command=self.toggle_task).pack(side="left")
        tk.Button(right, text="Delete Task", command=self.delete_task).pack(side="left")

    # ---------- projects ----------
    def load_projects(self):
        self.project_list.delete(0, "end")
        self.project_ids = []
        for pid, name in db.get_projects():
            self.project_list.insert("end", name)
            self.project_ids.append(pid)
        self.load_tasks()

    def on_project_select(self, event):
        selected = self.project_list.curselection()
        if selected:
            self.current_project = self.project_ids[selected[0]]
            self.load_tasks()

    def add_project(self):
        name = simpledialog.askstring("New project", "Project name:")
        if name:
            db.add_project(name)
            self.load_projects()

    def delete_project(self):
        if self.current_project is None:
            return
        if messagebox.askyesno("Delete", "Delete this project and all its tasks?"):
            db.delete_project(self.current_project)
            self.current_project = None
            self.load_projects()

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
        self.load_projects()
        messagebox.showinfo("Imported", f"Added {count} project(s).")

    # ---------- tasks ----------
    def load_tasks(self):
        self.task_tree.delete(*self.task_tree.get_children())
        if self.current_project is None:
            return
        for tid, title, done in db.get_tasks(self.current_project):
            tags = ("done",) if done else ()
            self.task_tree.insert("", "end", iid=str(tid), text=title, tags=tags)

    def add_task(self):
        if self.current_project is None:
            messagebox.showinfo("Pick a project", "Select a project first.")
            return
        title = simpledialog.askstring("New task", "Task:")
        if title:
            db.add_task(self.current_project, title)
            self.load_tasks()

    def toggle_task(self):
        selected = self.task_tree.selection()
        if selected:
            db.toggle_task(int(selected[0]))
            self.load_tasks()

    def delete_task(self):
        selected = self.task_tree.selection()
        if selected:
            db.delete_task(int(selected[0]))
            self.load_tasks()