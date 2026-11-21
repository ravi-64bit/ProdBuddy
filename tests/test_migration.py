import importlib
import sqlite3

import config
import db


def test_old_schema_migrates_and_preserves_data(tmp_path, monkeypatch):
    old_db_path = tmp_path / "legacy_tracker.db"
    conn = sqlite3.connect(old_db_path)
    conn.execute("CREATE TABLE projects (id INTEGER PRIMARY KEY, name TEXT)")
    conn.execute(
        "CREATE TABLE tasks ("
        "id INTEGER PRIMARY KEY, "
        "project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE, "
        "title TEXT, done INTEGER DEFAULT 0)"
    )
    conn.execute("INSERT INTO projects (id, name) VALUES (1, 'registration'), (2, 'image gen')")
    conn.execute("INSERT INTO tasks (id, project_id, title, done) VALUES (1, 1, 'add a box', 0), (2, 2, 'add image', 1)")
    conn.commit()
    conn.close()

    monkeypatch.setattr(config, "DB_PATH", str(old_db_path))
    reloaded = importlib.reload(db)
    try:
        cols = {row["name"] for row in reloaded.conn.execute("PRAGMA table_info(tasks)")}
        for expected in ("parent_id", "due", "notes", "tags", "seconds", "timer_start"):
            assert expected in cols

        projects = [dict(p) for p in reloaded.get_projects()]
        assert projects == [{"id": 1, "name": "registration"}, {"id": 2, "name": "image gen"}]

        t1 = reloaded.get_task(1)
        assert t1["title"] == "add a box"
        assert t1["done"] == 0
        assert t1["notes"] == ""
        assert t1["tags"] == ""
        assert t1["seconds"] == 0
        assert t1["parent_id"] is None
    finally:
        monkeypatch.setattr(config, "DB_PATH", ":memory:")