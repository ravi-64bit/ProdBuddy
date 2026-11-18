import os
import sqlite3

import backup
import config
import db


def use_temp_backup_folder(monkeypatch, tmp_path):
    folder = tmp_path / "backups"
    monkeypatch.setattr(backup, "BACKUP_FOLDER", str(folder))
    return folder


def test_backup_contains_current_data(monkeypatch, tmp_path):
    folder = use_temp_backup_folder(monkeypatch, tmp_path)
    db.add_project("Saved")

    backup.backup_on_launch()

    files = os.listdir(folder)
    assert len(files) == 1
    copy = sqlite3.connect(folder / files[0])
    assert copy.execute("SELECT name FROM projects").fetchall() == [("Saved",)]
    copy.close()


def test_second_launch_same_day_keeps_first_backup(monkeypatch, tmp_path):
    folder = use_temp_backup_folder(monkeypatch, tmp_path)
    db.add_project("First")
    backup.backup_on_launch()

    db.add_project("Second")
    backup.backup_on_launch()

    files = os.listdir(folder)
    assert len(files) == 1
    copy = sqlite3.connect(folder / files[0])
    assert copy.execute("SELECT COUNT(*) FROM projects").fetchone()[0] == 1
    copy.close()


def test_only_newest_7_backups_are_kept(monkeypatch, tmp_path):
    folder = use_temp_backup_folder(monkeypatch, tmp_path)
    folder.mkdir()
    for day in range(1, 11):
        (folder / f"tracker-2020-01-{day:02d}.db").write_text("old")

    backup.backup_on_launch()

    files = sorted(os.listdir(folder))
    assert len(files) == 7
    assert "tracker-2020-01-01.db" not in files  # oldest removed
    assert any(not f.startswith("tracker-2020") for f in files)  # today's backup kept


def test_first_run_without_database_does_nothing(monkeypatch, tmp_path):
    folder = use_temp_backup_folder(monkeypatch, tmp_path)
    monkeypatch.setattr(config, "DB_PATH", str(tmp_path / "missing.db"))

    backup.backup_on_launch()

    assert not folder.exists()
