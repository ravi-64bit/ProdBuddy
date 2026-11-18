import datetime
import json

import db
import logic


def export_json(path):
    data = {"version": 2, "projects": db.get_all()}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _clean_task(t, project, allow_subtasks=True):
    """Checks one task from the file and returns a clean copy. Old (version 1) files
    only have title/done, so every newer field is optional."""
    if not isinstance(t, dict) or not isinstance(t.get("title"), str) or not t["title"].strip():
        raise ValueError(f"A task in '{project}' has no title.")
    title = t["title"].strip()

    due = t.get("due")
    if due is not None:
        try:
            due = datetime.datetime.strptime(due, "%Y-%m-%d").date().isoformat()
        except (TypeError, ValueError):
            raise ValueError(f"Task '{title}' has an invalid due date.")

    notes, tags = t.get("notes", ""), t.get("tags", "")
    if not isinstance(notes, str) or not isinstance(tags, str):
        raise ValueError(f"Task '{title}' has invalid notes or tags.")

    seconds = t.get("seconds", 0)
    if isinstance(seconds, bool) or not isinstance(seconds, int) or seconds < 0:
        raise ValueError(f"Task '{title}' has invalid tracked time.")

    subtasks = t.get("subtasks", [])
    if not isinstance(subtasks, list):
        raise ValueError(f"Subtasks of '{title}' are not a list.")
    if subtasks and not allow_subtasks:
        raise ValueError(f"'{title}' is a subtask, so it can't have subtasks.")

    return {
        "title": title,
        "done": bool(t.get("done", False)),
        "due": due,
        "notes": notes,
        "tags": logic.parse_tags(tags),
        "seconds": seconds,
        "subtasks": [_clean_task(s, project, allow_subtasks=False) for s in subtasks],
    }


def import_json(path):
    """Adds the file's projects to existing data. Returns how many were added.
    Raises ValueError with a readable message if the file is not valid."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except ValueError:  # covers broken JSON and non-text files
        raise ValueError("This file is not valid JSON.")

    if not isinstance(data, dict) or not isinstance(data.get("projects"), list):
        raise ValueError("This is not a ProdBuddy export file.")

    projects = []
    for p in data["projects"]:
        if not isinstance(p, dict) or not isinstance(p.get("name"), str) or not p["name"].strip():
            raise ValueError("A project in the file has no name.")
        name = p["name"].strip()
        tasks = p.get("tasks", [])
        if not isinstance(tasks, list):
            raise ValueError(f"Tasks for '{name}' are not a list.")
        projects.append({"name": name, "tasks": [_clean_task(t, name) for t in tasks]})

    db.import_all(projects)  # only touches the database after everything is validated
    return len(projects)