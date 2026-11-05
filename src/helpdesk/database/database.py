

import sqlite3
from contextlib import closing, contextmanager
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS staff (
    id   INTEGER PRIMARY KEY,
    full_name   TEXT NOT NULL,
    role   TEXT NOT NULL DEFAULT 'SUPPORT',
    created_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tickets (
    id   INTEGER PRIMARY KEY, 
    title   TEXT NOT NULL,
    description   TEXT NOT NULL,
    category   TEXT NOT NULL CHECK (category IN('TECHNICAL','ACCOUNT','HARDWARE')),
    priority   TEXT NOT NULL CHECK (priority IN ('LOW','MEDIUM','HIGH','CRITICAL')),
    status   TEXT NOT NULL CHECK (status IN ('OPEN','IN_PROGRESS','RESOLVED','CLOSED')),
    created_at   TEXT NOT NULL,
    updated_at   TEXT NOT NULL,
    deadline   TEXT,
    assigned_staff_id   INTEGER REFERENCES staff (id),
    technical_component   TEXT,
    affected_account   TEXT,
    asset_tag   TEXT,
    location   TEXT,
    closed_at   TEXT,
    resolution_note   TEXT
);

CREATE TABLE IF NOT EXISTS ticket_activity (
    id   INTEGER PRIMARY KEY,
    ticket_id   INTEGER NOT NULL REFERENCES tickets (id) ON DELETE CASCADE,
    action   TEXT NOT NULL,
    description   TEXT,
    created_at   TEXT NOT NULL 
);

CREATE TABLE IF NOT EXISTS notifications (
    id   INTEGER PRIMARY KEY,
    ticket_id   INTEGER REFERENCES tickets (id) ON DELETE SET NULL,
    recipient   TEXT NOT NULL,
    channel   TEXT NOT NULL DEFAULT 'CONSOLE',
    message   TEXT NOT NULL,
    sent_at   TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tickets_status   ON tickets (status);
CREATE INDEX IF NOT EXISTS idx_tickets_staff   ON tickets (assigned_staff_id);
CREATE INDEX IF NOT EXISTS idx_activity_ticket   ON ticket_activity (ticket_id);

"""


class Database:
    """connection lifcycle owner. context manager guarantee close()
    and give the service layer explicit commit-vs-read semantics."""
    def __init__(self, db_path: str | Path) -> None:
        self._path = Path(db_path)

    def initialize(self) -> None:
        """Creat tables/indexes if thy don't exist (safe to call twice.)"""
        with closing(self._connect()) as conn:
            conn.executescript(SCHEMA)
            conn.commit()

    @contextmanager
    def transaction(self):
        """write scope: commits on success, rolls back and re-raises
        on error."""
        conn = self._connect()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @contextmanager
    def connection(self):
        """Read scope: SELECTs only; never commits."""
        with closing(self._connect()) as conn:
            yield conn

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._path)
        conn.row_factory = sqlite3.Row   #name-based column access in repos
        conn.execute("PRAGMA foreign_keys = ON")   #PER-CONNECTION must repeat 
        return conn