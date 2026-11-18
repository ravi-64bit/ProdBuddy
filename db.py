import sqlite3
import time

import config

conn = sqlite3.connect(config.DB_PATH)
conn.row_factory = sqlite3.Row  # rows work like dicts: row["title"]
conn.execute("PRAGMA journal_mode = WAL")  # safer if the app crashes mid-write
conn.execute("PRAGMA foreign_keys = ON")  # deleting a project/task deletes what's inside it

# ---------- tables ----------
conn.execute("CREATE TABLE IF NOT EXISTS projects (id INTEGER PRIMARY KEY, name TEXT)")
conn.execute(
    "CREATE TABLE IF NOT EXISTS tasks ("
    "id INTEGER PRIMARY KEY, "
    "project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE, "
    "title TEXT, done INTEGER DEFAULT 0)"
)

# Columns added after the first version. Runs on every start, but only adds the
# missing ones, so old databases upgrade themselves and nothing is lost.
NEW_TASK_COLUMNS = [
    ("parent_id", "INTEGER REFERENCES tasks(id) ON DELETE CASCADE"),  # set = this is a subtask
    ("due", "TEXT"),  # 'YYYY-MM-DD'
    ("notes", "TEXT DEFAULT ''"),
    ("tags", "TEXT DEFAULT ''"),  # 'work,home'
    ("seconds", "INTEGER DEFAULT 0"),  # tracked time
    ("timer_start", "REAL"),  # set while a timer is running
]
_have = {row["name"] for row in conn.execute("PRAGMA table_info(tasks)")}
for _name, _definition in NEW_TASK_COLUMNS:
    if _name not in _have:
        conn.execute(f"ALTER TABLE tasks ADD COLUMN {_name} {_definition}")

# A timer still "running" at startup means the app crashed. The normal exit stops it.
conn.execute("UPDATE tasks SET timer_start = NULL")
conn.commit()


# ---------- projects ----------
def get_projects():
    return conn.execute("SELECT id, name FROM projects ORDER BY id").fetchall()


def get_project(project_id):
    return conn.execute("SELECT id, name FROM projects WHERE id = ?", (project_id,)).fetchone()


def add_project(name):
    cur = conn.execute("INSERT INTO projects (name) VALUES (?)", (name,))
    conn.commit()
    return cur.lastrowid


def rename_project(project_id, name):
    conn.execute("UPDATE projects SET name = ? WHERE id = ?", (name, project_id))
    conn.commit()


def delete_project(project_id):
    conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()


# ---------- tasks ----------
def get_tasks(project_id):
    """All tasks of a project, subtasks included (they have parent_id set)."""
    return conn.execute("SELECT * FROM tasks WHERE project_id = ? ORDER BY id", (project_id,)).fetchall()


def get_task(task_id):
    return conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()


def get_due_tasks(today_iso):
    """Unfinished tasks from every project that are due today or earlier."""
    return conn.execute(
        "SELECT t.*, p.name AS project_name FROM tasks t "
        "JOIN projects p ON p.id = t.project_id "
        "WHERE t.done = 0 AND t.due IS NOT NULL AND t.due <= ? "
        "ORDER BY t.due, t.id",
        (today_iso,),
    ).fetchall()


def _insert_task(project_id, parent_id, title, done=0, due=None, notes="", tags="", seconds=0):
    """Inserts without committing, so imports can be one all-or-nothing transaction."""
    cur = conn.execute(
        "INSERT INTO tasks (project_id, parent_id, title, done, due, notes, tags, seconds) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (project_id, parent_id, title, done, due, notes, tags, seconds),
    )
    return cur.lastrowid


def add_task(project_id, title, parent_id=None, due=None, tags=""):
    task_id = _insert_task(project_id, parent_id, title, due=due, tags=tags)
    conn.commit()
    return task_id


EDITABLE = ("title", "due", "notes", "tags")


def update_task(task_id, **fields):
    """update_task(5, title="New", due="2026-12-01"). Only EDITABLE columns are allowed."""
    for key in fields:
        if key not in EDITABLE:
            raise ValueError(f"Can't edit '{key}'")
    if not fields:
        return
    columns = ", ".join(f"{key} = ?" for key in fields)
    conn.execute(f"UPDATE tasks SET {columns} WHERE id = ?", (*fields.values(), task_id))
    conn.commit()


def toggle_task(task_id):
    conn.execute("UPDATE tasks SET done = 1 - done WHERE id = ?", (task_id,))
    conn.commit()
    task = get_task(task_id)
    if task and task["done"] and task["timer_start"] is not None:
        stop_timer()  # finished tasks don't keep counting


def delete_task(task_id):
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))  # subtasks go with it
    conn.commit()


# ---------- timer (only one task is timed at a time) ----------
def stop_timer(now=None):
    """Adds the elapsed time to the running task and stops it."""
    if now is None:
        now = time.time()
    conn.execute(
        "UPDATE tasks SET seconds = COALESCE(seconds, 0) + MAX(0, CAST(? - timer_start AS INTEGER)), "
        "timer_start = NULL WHERE timer_start IS NOT NULL",
        (now,),
    )
    conn.commit()


def start_timer(task_id, now=None):
    if now is None:
        now = time.time()
    stop_timer(now)
    conn.execute("UPDATE tasks SET timer_start = ? WHERE id = ?", (now, task_id))
    conn.commit()


def running_task():
    return conn.execute("SELECT * FROM tasks WHERE timer_start IS NOT NULL").fetchone()


# ---------- export / import ----------
def _task_dict(row):
    return {
        "title": row["title"],
        "done": bool(row["done"]),
        "due": row["due"],
        "notes": row["notes"] or "",
        "tags": row["tags"] or "",
        "seconds": row["seconds"] or 0,
    }


def get_all():
    """Everything as plain lists/dicts (used for JSON export). Subtasks are nested."""
    result = []
    for project in get_projects():
        rows = get_tasks(project["id"])
        subtasks = {}
        for row in rows:
            if row["parent_id"] is not None:
                subtasks.setdefault(row["parent_id"], []).append(_task_dict(row))
        tasks = [
            {**_task_dict(row), "subtasks": subtasks.get(row["id"], [])}
            for row in rows
            if row["parent_id"] is None
        ]
        result.append({"name": project["name"], "tasks": tasks})
    return result


def _insert_task_tree(project_id, parent_id, task):
    task_id = _insert_task(
        project_id,
        parent_id,
        task["title"],
        done=int(task.get("done", False)),
        due=task.get("due"),
        notes=task.get("notes", ""),
        tags=task.get("tags", ""),
        seconds=task.get("seconds", 0),
    )
    for sub in task.get("subtasks", []):
        _insert_task_tree(project_id, task_id, sub)


def import_all(projects):
    """Add projects + tasks in ONE transaction: all saved, or nothing saved."""
    try:
        for p in projects:
            cur = conn.execute("INSERT INTO projects (name) VALUES (?)", (p["name"],))
            for task in p["tasks"]:
                _insert_task_tree(cur.lastrowid, None, task)
        conn.commit()
    except Exception:
        conn.rollback()
        raise