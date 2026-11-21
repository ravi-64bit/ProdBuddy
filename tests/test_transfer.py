import json

import pytest

import db
import transfer


def sample():
    db.import_all([{
        "name": "Café ☕",
        "tasks": [{
            "title": "a", "done": True, "due": "2026-12-01", "notes": "some\nnotes", "tags": "work,home", "seconds": 90,
            "subtasks": [{"title": "sub", "done": False}],
        }, {"title": "b"}],
    }])


def test_export_then_import_roundtrip(tmp_path):
    sample()
    file = tmp_path / "out.json"

    transfer.export_json(file)
    assert json.loads(file.read_text(encoding="utf-8"))["version"] == 2

    assert transfer.import_json(file) == 1
    first, second = db.get_all()  # import adds, never replaces
    assert first == second
    assert first["tasks"][0]["subtasks"][0]["title"] == "sub"
    assert first["tasks"][0]["seconds"] == 90


def test_old_version_1_file_still_imports(tmp_path):
    file = tmp_path / "v1.json"
    file.write_text(json.dumps({"version": 1, "projects": [{"name": "A", "tasks": [{"title": "t", "done": True}]}]}))
    transfer.import_json(file)
    assert db.get_all() == [{"name": "A", "tasks": [
        {"title": "t", "done": True, "due": None, "notes": "", "tags": "", "seconds": 0, "subtasks": []}]}]


def test_import_missing_done_defaults_to_false(tmp_path):
    file = tmp_path / "in.json"
    file.write_text(json.dumps({"projects": [{"name": "A", "tasks": [{"title": "t"}]}]}))
    transfer.import_json(file)
    assert db.get_all()[0]["tasks"][0]["done"] is False


def test_import_project_without_tasks_key(tmp_path):
    file = tmp_path / "in.json"
    file.write_text(json.dumps({"projects": [{"name": "A"}]}))
    transfer.import_json(file)
    assert db.get_all() == [{"name": "A", "tasks": []}]


def test_import_cleans_tags_and_dates(tmp_path):
    file = tmp_path / "in.json"
    file.write_text(json.dumps({"projects": [{"name": "A", "tasks": [{"title": "t", "tags": "Work, #Home", "due": "2026-1-5"}]}]}))
    transfer.import_json(file)
    task = db.get_all()[0]["tasks"][0]
    assert (task["tags"], task["due"]) == ("work,home", "2026-01-05")


def bad_task(**fields):
    return json.dumps({"projects": [{"name": "X", "tasks": [{"title": "ok"}, {"title": "bad", **fields}]}]})


@pytest.mark.parametrize(
    "content, message",
    [
        ("not json", "not valid JSON"),
        ("[1, 2]", "not a ProdBuddy export"),
        ('{"projects": "nope"}', "not a ProdBuddy export"),
        ('{"projects": [{"name": "  "}]}', "no name"),
        ('{"projects": [{"name": "X", "tasks": "nope"}]}', "not a list"),
        ('{"projects": [{"name": "X", "tasks": [{"nope": 1}]}]}', "no title"),
        ('{"projects": [{"name": "X", "tasks": [{"title": "  "}]}]}', "no title"),
        (bad_task(due="tomorrow"), "invalid due date"),
        (bad_task(due=5), "invalid due date"),
        (bad_task(seconds=-1), "invalid tracked time"),
        (bad_task(seconds="10"), "invalid tracked time"),
        (bad_task(seconds=True), "invalid tracked time"),
        (bad_task(notes=5), "invalid notes or tags"),
        (bad_task(tags=["a"]), "invalid notes or tags"),
        (bad_task(subtasks="x"), "not a list"),
        (bad_task(subtasks=[{"title": "s", "subtasks": [{"title": "deep"}]}]), "can't have subtasks"),
    ],
)
def test_bad_files_raise_friendly_error_and_import_nothing(tmp_path, content, message):
    file = tmp_path / "bad.json"
    file.write_text(content)
    with pytest.raises(ValueError, match=message):
        transfer.import_json(file)
    assert db.get_all() == []  # even the valid first task must not be left behind


def test_binary_file_is_rejected(tmp_path):
    file = tmp_path / "bin.json"
    file.write_bytes(b"\xff\xfe\x00")
    with pytest.raises(ValueError, match="not valid JSON"):
        transfer.import_json(file)