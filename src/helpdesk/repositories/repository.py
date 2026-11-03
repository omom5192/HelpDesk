import sqlite3
from typing import List

class TicketRepository:
    def __init__(self, db_path: str = "helpdesk.db"):
        self.db_path = db_path
        self._create_table()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _create_table(self):
        # Veritabanı tablosu eğer yoksa oluşturulur
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    category TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'Open'
                )
                """
            )
            conn.commit()

    def add_ticket(self, title: str, description: str, priority: str, category: str) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO tickets (title, description, priority, category)
                VALUES (?, ?, ?, ?)
                """,
                (title, description, priority, category),
            )
            conn.commit()
            return cursor.lastrowid

    def get_all_tickets(self) -> List[dict]:
        # Veritabanındaki tüm biletleri getirir
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tickets")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def update_status(self, ticket_id: int, new_status: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE tickets
                SET status = ?
                WHERE id = ?
                """,
                (new_status, ticket_id),
            )
            conn.commit()