import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
import pytz


def ensure_dirs(paths):
    for path in paths:
        Path(path).mkdir(parents=True, exist_ok=True)


def iso_to_local(iso_value: str, tz_name: str):
    tz = pytz.timezone(tz_name)
    dt = datetime.fromisoformat(iso_value.replace('Z', '+00:00'))
    return dt.astimezone(tz).strftime('%Y-%m-%d %H:%M %Z')


def should_send_pre_match_alert(kickoff_utc: str, tz_name: str, hours_before: int = 1):
    kickoff = datetime.fromisoformat(kickoff_utc.replace('Z', '+00:00'))
    now = datetime.now(timezone.utc)
    delta = kickoff - now
    return timedelta(minutes=0) <= delta <= timedelta(hours=hours_before, minutes=10)


def safe_json_dump(path: Path, obj):
    path.write_text(json.dumps(obj, indent=2), encoding='utf-8')
