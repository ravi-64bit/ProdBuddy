sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import os
import tempfile

# Must run BEFORE db/config are imported anywhere:
# tests use a throwaway folder, so your real data in %APPDATA% is never touched.
os.environ["APPDATA"] = tempfile.mkdtemp()

import pytest


@pytest.fixture(autouse=True)
def clean_db():
    """Empty the tables before every test so tests don't affect each other."""
    import db

    db.conn.execute("DELETE FROM tasks")
    db.conn.execute("DELETE FROM projects")
    db.conn.commit()
