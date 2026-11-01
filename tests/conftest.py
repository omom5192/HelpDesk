"""Shared fixtures: one isolated temp database per test (NFR-4)."""
import pytest

from helpdesk.database.database import Database
from helpdesk.repositories.activity_repository import ActivityRepository
from helpdesk.repositories.staff_repository import StaffRepository


@pytest.fixture
def database(tmp_path):
    db = Database(tmp_path / "test_helpdesk.db")
    db.initialize()
    return db


@pytest.fixture
def staff_repository(database):
    return StaffRepository(database)


@pytest.fixture
def activity_repository(database):
    return ActivityRepository(database)