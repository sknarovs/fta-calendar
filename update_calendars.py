#!/usr/bin/env python3
import json
import hashlib
import re
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

API_BASE = "https://www.footour.lv/api"
MASTER_TOURNAMENT_ID = 59
TOURNAMENT_ID = 371
CALENDARS_DIR = Path(__file__).parent / "calendars"
RIGA_TZ_OFFSET = timedelta(hours=3)

def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "fta-calendar-updater/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))

def get_data():
    cal = fetch_json(f"{API_BASE}/matchCalendar?masterTournamentId={MASTER_TOURNAMENT_ID}&tid={TOURNAMENT_ID}")
    teams = fetch_json(f"{API_BASE}/teams?masterTournamentId={MASTER_TOURNAMENT_ID}&tid={TOURNAMENT_ID}")

    tournament_name = cal["records"].get("superTournamentName", "Minifootball")

    team_map = {}
    for rec in teams.get("records", []):
        team_map[rec["id"]] = rec["team_name"]

    all_matches = []
    for st_id, st in cal["records"].get("subTournaments", {}).items():
        st_name = st.get("tournamentName", "")
        for stage_id, stage in st.get("stages", {}).items():
            matches = stage.get("matches", {})
            for m in matches.get("prevMatches", []):
                m["_sub_tournament"] = st_name
                all_matches.append(m)
            for m in matches.get("nextMatches", []):
                m["_sub_tournament"] = st_name
                all_matches.append(m)

    return tournament_name, team_map, all_matches

def format_dt(match_datetime_str):
    dt = datetime.strptime(match_datetime_str, "%Y-%m-%d %H:%M:%S")
    dt = dt.replace(tzinfo=timezone(RIGA_TZ_OFFSET))
    return dt

def match_uid(match):
    h = hashlib.md5()
    h.update(f"fta-{match['id']}".encode())
    return h.hexdigest()

def slugify(text):
    text = text.lower()
    for src, dst in [("ā", "a"), ("č", "c"), ("ē", "e"), ("ģ", "g"), ("ī", "i"), ("ķ", "k"), ("ļ", "l"), ("ņ", "n"), ("ū", "u"), ("š", "s"), ("ž", "z")]:
        text = text.replace(src, dst)
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text

def escape_ics(text):
    return text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")

def format_ics_date(dt):
    return dt.strftime("%Y%m%dT%H%M%S")

def build_calendar(team_id, team_name, matches, tournament_name):
    team_matches = [m for m in matches if m["home_team_id"] == team_id or m["away_team_id"] == team_id]

    lines = []
    lines.append("BEGIN:VCALENDAR")
    lines.append("VERSION:2.0")
    lines.append("PRODID:-//FTA Calendar//EN")
    lines.append("CALSCALE:GREGORIAN")
    lines.append("METHOD:PUBLISH")
    lines.append(f"X-WR-CALNAME:{escape_ics(tournament_name + ' - ' + team_name)}")
    lines.append("X-WR-TIMEZONE:Europe/Riga")
    lines.append("X-WR-RELCALID:fta-calendar-" + str(team_id))
    lines.append("REFRESH-INTERVAL;VALUE=DURATION:P1D")

    for m in sorted(team_matches, key=lambda x: x["match_datetime"]):
        dt = format_dt(m["match_datetime"])
        is_midnight = m["match_datetime"].endswith(" 00:00:00")

        summary = f"{m['home_team_name']} vs {m['away_team_name']}"

        st = m.get("_sub_tournament", "")
        if st and st != "Čempionāts":
            summary = f"[{st}] {summary}"

        hs = m.get("home_team_full_time_score")
        aws = m.get("away_team_full_time_score")
        if hs is not None and aws is not None:
            summary += f" [{hs}:{aws}]"

        duration = timedelta(hours=1) if not is_midnight else timedelta(days=0)
        dt_end = dt + duration if not is_midnight else dt

        lines.append("BEGIN:VEVENT")
        lines.append(f"UID:{match_uid(m)}@fta-calendar")
        lines.append(f"DTSTAMP:{format_ics_date(datetime.now(timezone.utc))}")
        if is_midnight:
            lines.append(f"DTSTART;VALUE=DATE:{dt.strftime('%Y%m%d')}")
            lines.append(f"DTEND;VALUE=DATE:{(dt + timedelta(days=1)).strftime('%Y%m%d')}")
        else:
            lines.append(f"DTSTART;TZID=Europe/Riga:{format_ics_date(dt)}")
            lines.append(f"DTEND;TZID=Europe/Riga:{format_ics_date(dt_end)}")
        lines.append(f"SUMMARY:{escape_ics(summary)}")
        desc = f"{m['home_team_name']} vs {m['away_team_name']}"
        if st:
            desc = f"[{st}] {desc}"
        if is_midnight:
            desc += " (time TBC)"
        if hs is not None and aws is not None:
            desc += f" | Score: {hs}-{aws}"
        lines.append(f"DESCRIPTION:{escape_ics(desc)}")
        lines.append(f"URL:https://fta.lv/synottip/2026/calendar/{TOURNAMENT_ID}")
        lines.append("END:VEVENT")

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"

def main():
    CALENDARS_DIR.mkdir(parents=True, exist_ok=True)

    for f in CALENDARS_DIR.glob("*.ics"):
        f.unlink()

    tournament_name, teams, matches = get_data()

    for team_id, team_name in teams.items():
        slug = slugify(team_name)
        ics_content = build_calendar(team_id, team_name, matches, tournament_name)
        filepath = CALENDARS_DIR / f"{slug}.ics"
        filepath.write_text(ics_content, encoding="utf-8")
        print(f"Created {filepath}")

if __name__ == "__main__":
    main()