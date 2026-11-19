"""Small, UI-independent helpers used throughout ProdBuddy."""
from datetime import date, datetime


def today_iso():
    return date.today().isoformat()


def parse_tags(value):
    """Normalise comma-separated tags into a predictable, lowercase string."""
    if value is None:
        return ""
    if isinstance(value, (list, tuple, set)):
        parts = value
    elif isinstance(value, str):
        parts = value.split(",")
    else:
        raise ValueError("Tags must be text.")
    clean = []
    seen = set()
    for item in parts:
        tag = str(item).strip().lstrip("#").lower()
        if tag and tag not in seen:
            clean.append(tag)
            seen.add(tag)
    return ",".join(clean)


def format_duration(seconds):
    seconds = max(0, int(seconds or 0))
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours}h {minutes:02d}m"
    if minutes:
        return f"{minutes}m {secs:02d}s"
    return f"{secs}s"


def valid_date(value):
    """Return an ISO date or None; raise ValueError for invalid non-empty input."""
    if value in (None, ""):
        return None
    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d").date().isoformat()
    except (AttributeError, TypeError, ValueError):
        raise ValueError("Enter a date in YYYY-MM-DD format.")
