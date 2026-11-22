# README contribution - M3 (wiring & delivery)

## README additions

- `python -m helpdesk.database.seed` documented as the idempotent demo setup.
- Documentation section links the pattern map, UML diagrams, traceability,
  compliance checklist and A4 contribution reports.
- BR-2 note explains why the two seeded closed tickets use wall-clock offsets
  while the rest of the seed is frozen at `FAKE_NOW`.

## M3 implementation surface

- **Decorator:** `NotificationDecorator` base + `LoggingNotificationDecorator`
  and `UrgentNotificationDecorator`; the composition root builds
  `Logging(Urgent(Console))`. Observers were not modified to support it.
- **Wiring:** `main.py::build_application` is the single composition root;
  `ConsoleMenu` receives both services and offers options 1-7.
- **Observer completion:** `ActivityLogObserver` writes real `ticket_activity`
  rows; assignment publishes `StaffAssignedEvent`.
- **Seed:** 6 staff + 11 tickets, idempotent, with workload design 2/2/1/1/0/0
  and two BR-2 reopen examples.
- **Hardening:** repository defaults `updated_at`, naive/aware-safe ordering,
  indexes on all filtered columns, boundary-safe validators.
- **Delivery:** CI on `windows-latest` / Python 3.13, docs set, full
  integration suite (`tests/test_integration.py`, `test_integration_suite.py`,
  `test_cli_parsing.py`, `test_seed.py`, `test_repository_edges.py`).
