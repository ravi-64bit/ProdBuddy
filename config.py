import os
import sys

# Store ProdBuddy data files inside a ProdBuddy folder on the user's Desktop
DESKTOP_DIR = os.path.join(os.path.expanduser("~"), "Documents")
FOLDER = os.path.join(DESKTOP_DIR, "ProdBuddy")
os.makedirs(FOLDER, exist_ok=True)

DB_PATH = os.path.join(FOLDER, "tracker.db")
LOG_PATH = os.path.join(FOLDER, "error.log")
SETTINGS_PATH = os.path.join(FOLDER, "settings.json")


def resource_path(relative_path):
  """Resolve bundled resource path for both source runs and PyInstaller builds."""
  base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
  return os.path.join(base_dir, relative_path)