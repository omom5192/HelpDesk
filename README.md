# HelpDesk - Ticket Management System

A small console application for creating, listing and viewing support tickets,
built as a design-patterns course project.

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -q
helpdesk          # or: python -m helpdesk.main
```

The console menu offers:

- `1` Create a ticket
- `2` List tickets
- `3` View a ticket
- `0` Exit

## Layout

- `src/helpdesk/database/` - SQLite schema and connection helpers
- `src/helpdesk/repositories/` - persistence for tickets, staff, activity and notifications
- `src/helpdesk/models/` - domain models, validators and exceptions
- `src/helpdesk/services/` - application use cases
- `src/helpdesk/patterns/` - Observer and Decorator implementations
- `src/helpdesk/cli/` - console user interface
- `tests/` - pytest suite

## Notes

SQLite stores datetimes as ISO-8601 text. Foreign keys are enabled per
connection in `Database._connect()`. Tickets are created through validated,
canonical uppercase category/priority tokens (`TECHNICAL`, `ACCOUNT`,
`HARDWARE` and `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
