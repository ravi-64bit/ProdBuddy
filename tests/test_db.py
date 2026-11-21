import pytest

import db


def make_project(name="P"):
    return db.add_project(name)


def titles(project_id):
    return [t["title"] for t in db.get_tasks(project_id)]


# ---------- projects ----------
def test_add_and_list_projects():
    make_project("A")
    make_project("B")
    assert [p["name"] for p in db.get_projects()] == ["A", "B"]


def test_rename_project():
    pid = make_project("Old")
    db.rename_project(pid, "New")
    assert db.get_project(pid)["name"] == "New"


def test_get_project_missing_returns_none():
    assert db.get_project(999) is None


def test_delete_project_also_deletes_its_tasks_and_subtasks():
    pid = make_project()
    parent = db.add_task(pid, "parent")
    db.add_task(pid, "child", parent_id=parent)
    db.delete_project(pid)
    assert db.get_projects() == []
    assert db.conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0] == 0


# ---------- tasks ----------
def test_new_task_defaults():
    pid = make_project()
    db.add_task(pid, "write tests")
    task = db.get_tasks(pid)[0]
    assert (task["title"], task["done"], task["due"], task["notes"], task["tags"], task["seconds"]) == (
        "write tests", 0, None, "", "", 0,
    )
    assert task["parent_id"] is None and task["timer_start"] is None


def test_add_task_with_due_and_tags():
    pid = make_project()
    task_id = db.add_task(pid, "x", due="2026-12-01", tags="a,b")
    task = db.get_task(task_id)
    assert (task["due"], task["tags"]) == ("2026-12-01", "a,b")


def test_toggle_task_twice_returns_to_not_done():
    pid = make_project()
    tid = db.add_task(pid, "x")
    db.toggle_task(tid)
    assert db.get_task(tid)["done"] == 1
    db.toggle_task(tid)
    assert db.get_task(tid)["done"] == 0


def test_update_task_changes_only_given_fields():
    pid = make_project()
    tid = db.add_task(pid, "old", tags="x")
    db.update_task(tid, title="new", notes="some notes", due="2026-01-05")
    task = db.get_task(tid)
    assert (task["title"], task["notes"], task["due"], task["tags"]) == ("new", "some notes", "2026-01-05", "x")


def test_update_task_rejects_other_columns():
    tid = db.add_task(make_project(), "x")
    with pytest.raises(ValueError):
        db.update_task(tid, done=1)
    with pytest.raises(ValueError):
        db.update_task(tid, **{"title = 'hacked' --": "x"})


def test_delete_task_deletes_its_subtasks():
    pid = make_project()
    parent = db.add_task(pid, "parent")
    db.add_task(pid, "child", parent_id=parent)
    db.add_task(pid, "other")
    db.delete_task(parent)
    assert titles(pid) == ["other"]


def test_tasks_stay_in_their_own_project():
    a, b = make_project("A"), make_project("B")
    db.add_task(a, "only in A")
    assert db.get_tasks(b) == []


def test_unicode_and_quotes_are_stored_safely():
    pid = make_project("Café ☕ ' \" ; DROP TABLE tasks;--")
    db.add_task(pid, "it's \"fine\"")
    assert db.get_projects()[0]["name"] == "Café ☕ ' \" ; DROP TABLE tasks;--"
    assert titles(pid) == ["it's \"fine\""]


# ---------- today view ----------
def test_due_tasks_include_today_and_overdue_but_not_future_or_done_or_undated():
    a, b = make_project("A"), make_project("B")
    db.add_task(a, "overdue", due="2026-11-10")
    db.add_task(b, "today", due="2026-11-12")
    db.add_task(a, "future", due="2026-11-13")
    db.add_task(a, "no date")
    done = db.add_task(a, "done", due="2026-11-11")
    db.toggle_task(done)

    rows = db.get_due_tasks("2026-11-12")
    assert [(r["title"], r["project_name"]) for r in rows] == [("overdue", "A"), ("today", "B")]


def test_due_tasks_include_subtasks():
    pid = make_project()
    parent = db.add_task(pid, "parent")
    db.add_task(pid, "child", parent_id=parent, due="2026-11-12")
    assert [r["title"] for r in db.get_due_tasks("2026-11-12")] == ["child"]


# ---------- timer ----------
def test_timer_adds_elapsed_seconds():
    tid = db.add_task(make_project(), "x")
    db.start_timer(tid, now=1000)
    assert db.running_task()["id"] == tid
    db.stop_timer(now=1090)
    task = db.get_task(tid)
    assert (task["seconds"], task["timer_start"]) == (90, None)
    assert db.running_task() is None


def test_timer_accumulates_over_several_runs():
    tid = db.add_task(make_project(), "x")
    db.start_timer(tid, now=0)
    db.stop_timer(now=60)
    db.start_timer(tid, now=100)
    db.stop_timer(now=130)
    assert db.get_task(tid)["seconds"] == 90


def test_starting_a_second_timer_stops_the_first():
    pid = make_project()
    a, b = db.add_task(pid, "a"), db.add_task(pid, "b")
    db.start_timer(a, now=0)
    db.start_timer(b, now=50)
    assert db.get_task(a)["seconds"] == 50
    assert db.running_task()["id"] == b


def test_finishing_a_task_stops_its_timer():
    tid = db.add_task(make_project(), "x")
    db.start_timer(tid)
    db.toggle_task(tid)
    assert db.running_task() is None


def test_stop_timer_with_nothing_running_is_fine():
    db.stop_timer()


def test_clock_going_backwards_never_removes_time():
    tid = db.add_task(make_project(), "x")
    db.start_timer(tid, now=1000)
    db.stop_timer(now=900)
    assert db.get_task(tid)["seconds"] == 0


def test_deleting_the_running_task_leaves_no_timer_behind():
    tid = db.add_task(make_project(), "x")
    db.start_timer(tid)
    db.delete_task(tid)
    assert db.running_task() is None


# ---------- export / import ----------
def test_get_all_nests_subtasks():
    pid = make_project("A")
    parent = db.add_task(pid, "parent", due="2026-12-01", tags="x")
    db.add_task(pid, "child", parent_id=parent)
    db.update_task(parent, notes="n")
    db.toggle_task(parent)

    assert db.get_all() == [
        {
            "name": "A",
            "tasks": [
                {
                    "title": "parent", "done": True, "due": "2026-12-01", "notes": "n", "tags": "x", "seconds": 0,
                    "subtasks": [{"title": "child", "done": False, "due": None, "notes": "", "tags": "", "seconds": 0}],
                }
            ],
        }
    ]


def test_import_all_adds_projects_tasks_and_subtasks():
    data = [{"name": "A", "tasks": [{"title": "t", "done": True, "subtasks": [{"title": "s"}]}]}]
    db.import_all(data)
    pid = db.get_projects()[0]["id"]
    tasks = db.get_tasks(pid)
    assert [(t["title"], t["done"]) for t in tasks] == [("t", 1), ("s", 0)]
    assert tasks[1]["parent_id"] == tasks[0]["id"]


def test_import_all_is_all_or_nothing():
    good = {"name": "Good", "tasks": [{"title": "t"}]}
    broken = {"name": "Broken", "tasks": [{"done": False}]}  # task has no title
    with pytest.raises(KeyError):
        db.import_all([good, broken])
    assert db.get_all() == []  # "Good" must not be left behind