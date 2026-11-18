import pytest

import db


def make_project(name="P"):
    db.add_project(name)
    return db.get_projects()[-1][0]  # id of the newest project


def test_add_and_list_projects():
    make_project("A")
    make_project("B")
    assert [name for _, name in db.get_projects()] == ["A", "B"]


def test_new_task_is_not_done():
    pid = make_project()
    db.add_task(pid, "write tests")
    assert [(t, d) for _, t, d in db.get_tasks(pid)] == [("write tests", 0)]


def test_toggle_task_twice_returns_to_not_done():
    pid = make_project()
    db.add_task(pid, "x")
    tid = db.get_tasks(pid)[0][0]

    db.toggle_task(tid)
    assert db.get_tasks(pid)[0][2] == 1
    db.toggle_task(tid)
    assert db.get_tasks(pid)[0][2] == 0


def test_delete_task():
    pid = make_project()
    db.add_task(pid, "x")
    db.delete_task(db.get_tasks(pid)[0][0])
    assert db.get_tasks(pid) == []


def test_tasks_stay_in_their_own_project():
    a, b = make_project("A"), make_project("B")
    db.add_task(a, "only in A")
    assert db.get_tasks(b) == []


def test_delete_project_also_deletes_its_tasks():
    pid = make_project()
    db.add_task(pid, "x")
    db.delete_project(pid)
    assert db.get_projects() == []
    assert db.conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0] == 0


def test_unicode_and_quotes_are_stored_safely():
    pid = make_project("Café ☕ ' \" ; DROP TABLE tasks;--")
    db.add_task(pid, "it's \"fine\"")
    assert db.get_projects()[0][1] == "Café ☕ ' \" ; DROP TABLE tasks;--"
    assert db.get_tasks(pid)[0][1] == "it's \"fine\""


def test_get_all_shape():
    pid = make_project("A")
    db.add_task(pid, "t1")
    db.toggle_task(db.get_tasks(pid)[0][0])
    assert db.get_all() == [{"name": "A", "tasks": [{"title": "t1", "done": True}]}]


def test_import_all_adds_projects_and_tasks():
    db.import_all([{"name": "A", "tasks": [{"title": "t", "done": True}]}])
    assert db.get_all() == [{"name": "A", "tasks": [{"title": "t", "done": True}]}]


def test_import_all_is_all_or_nothing():
    good = {"name": "Good", "tasks": [{"title": "t", "done": False}]}
    broken = {"name": "Broken", "tasks": [{"done": False}]}  # task has no title
    with pytest.raises(KeyError):
        db.import_all([good, broken])
    assert db.get_all() == []  # "Good" must not be left behind
