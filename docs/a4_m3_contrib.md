# A4 individual contribution - M3 (wiring / hardening / delivery)

## What I implemented

1. **Decorator pattern** (`patterns/decorator/`)
   - `NotificationDecorator` base wraps the existing `TicketObserver`
     interface, so no observer class had to change.
   - `LoggingNotificationDecorator` records every notification;
     `UrgentNotificationDecorator` prefixes HIGH/CRITICAL messages using
     `dataclasses.replace`, preserving event immutability.
   - `main.py::build_application` builds `Logging(Urgent(Console))` - the
     composition root is the only place that knows the concrete stack.

2. **Wiring and CLI**
   - `ConsoleMenu` extended with options 4-7 (strategy switch, assignment,
     workloads, lifecycle transitions) and HD-<id> code parsing.
   - Assignment events reach the same publisher as creation/status events.

3. **Seed and hardening** (`database/seed.py`, repositories, strategies)
   - Idempotent seed: 6 staff, 11 tickets, workload design 2/2/1/1/0/0 so two
     AUTO assignments deterministically pick staff 5 and 6.
   - Two BR-2 demo tickets use wall-clock offsets; every other timestamp uses
     `FAKE_NOW`.
   - Repository defaults `updated_at`; ordering is naive/aware safe; indexes
     added for all filtered columns.

4. **Delivery**
   - CI moved to `windows-latest` + Python 3.13.
   - Documentation set: pattern map, UML diagrams, database design,
     traceability, compliance checklist, integration coverage and A4 reports.
   - Tests: `test_seed.py`, `test_repository_edges.py`,
     `test_validator_edges.py`, `test_integration_suite.py`,
     `test_cli_parsing.py`.

## Verification

`python -m pytest -q` -> **207 passed, 7 intentional skips**. CLI composition
root import smoke test passes. Seed run twice reports the second run as a
no-op.
