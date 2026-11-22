# HelpDesk - Ticket Management System

A small console application for creating, listing, ordering, assigning and
resolving support tickets, built as a design-patterns course project.
Five GoF patterns are implemented and wired together: **Factory Method,
State, Strategy, Observer and Decorator**.

## Quick start (Windows / PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -e .
python -m pytest -q
helpdesk          # or: python -m helpdesk.main
```

Seed the deterministic demo data (safe to run twice):

```powershell
python -m helpdesk.database.seed
```

## Console menu

- `1` Create a ticket (category-specific mandatory fields are prompted)
- `2` List tickets (current ordering strategy)
- `3` View a ticket (`HD-0001` or the numeric id)
- `4` Switch ordering strategy (Priority BR-4 / Deadline BR-5)
- `5` Assign a ticket (explicit id or AUTO using fewest open tickets, BR-8)
- `6` Show staff workloads (OPEN + IN_PROGRESS counts)
- `7` Transition a ticket (start / resolve / close / reopen)
- `0` Exit

## Layout

- `src/helpdesk/database/` - SQLite schema, connection helpers, deterministic seed
- `src/helpdesk/repositories/` - persistence for tickets, staff, activity and notifications
- `src/helpdesk/models/` - domain models (Ticket Context + Products), validators, exceptions
- `src/helpdesk/services/` - application use cases (TicketService, AssignmentService)
- `src/helpdesk/patterns/` - State, Factory Method, Strategy, Observer, Decorator
- `src/helpdesk/cli/` - console user interface
- `tests/` - pytest suite (unit, matrix, edge, integration and CLI tests)
- `docs/` - pattern map, UML-style diagrams, traceability, compliance and A4 reports

## Design notes

SQLite stores datetimes as ISO-8601 text. Foreign keys are enabled per
connection in `Database._connect()`. Tickets are created through validated,
canonical uppercase category/priority tokens (`TECHNICAL`, `ACCOUNT`,
`HARDWARE` and `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).

The lifecycle matrix (BR-1/BR-2) lives only in
`src/helpdesk/patterns/state/states.py`. The 7-day reopen window uses the real
clock, so the two seeded BR-2 demo tickets stay valid on any demo date; all
other seed timestamps are frozen at `FAKE_NOW`.

See [docs/pattern_map.md](docs/pattern_map.md) for the full pattern-to-code map.
