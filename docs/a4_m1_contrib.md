# A4 individual contribution - M1 (foundation)

## What I implemented

1. **Schema and connection layer** (`database/database.py`)
   - Four tables with CHECK constraints and foreign keys; indexes for the
     filters the repositories actually use.
   - `transaction()` commits on success and rolls back on failure;
     `connection()` is read-only. Foreign keys are enabled per connection.
2. **Repositories** (`repositories/`)
   - Staff, ticket, activity and notification persistence; all SQL goes
     through `Database`; ISO-8601 datetime encoding/decoding.
   - `StaffRepository.count_open_workloads()` later became the data source for
     BR-8.
3. **Observer core** (`patterns/observer/`)
   - `TicketEventPublisher` (subscribe/unsubscribe/publish), immutable event
     records with human-readable `message`, failure isolation per observer.
4. **TicketService skeleton** (`services/ticket_service.py`)
   - create/list/get use cases; the service owns the clock (amendment #1).
5. **Test infrastructure** (`tests/conftest.py`)
   - One isolated temp SQLite DB per test.

## Problems solved

- SQLite disables foreign keys by default - fixed by `PRAGMA foreign_keys = ON`
  in every `Database._connect()`.
- Mixed naive/aware datetimes would raise on comparison - later hardened with
  `_as_utc()` in the ordering strategies.

## Evidence

`tests/test_database.py`, `tests/test_repositories.py`, `tests/test_observer.py`,
`tests/test_service.py`, `tests/test_ticket_service.py`.
