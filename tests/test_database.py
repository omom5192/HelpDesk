"""Database-layer tests: schema, FK enforcement, transaction rollback."""

import sqlite3

import pytest


def test_initialize_is_idempotent(database):
    database.initialize()

    with database.connection() as conn:
        names = {
            r["name"]
            for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }

    assert {
        "staff",
        "tickets",
        "ticket_activity",
        "notifications",
    } <= names


def test_foreign_keys_are_enforced(database):
    with database.transaction() as conn, pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO ticket_activity "
            "(ticket_id, action, description, created_at) "
            "VALUES (999, 'TEST', 'no such ticket', "
            "'2026-10-23T10:00:00+00:00')"
        )


def test_transaction_rolls_back_on_error(database):
    with pytest.raises(RuntimeError):
        with database.transaction() as conn:
            conn.execute(
                "INSERT INTO staff (full_name, role, created_at) "
                "VALUES ('Amal', 'SUPPORT', "
                "'2026-10-23T10:00:00+00:00')"
            )
            raise RuntimeError("boom")

    with database.connection() as conn:
        count = conn.execute(
            "SELECT COUNT(*) AS n FROM staff"
        ).fetchone()["n"]

    assert count == 0