import sqlite3

import config

conn = sqlite3.connect(config.DB_PATH)
conn.execute("PRAGMA journal_mode = WAL")  # safer if the app crashes mid-write
conn.execute("PRAGMA foreign_keys = ON")  # lets deleting a project delete its tasks

conn.execute("CREATE TABLE IF NOT EXISTS projects (id INTEGER PRIMARY KEY, name TEXT)")
conn.execute(
    "CREATE TABLE IF NOT EXISTS tasks ("
    "id INTEGER PRIMARY KEY, "
    "project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE, "
    "title TEXT, done INTEGER DEFAULT 0)"
)
conn.commit()


def get_projects():
    return conn.execute("SELECT id, name FROM projects").fetchall()


def add_project(name):
    conn.execute("INSERT INTO projects (name) VALUES (?)", (name,))
    conn.commit()


def delete_project(project_id):
    conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()


def get_tasks(project_id):
    return conn.execute(
        "SELECT id, title, done FROM tasks WHERE project_id = ?", (project_id,)
    ).fetchall()


def add_task(project_id, title):
    conn.execute("INSERT INTO tasks (project_id, title) VALUES (?, ?)", (project_id, title))
    conn.commit()


def toggle_task(task_id):
    conn.execute("UPDATE tasks SET done = 1 - done WHERE id = ?", (task_id,))
    conn.commit()


def get_all():
    """Everything as plain lists/dicts (used for JSON export)."""
    result = []
    for pid, name in get_projects():
        tasks = [{"title": t, "done": bool(d)} for _, t, d in get_tasks(pid)]
        result.append({"name": name, "tasks": tasks})
    return result


def import_all(projects):
    """Add projects + tasks in ONE transaction: all saved, or nothing saved."""
    try:
        for p in projects:
            cur = conn.execute("INSERT INTO projects (name) VALUES (?)", (p["name"],))
            for t in p["tasks"]:
                conn.execute(
                    "INSERT INTO tasks (project_id, title, done) VALUES (?, ?, ?)",
                    (cur.lastrowid, t["title"], int(t["done"])),
                )
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def delete_task(task_id):
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()