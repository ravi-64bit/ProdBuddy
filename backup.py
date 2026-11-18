import datetime
import os
import sqlite3

import config

BACKUP_FOLDER = os.path.join(config.FOLDER, "backups")
KEEP = 7  # how many daily backups to keep


def backup_on_launch():
    """Make one backup per day, keep the newest KEEP files."""
    if not os.path.exists(config.DB_PATH):
        return  # first run, nothing to back up yet

    os.makedirs(BACKUP_FOLDER, exist_ok=True)
    today = datetime.date.today().isoformat()
    target = os.path.join(BACKUP_FOLDER, f"tracker-{today}.db")

    if not os.path.exists(target):  # keep the first backup of the day
        src = sqlite3.connect(config.DB_PATH)
        dst = sqlite3.connect(target)
        src.backup(dst)  # safe copy, even with WAL mode
        dst.close()
        src.close()

    # Delete the oldest ones (names sort by date)
    files = sorted(f for f in os.listdir(BACKUP_FOLDER) if f.startswith("tracker-"))
    for old in files[:-KEEP]:
        os.remove(os.path.join(BACKUP_FOLDER, old))
