# FTA Calendar

Fetches match data from the footour.lv API and generates per-team `.ics` calendar files under `calendars/`.

## Running

```sh
python3 update_calendars.py   # regenerate .ics files
bash update.sh                # regenerate, then git commit + push if changed
```

`update.sh` auto-commits and pushes — do **not** run it unless you intend to publish.

## Key details

- Pure Python 3 stdlib — no dependencies, no venv, no `requirements.txt`.
- Tournament IDs are hardcoded constants (`MASTER_TOURNAMENT_ID`, `TOURNAMENT_ID`) near the top of `update_calendars.py`. These must be updated when the season changes.
- Riga timezone offset is hardcoded as `+3h` (EEST). Does not handle DST transitions dynamically.
- ICS output uses CRLF (`\r\n`) line endings per RFC 5545 — preserve this if editing the generator.
- `calendars/` is wiped and regenerated on every run; all `.ics` files there are ephemeral.
- No tests exist.