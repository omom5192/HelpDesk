"""Persistence for dispatched notification records."""

from dataclasses import dataclass
from datetime import datetime

from helpdesk.database.database import Database


@dataclass
class NotificationRecord:
    id: int
    recipient: str
    channel: str
    message: str
    sent_at: datetime


class NotificationRepository:
    def __init__(self, database: Database) -> None:
        self._db = database

    def append(
        self,
        recipient: str,
        channel: str,
        message: str,
        sent_at: datetime,
    ) -> None:
        with self._db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO notifications
                    (recipient, channel, message, sent_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    recipient,
                    channel,
                    message,
                    sent_at.isoformat(),
                ),
            )

    def list_all(self) -> list[NotificationRecord]:
        with self._db.connection() as conn:
            rows = conn.execute(
                "SELECT * FROM notifications ORDER BY id"
            ).fetchall()

        return [
            NotificationRecord(
                id=row["id"],
                recipient=row["recipient"],
                channel=row["channel"],
                message=row["message"],
                sent_at=datetime.fromisoformat(row["sent_at"]),
            )
            for row in rows
        ]