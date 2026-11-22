# Compliance checklist

## Patterns (5 required, all present)

- [x] **Factory Method** - abstract creator + 3 concrete creators + 3 products + registry.
- [x] **State** - Context (`Ticket`), abstract state + 4 concrete states, BR-1 matrix centralized.
- [x] **Strategy** - ordering (2 concrete) and assignment (1 concrete), both hot-swappable.
- [x] **Observer** - publisher, observer interface, console notification + activity log observers, 3 event types.
- [x] **Decorator** - component = `TicketObserver`, concrete component = console observer, base decorator + 2 concrete decorators, stack built in the composition root only.

## Domain rules

- [x] BR-1: all 16 state/action cells implemented; rejected actions raise with a reason.
- [x] BR-2: 7-day inclusive reopen window, wall-clock based (demo-safe).
- [x] BR-3: resolution note >= 3 chars; cleared on reopen.
- [x] BR-4 / BR-5: ordering strategies with documented tie-breaks.
- [x] BR-6: component / affected_account / asset_tag+location mandatory by creator.
- [x] BR-7: assignment refused outside OPEN and IN_PROGRESS.
- [x] BR-8: AUTO assignment selects fewest OPEN+IN_PROGRESS; stable tie-break.
- [x] BR-9: canonical uppercase tokens in models, validators and DB CHECKs.

## Engineering hygiene

- [x] One Git branch (`main`) only; no feature branches remain.
- [x] No commits or pushes for the final consolidation pass (local working tree only).
- [x] No domain/service/CLI code prints directly except through the CLI and decorators.
- [x] No raw SQL outside `Database`, repositories and the schema definition.
- [x] All datetime comparisons are aware-datetime safe (`_as_utc`).
- [x] Seed is idempotent and deterministic apart from the BR-2 wall-clock offsets.
- [x] Tests use one isolated temp DB per test (`tmp_path` fixture).
- [x] CI runs on `windows-latest` with Python 3.13.

## Verification performed

- [x] `python -m pytest -q` - **207 passed, 7 intentional skips** (allowed matrix cells in the rejection-message test).
- [x] CLI entry point import smoke test.
- [x] Seed run twice - second run refuses to duplicate.
- [x] Composition root builds the full object graph (`build_application`).

## Known documented deviations

- `Ticket.status` is an alias of `status_code` (uppercase token) for backward
  compatibility; the human-readable name is `status_display`.
- `models/states.py` and `patterns/observer/observer.py` are thin re-export
  shims so both historical import paths keep working.
- The BR-2 seed timestamps are relative to the wall clock (all other seed
  timestamps are frozen at `FAKE_NOW`) so the demo works on any date.
