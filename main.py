import sys
import tkinter as tk

import backup
import errors

if __name__ == "__main__":
    try:
        backup.backup_on_launch()  # must run before ui/db opens the database
    except Exception:
        errors.log(*sys.exc_info())  # a failed backup should never stop the app

    try:
        from ui import App  # also opens the database, so DB problems are caught here
        App().mainloop()
    except Exception:
        root = tk.Tk()
        root.withdraw()  # hide the empty window, we only want the popup
        errors.report(*sys.exc_info())