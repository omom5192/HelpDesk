import sqlite3

from datetime import UTC, datetime

import pytest

from helpdesk.models.exceptions import NotFoundError


def test_staff_add_get_round_trip(staff_repository):
    staff = staff_repository.add("Amal Ahmed", "SUPPORT")
    fetched = staff_repository.get(staff.id)

    assert fetched.id == staff.id
    assert fetched.full_name == "Amal Ahmed"


def test_staff_get_unknown_raises(staff_repository):
    with pytest.raises(NotFoundError):
        staff_repository.get(999)


def test_staff_list_all(staff_repository):
    staff_repository.add("Amal", "SUPPORT")
    staff_repository.add("Sara", "MANAGER")

    names = [s.full_name for s in staff_repository.list_all()]

    assert names == ["Amal", "Sara"]


def test_activity_append_and_list(database, activity_repository):
    with database.transaction() as conn:
        conn.execute(
            "INSERT INTO tickets "
            "(id, title, description, category, priority, status, "
            "created_at, updated_at) VALUES "
            "(1, 'Printer on fire', 'Smoke out of the lab printer', "
            "'HARDWARE', 'MEDIUM', 'OPEN', "
            "'2026-10-23T10:00:00+00:00', "
            "'2026-10-23T10:00:00+00:00')"
        )

    activity_repository.append(
        1,
        "TEST_ACTION",
        "manual row",
        datetime.now(UTC),
    )

    records = activity_repository.list_for(1)

    assert len(records) == 1
    assert records[0].action == "TEST_ACTION"
    assert records[0].description == "manual row"


def test_activity_fk_rejects_unknown_ticket(
    database, activity_repository
):
    with pytest.raises(sqlite3.IntegrityError):
        activity_repository.append(
            12345,
            "TEST",
            "missing ticket",
            datetime.now(UTC),
        )