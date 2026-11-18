import os

# Fixed app folder: C:\Users\<you>\AppData\Roaming\ProdBuddy on Windows
# (falls back to your home folder if APPDATA doesn't exist, e.g. Mac/Linux)
FOLDER = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "ProdBuddy")
os.makedirs(FOLDER, exist_ok=True)

DB_PATH = os.path.join(FOLDER, "tracker.db")
LOG_PATH = os.path.join(FOLDER, "error.log")
SETTINGS_PATH = os.path.join(FOLDER, "settings.json")