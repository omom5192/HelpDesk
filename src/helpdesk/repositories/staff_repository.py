"""Persistence for support staff."""

from datetime import datetime, timezone

from helpdesk.database.database import Database
from helpdesk.models.exceptions import NotFoundError
from helpdesk.models.staff import Staff


class StaffRepository:
    def __init__(self, database: Database) -> None:
        self._db = database

    def add(self, full_name: str, role: str = "SUPPORT") -> Staff:
        staff = Staff(
            full_name=full_name,
            role=role,
            created_at=datetime.now(timezone.utc),
        )

        with self._db.transaction() as conn:
            cursor = conn.execute(
                """
                INSERT INTO staff (full_name, role, created_at)
                VALUES (?, ?, ?)
                """,
                (
                    staff.full_name,
                    staff.role,
                    staff.created_at.isoformat(),
                ),
            )
            staff.id = cursor.lastrowid

        return staff

    def get(self, staff_id: int) -> Staff:
        with self._db.connection() as conn:
            row = conn.execute(
                """
                SELECT id, full_name, role, created_at
                FROM staff
                WHERE id = ?
                """,
                (staff_id,),
            ).fetchone()

        if row is None:
            raise NotFoundError(
                f"Staff #{staff_id} does not exist."
            )

        return Staff(
            id=row["id"],
            full_name=row["full_name"],
            role=row["role"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def list_all(self) -> list[Staff]:
        with self._db.connection() as conn:
            rows = conn.execute(
                """
                SELECT id, full_name, role, created_at
                FROM staff
                ORDER BY id
                """
            ).fetchall()

        return [
            Staff(
                id=row["id"],
                full_name=row["full_name"],
                role=row["role"],
                created_at=datetime.fromisoformat(row["created_at"]),
            )
            for row in rows
        ]

    def count_open_workloads(self) -> dict[int, int]:
        """BR-8 helper: OPEN + IN_PROGRESS tickets per staff member."""
        with self._db.connection() as conn:
            rows = conn.execute(
                """
                SELECT assigned_staff_id AS staff_id,
                       COUNT(*) AS open_count
                FROM tickets
                WHERE status IN ('OPEN', 'IN_PROGRESS')
                  AND assigned_staff_id IS NOT NULL
                GROUP BY assigned_staff_id
                """
            ).fetchall()

        return {
            row["staff_id"]: row["open_count"]
            for row in rows
        }