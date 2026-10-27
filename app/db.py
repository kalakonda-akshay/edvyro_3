import json
import os
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = os.environ.get("DB_PATH", str(ROOT / "internships.db"))


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Create the table if it doesn't exist."""
    with get_conn() as conn:
        conn.executescript((ROOT / "schema.sql").read_text())


def seed_db(reset: bool = False) -> int:
    """Load data/seed.json. Only seeds an empty table unless reset=True."""
    init_db()
    records = json.loads((ROOT / "data" / "seed.json").read_text())
    with get_conn() as conn:
        if reset:
            conn.execute("DELETE FROM internships")
            conn.execute("DELETE FROM sqlite_sequence WHERE name='internships'")
        count = conn.execute("SELECT COUNT(*) FROM internships").fetchone()[0]
        if count > 0:
            return 0
        conn.executemany(
            """INSERT INTO internships
               (title, company, location, work_mode, stipend, description, deadline, status)
               VALUES (:title, :company, :location, :work_mode, :stipend, :description, :deadline, :status)""",
            records,
        )
    return len(records)


if __name__ == "__main__":
    n = seed_db(reset=True)
    print(f"Seeded {n} internships into {DB_PATH}")
