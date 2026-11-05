"""Persistence for ticket_activity rows.

Consumed by M3's ActivityLogObserver - the signature is frozen team
contract: append(ticket_id, action, description, occurred_at)
"""
from dataclasses import dataclass
from datetime import datetime

from helpdesk.database.database import Database


@dataclass
class ActivityRecord:
    id: int
    ticket_id: int
    action: str
    description: str | None
    created_at: datetime


class ActivityRepository:
    def __init__(self, database: Database) -> None:
        self._db = database

    def append(self, ticket_id: int, action: str,
               description: str | None, occurred_at: datetime) -> None:
        with self._db.transaction() as conn:
            conn.execute(
                "INSERT INTO ticket_activity (ticket_id, action, description, created_at) "
                "VALUES (?, ?, ?, ?)",
                (ticket_id, action, description, occurred_at.isoformat()),
            )

    def list_for(self, ticket_id: int) -> list[ActivityRecord]:
        with self._db.connection() as conn:
            rows = conn.execute(
                "SELECT * FROM ticket_activity WHERE ticket_id = ? ORDER BY id",
                (ticket_id,),
            ).fetchall()
        return [
            ActivityRecord(
                id=r["id"], ticket_id=r["ticket_id"], action=r["action"],
                description=r["description"],
                created_at=datetime.fromisoformat(r["created_at"]),
            )
            for r in rows
        ]