<pre>
8888888b.                       888 888888b.                 888      888          
888   Y88b                      888 888  "88b                888      888          
888    888                      888 888  .88P                888      888          
888   d88P 888d888 .d88b.   .d88888 8888888K.  888  888  .d88888  .d88888 888  888 
8888888P"  888P"  d88""88b d88" 888 888  "Y88b 888  888 d88" 888 d88" 888 888  888 
888        888    888  888 888  888 888    888 888  888 888  888 888  888 888  888 
888        888    Y88..88P Y88b 888 888   d88P Y88b 888 Y88b 888 Y88b 888 Y88b 888 
888        888     "Y88P"   "Y88888 8888888P"   "Y88888  "Y88888  "Y88888  "Y88888 
                                                                               888 
                                                                          Y8b d88P 
                                                                           "Y88P"  </pre>

---
ProdBuddy is a zero-install local desktop task manager and time tracker built with Python and Tkinter. It supports light and dark themes, subtasks, tags, live stopwatch timing, daily SQLite backups, and JSON export/import.


## Features

- **Views**: Switch between **Today** (due and overdue unfinished tasks), **All tasks**, or individual **Projects**, with a **Project** column and project selector dropdown when adding from multi-project views.
- **Subtasks & Tags**: Create subtasks under tasks and organize items with comma-separated tags (`work`, `urgent`, `#home`) and multi-line task notes.
- **Live Timer**: Start and stop a per-task timer with live elapsed seconds in the status bar and **Tracked** column, plus visual highlight on the active task.
- **Light & Dark Themes**: Toggle between light and dark palettes with custom themed dialogs and automatic logo switching.
- **Safe Storage & Transfer**: SQLite database in `%APPDATA%\ProdBuddy\tracker.db` with automatic daily backups (keeping the 7 newest) and JSON export/import.

---

## Getting Started

### Prerequisites

- Python 3.8 or higher (uses standard library `tkinter` and `sqlite3` — no extra `pip install` needed).

### Run Locally

```bash
python main.py