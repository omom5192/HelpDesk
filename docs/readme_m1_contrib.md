# README contribution - M1 (foundation)

## Added to the README

- Quick start commands (venv, install, tests, `helpdesk` entry point).
- Menu description (now extended by M2/M3 to options 1-7).
- Layout section pointing at `database/`, `repositories/`, `models/`,
  `services/`, `patterns/`, `cli/`, `tests/`.
- Notes on ISO-8601 datetime storage and per-connection foreign keys.

## Foundation decisions owned by M1

- Single wide `tickets` table with CHECK constraints for category, priority
  and status (BR-9); `staff`, `ticket_activity`, `notifications` tables.
- `Database` class owns connection lifecycle: `initialize()`, `transaction()`
  (commit/rollback) and `connection()` (read-only).
- Repositories talk to the database only through `Database`.
- `TicketEventPublisher` (Observer Subject) plus immutable event records with
  a `message` field.
- `TicketService` create/list/get use cases with the service owning the clock.
- Isolated `tmp_path` database fixture in `tests/conftest.py` (NFR-4).

These pieces are the substrate on which M2 (State/Factory/Strategy) and M3
(Decorator/wiring/seed) built without changing the schema.
