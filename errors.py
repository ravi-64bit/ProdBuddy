import datetime
import traceback

import config


def log(exc_type, exc, tb):
    """Save the full error to error.log (no popup)."""
    details = "".join(traceback.format_exception(exc_type, exc, tb))
    try:
        with open(config.LOG_PATH, "a") as f:
            f.write(f"--- {datetime.datetime.now()}\n{details}\n")
    except OSError:
        pass  # never let logging crash the error handler


def report(exc_type, exc, tb):
    """Log the error and show a friendly popup."""
    log(exc_type, exc, tb)

    from tkinter import messagebox  # imported here so this file works without a window

    messagebox.showerror(
        "Something went wrong",
        f"{exc}\n\nThe app is still running.\nDetails saved to:\n{config.LOG_PATH}",
    )
