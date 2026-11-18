import json

import db


def export_json(path):
    data = {"version": 1, "projects": db.get_all()}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


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
        tasks = p.get("tasks", [])
        if not isinstance(tasks, list):
            raise ValueError(f"Tasks for '{p['name']}' are not a list.")
        clean = []
        for t in tasks:
            if not isinstance(t, dict) or not isinstance(t.get("title"), str):
                raise ValueError(f"A task in '{p['name']}' has no title.")
            clean.append({"title": t["title"], "done": bool(t.get("done", False))})
        projects.append({"name": p["name"].strip(), "tasks": clean})

    db.import_all(projects)  # only touches the database after everything is validated
    return len(projects)
