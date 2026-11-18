"""Persistent, defensive loading/saving of user preferences."""
import json
import os
import tempfile

import config

DEFAULTS = {"dark": False}


def load():
    try:
        with open(config.SETTINGS_PATH, "r", encoding="utf-8") as handle:
            saved = json.load(handle)
        if not isinstance(saved, dict):
            return DEFAULTS.copy()
        return {**DEFAULTS, **{k: v for k, v in saved.items() if k in DEFAULTS}}
    except (OSError, ValueError, TypeError):
        return DEFAULTS.copy()


def save(settings):
    data = {**DEFAULTS, **{k: v for k, v in settings.items() if k in DEFAULTS}}
    os.makedirs(os.path.dirname(config.SETTINGS_PATH), exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix="settings-", suffix=".tmp", dir=os.path.dirname(config.SETTINGS_PATH))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
        os.replace(temporary, config.SETTINGS_PATH)
    except Exception:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise
