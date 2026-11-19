import os
import sys

# Fixed app folder: C:\Users\<you>\AppData\Roaming\ProdBuddy on Windows
# (falls back to your home folder if APPDATA doesn't exist, e.g. Mac/Linux)
FOLDER = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "ProdBuddy")
os.makedirs(FOLDER, exist_ok=True)

DB_PATH = os.path.join(FOLDER, "tracker.db")
LOG_PATH = os.path.join(FOLDER, "error.log")
SETTINGS_PATH = os.path.join(FOLDER, "settings.json")


def resource_path(relative_path):
    """Resolve bundled resource path for both source runs and PyInstaller builds."""
    base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, relative_path)