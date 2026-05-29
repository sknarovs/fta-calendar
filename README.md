# FTA Calendar

Per-team `.ics` calendar files for the LNK Sporta Parks minifootball league (footour.lv).

Each team gets its own calendar with only that team's matches. Subscribe in Google Calendar, Apple Calendar, etc. via the raw `.ics` URL.

## Calendars

Files live in [`calendars/`](calendars/) and are regenerated on each update.

## Updating

```sh
python3 update_calendars.py   # regenerate .ics files
bash update.sh                # regenerate, then git commit + push if changed
```

> **Note:** `update.sh` auto-commits and pushes. Don't run it unless you intend to publish.

## How it works

1. Fetches match and team data from the footour.lv API
2. Builds one `.ics` per team, filtered to that team's matches
3. Event summaries show both team names (e.g. `FK Lauvu Bendes vs Hydro`)
4. Writes files to `calendars/`, wiping any previous `.ics` files

## Season changes

Tournament IDs are hardcoded at the top of `update_calendars.py` (`MASTER_TOURNAMENT_ID`, `TOURNAMENT_ID`). Update these when a new season starts.