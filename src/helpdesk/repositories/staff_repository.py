"""Persistence for support staff."""

from datetime import UTC, datetime

from helpdesk.database.database import Database
from helpdesk.models.exceptions import NotFoundError
from helpdesk.models.staff import Staff


class StaffRepository:
    def __init__(self, database: Database) -> None:
        self._db = database

    def add(
        self,
        full_name: str,
        role: str = "SUPPORT",
        created_at: datetime | None = None,
    ) -> Staff:
        staff = Staff(
            full_name=full_name,
            role=role,
            created_at=created_at or datetime.now(UTC),
        )
        return self.save(staff)

    def save(self, staff: Staff) -> Staff:
        """Insert a staff row; the deterministic seed supplies created_at."""
        created_at = staff.created_at or datetime.now(UTC)
        with self._db.transaction() as conn:
            cursor = conn.execute(
                "INSERT INTO staff (full_name, role, created_at) VALUES (?, ?, ?)",
                (staff.full_name, staff.role, created_at.isoformat()),
            )
            staff.id = cursor.lastrowid
            staff.created_at = created_at
        return staff

    def get(self, staff_id: int) -> Staff:
        with self._db.connection() as conn:
            row = conn.execute(
                "SELECT * FROM staff WHERE id = ?", (staff_id,)
            ).fetchone()
        if row is None:
            raise NotFoundError(f"Staff #{staff_id} does not exist.")
        return self._hydrate(row)

    def list_all(self) -> list[Staff]:
        with self._db.connection() as conn:
            rows = conn.execute("SELECT * FROM staff ORDER BY id").fetchall()
        return [self._hydrate(row) for row in rows]

    def count_open_workloads(self, staff_id: int | None = None) -> dict[int, int] | int:
        """BR-8 helper: OPEN + IN_PROGRESS tickets per staff member.

        With an id, returns that member's count; without one, the whole map.
        """
        with self._db.connection() as conn:
            rows = conn.execute(
                """SELECT assigned_staff_id AS staff_id, COUNT(*) AS open_count
                   FROM tickets
                   WHERE status IN ('OPEN','IN_PROGRESS')
                     AND assigned_staff_id IS NOT NULL
                   GROUP BY assigned_staff_id"""
            ).fetchall()
        workloads = {row["staff_id"]: row["open_count"] for row in rows}
        if staff_id is not None:
            return workloads.get(staff_id, 0)
        return workloads

    @staticmethod
    def _hydrate(row) -> Staff:
        return Staff(
            id=row["id"],
            full_name=row["full_name"],
            role=row["role"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )
