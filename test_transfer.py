import json

import pytest

import db
import transfer


def test_export_then_import_roundtrip(tmp_path):
    db.import_all([{"name": "Café ☕", "tasks": [{"title": "a", "done": True}, {"title": "b", "done": False}]}])
    file = tmp_path / "out.json"

    transfer.export_json(file)
    assert json.loads(file.read_text(encoding="utf-8"))["version"] == 1

    assert transfer.import_json(file) == 1
    projects = db.get_all()
    assert len(projects) == 2  # import adds, never replaces
    assert projects[0] == projects[1]  # same name, same tasks, same done flags


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


@pytest.mark.parametrize(
    "content, message",
    [
        ("not json", "not valid JSON"),
        ("[1, 2]", "not a ProdBuddy export"),
        ('{"projects": "nope"}', "not a ProdBuddy export"),
        ('{"projects": [{"name": "  "}]}', "no name"),
        ('{"projects": [{"name": "X", "tasks": "nope"}]}', "not a list"),
        ('{"projects": [{"name": "X", "tasks": [{"nope": 1}]}]}', "no title"),
    ],
)
def test_bad_files_raise_friendly_error_and_import_nothing(tmp_path, content, message):
    file = tmp_path / "bad.json"
    file.write_text(content)
    with pytest.raises(ValueError, match=message):
        transfer.import_json(file)
    assert db.get_all() == []


def test_binary_file_is_rejected(tmp_path):
    file = tmp_path / "bin.json"
    file.write_bytes(b"\xff\xfe\x00")
    with pytest.raises(ValueError, match="not valid JSON"):
        transfer.import_json(file)
