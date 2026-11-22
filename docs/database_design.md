# Database design

SQLite file (`helpdesk.db` by default). `Database.initialize()` executes the
schema in `src/helpdesk/database/database.py`; it is safe to call repeatedly.

## Tables

### `staff`
| column | type | notes |
| --- | --- | --- |
| `id` | INTEGER PRIMARY KEY | assigned by SQLite |
| `full_name` | TEXT NOT NULL | trimmed in the model |
| `role` | TEXT NOT NULL DEFAULT 'SUPPORT' | free text (seed uses network/email/dba...) |
| `created_at` | TEXT NOT NULL | ISO-8601; seed uses FAKE_NOW - N days; also the tie-break order for BR-8 |

### `tickets`
| column | type | notes |
| --- | --- | --- |
| `id` | INTEGER PRIMARY KEY | `None` until first save |
| `title` | TEXT NOT NULL | 3-120 chars |
| `description` | TEXT NOT NULL | >= 10 chars |
| `category` | TEXT CHECK IN ('TECHNICAL','ACCOUNT','HARDWARE') | BR-9 |
| `priority` | TEXT CHECK IN ('LOW','MEDIUM','HIGH','CRITICAL') | BR-9 |
| `status` | TEXT CHECK IN ('OPEN','IN_PROGRESS','RESOLVED','CLOSED') | stored from `ticket.status_code` |
| `created_at` | TEXT NOT NULL | service-owned clock |
| `updated_at` | TEXT NOT NULL | set by `_transition_to` |
| `deadline` | TEXT | ISO-8601 or NULL (BR-5 puts NULLs last) |
| `assigned_staff_id` | INTEGER REFERENCES staff(id) | FK on |
| `technical_component` | TEXT | TECHNICAL mandatory |
| `affected_account` | TEXT | ACCOUNT mandatory |
| `asset_tag`, `location` | TEXT | HARDWARE mandatory |
| `closed_at` | TEXT | BR-2 window source |
| `resolution_note` | TEXT | BR-3, cleared on reopen |

One wide table is intentional: all three Factory Method products share the
same persistence round-trip; only behaviour differs in the Python classes.

### `ticket_activity`
`id`, `ticket_id` (FK ON DELETE CASCADE), `action`, `description`, `created_at`.
Written by `ActivityLogObserver` — the Observer pattern has a real persistence
side effect, not just console output.

### `notifications`
`id`, `ticket_id` (FK ON DELETE SET NULL), `recipient`, `channel`, `message`,
`sent_at`. Kept for the notification repository contract.

## Integrity rules

- Every `Database._connect()` runs `PRAGMA foreign_keys = ON` (SQLite defaults
  it OFF, per connection).
- Writes go through `Database.transaction()` which commits on success and
  rolls back + re-raises on failure; reads go through `Database.connection()`.
- Datetimes cross the boundary as ISO-8601 text and are parsed back by the
  repositories. `_as_utc()` in the ordering strategies prevents naive/aware
  comparison errors.
- Indexes (Week 3 hardening): `status`, `priority`, `category`,
  `assigned_staff_id`, `deadline`, `ticket_activity.ticket_id`.

## Seed invariants

`python -m helpdesk.database.seed` is **idempotent**: it refuses to add data
when staff rows already exist. It inserts 6 staff and 11 tickets.

| staff id | expected OPEN+IN_PROGRESS load |
| --- | --- |
| 1 | 2 |
| 2 | 2 |
| 3 | 1 |
| 4 | 1 |
| 5 | 0 |
| 6 | 0 |

Therefore two AUTO assignments deterministically pick staff 5 then staff 6.
Two closed tickets demonstrate BR-2: `Outage came back` (closable window open)
and `Dead dock station` (window expired). Their `closed_at` uses wall-clock
offsets; other timestamps use `FAKE_NOW = 2026-11-02 09:00Z`.
