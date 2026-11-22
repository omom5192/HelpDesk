# Traceability matrix

Requirement -> implementation -> evidence (tests / docs).

| ID | Requirement (short) | Implementation | Evidence |
| --- | --- | --- | --- |
| BR-1 | Legal lifecycle transitions | `patterns/state/states.py` | `tests/test_state.py`, `tests/test_state_matrix.py` |
| BR-2 | Reopen only within 7 days of closing | `ClosedState.reopen`, `REOPEN_WINDOW_DAYS` | `tests/test_reopen_window.py` (inclusive boundary, +1s, 30d, missing timestamp) |
| BR-3 | Resolve requires a real note | `validate_resolution_note` used by state `resolve` | `tests/test_validator_edges.py`, `tests/test_state.py` |
| BR-4 | Priority ordering CRITICAL>HIGH>MEDIUM>LOW, oldest first | `PriorityOrderingStrategy` | `tests/test_strategy.py` |
| BR-5 | Deadline ordering, nulls last | `DeadlineOrderingStrategy` | `tests/test_strategy.py` |
| BR-6 | Category-specific mandatory fields | Factory creators | `tests/test_factory.py` |
| BR-7 | Assignment only for OPEN/IN_PROGRESS | `AssignmentService.assign` | `tests/test_integration.py`, `tests/test_integration_suite.py` |
| BR-8 | Assign to least-loaded staff; tie by staff order | `FewestOpenTicketsStrategy`, `StaffRepository.count_open_workloads` | `tests/test_strategy.py`, `tests/test_integration.py`, `tests/test_seed.py` |
| BR-9 | Canonical uppercase tokens | `models/ticket_types.py`, `models/validators.py`, DB CHECKs | `tests/test_validators.py`, `tests/test_validator_edges.py`, `tests/test_database.py` |
| FR-10 | Runtime ordering strategy switch | `TicketService.set_ordering_strategy`, CLI option 4 | `tests/test_strategy.py`, `tests/test_integration.py` |
| NFR-4 | Isolated test databases | `tests/conftest.py::database` fixture (tmp_path) | all tests |
| IDEMPOTENT | Seed refuses duplicate data | `database/seed.py::seed` | `tests/test_seed.py` |
| OBS | Activity log + notifications on events | `TicketEventPublisher`, observers | `tests/test_observer.py`, `tests/test_integration.py` |
| DEC | Logging/Urgent stack without changing observers | `notification_decorators.py`, `main.py` | `tests/test_decorator.py`, `tests/test_integration_suite.py` |
| CLI | Ticket codes, menu 0-7 | `cli/menu.py` | `tests/test_cli_parsing.py` |

## Pattern-to-deliverable map

| Deliverable | File |
| --- | --- |
| Pattern map (5 patterns + non-patterns) | `docs/pattern_map.md` |
| UML-style diagrams | `docs/uml/{strategy,factory_method,state_machine,wiring,decorator}.md` |
| Database design | `docs/database_design.md` |
| Integration coverage | `docs/integration_coverage.md` |
| Compliance checklist | `docs/compliance_checklist.md` |
| A4 individual contributions | `docs/a4_m{1,2,3}_contrib.md` |
| M1/M2/M3 README contributions | `docs/readme_m{1,2,3}_contrib.md` |
| CI | `.github/workflows/ci.yml` (windows-latest, Python 3.13) |
