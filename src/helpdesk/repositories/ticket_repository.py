"""Persistence for tickets on the frozen database schema (owned by M1).

Accesses the database exclusively through the Database class:
transaction() for writes, connection() for reads. Dates cross the sqlite
boundary as ISO-8601 strings, exactly like the other repositories.
"""

from datetime import UTC, datetime

from helpdesk.database.database import Database
from helpdesk.models.exceptions import NotFoundError
from helpdesk.models.ticket import (
    AccountTicket,
    HardwareTicket,
    TechnicalTicket,
    Ticket,
)
from helpdesk.patterns.state.states import state_for

_COLUMNS = (
    "id", "title", "description", "category", "priority", "status",
    "created_at", "updated_at", "deadline", "assigned_staff_id",
    "technical_component", "affected_account", "asset_tag", "location",
    "closed_at", "resolution_note",
)
_INSERT_COLUMNS = tuple(column for column in _COLUMNS if column != "id")
_DATETIME_COLUMNS = ("created_at", "updated_at", "deadline", "closed_at")

_PRODUCT_BY_CATEGORY = {
    "TECHNICAL": TechnicalTicket,
    "ACCOUNT": AccountTicket,
    "HARDWARE": HardwareTicket,
}


def _encode(value):
    """Python -> sqlite: datetimes become ISO-8601 strings."""
    return value.isoformat() if isinstance(value, datetime) else value


def _decode(row, column):
    """sqlite -> Python: schema date columns come back as datetimes."""
    value = row[column]
    if value is None or column not in _DATETIME_COLUMNS:
        return value
    return datetime.fromisoformat(value)


class TicketRepository:
    def __init__(self, database: Database) -> None:
        self._db = database

    def save(self, ticket: Ticket) -> Ticket:
        """INSERT when the ticket is new (id is None), otherwise UPDATE (upsert)."""
        # updated_at is NOT NULL: a directly constructed product may leave it
        # unset. Seeding it from created_at keeps round-trips lossless.
        if ticket.updated_at is None:
            ticket.updated_at = ticket.created_at or datetime.now(UTC)

        values = {
            column: _encode(
                ticket.status_code if column == "status" else getattr(ticket, column)
            )
            for column in _INSERT_COLUMNS
        }

        with self._db.transaction() as conn:
            if ticket.id is None:
                columns = ", ".join(_INSERT_COLUMNS)
                placeholders = ", ".join("?" for _ in _INSERT_COLUMNS)
                cursor = conn.execute(
                    f"INSERT INTO tickets ({columns}) VALUES ({placeholders})",
                    tuple(values[column] for column in _INSERT_COLUMNS),
                )
                ticket.id = cursor.lastrowid
            else:
                self._update(conn, ticket, values)

        return ticket

    def _update(self, conn, ticket: Ticket, values: dict) -> None:
        assignments = ", ".join(f"{column} = ?" for column in _INSERT_COLUMNS)
        parameters = tuple(values[column] for column in _INSERT_COLUMNS)
        conn.execute(
            f"UPDATE tickets SET {assignments} WHERE id = ?",
            (*parameters, ticket.id),
        )

    def get(self, ticket_id: int) -> Ticket:
        with self._db.connection() as conn:
            row = conn.execute(
                "SELECT * FROM tickets WHERE id = ?", (ticket_id,)
            ).fetchone()

        if row is None:
            raise NotFoundError(f"Ticket #{ticket_id} does not exist.")

        return self._row_to_ticket(row)

    def find(
        self,
        *,
        status=None,
        priority=None,
        category=None,
        staff_id=None,
    ) -> list[Ticket]:
        """Filter by schema columns; staff_id maps to assigned_staff_id."""
        filters, parameters = [], []
        if status is not None:
            filters.append("status = ?")
            parameters.append(status)
        if priority is not None:
            filters.append("priority = ?")
            parameters.append(priority)
        if category is not None:
            filters.append("category = ?")
            parameters.append(category)
        if staff_id is not None:
            filters.append("assigned_staff_id = ?")
            parameters.append(staff_id)

        where = f"WHERE {' AND '.join(filters)}" if filters else ""

        with self._db.connection() as conn:
            rows = conn.execute(
                f"SELECT * FROM tickets {where} ORDER BY id", parameters
            ).fetchall()

        return [self._row_to_ticket(row) for row in rows]

    def _row_to_ticket(self, row) -> Ticket:
        kwargs = {column: _decode(row, column) for column in _COLUMNS}
        status = kwargs.pop("status")
        # Infrastructure lookup, deliberately NOT a GoF pattern.
        product_class = _PRODUCT_BY_CATEGORY[row["category"]]
        ticket = product_class(**kwargs)
        ticket.set_state_from_code(status)
        return ticket
