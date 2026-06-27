from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict, List


def _parse_dt(value: str):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def build_recent_results_from_matches(matches: List[Dict], lookback_days: int = 365, max_matches: int = 8) -> Dict[str, List[Dict]]:
    now = datetime.now(timezone.utc)
    team_results = defaultdict(list)

    for m in matches:
        status = str(m.get('status', '')).lower()
        if status not in {'ft', 'finished', 'fulltime', 'completed'}:
            continue
        if m.get('home_score') is None or m.get('away_score') is None:
            continue
        dt = _parse_dt(m['kickoff_utc'])
        if now - dt > timedelta(days=lookback_days):
            continue

        hg = int(m['home_score'])
        ag = int(m['away_score'])
        home_outcome = 'W' if hg > ag else 'D' if hg == ag else 'L'
        away_outcome = 'W' if ag > hg else 'D' if hg == ag else 'L'

        team_results[m['home_team']].append({
            'date': m['kickoff_utc'],
            'outcome': home_outcome,
            'goal_diff': hg - ag,
            'goals_for': hg,
            'goals_against': ag,
            'opponent': m['away_team'],
        })
        team_results[m['away_team']].append({
            'date': m['kickoff_utc'],
            'outcome': away_outcome,
            'goal_diff': ag - hg,
            'goals_for': ag,
            'goals_against': hg,
            'opponent': m['home_team'],
        })

    cleaned = {}
    for team, rows in team_results.items():
        rows = sorted(rows, key=lambda x: x['date'], reverse=True)[:max_matches]
        cleaned[team] = rows
    return cleaned


def compute_attack_defense_from_recent_results(results_by_team: Dict[str, List[Dict]]) -> Dict[str, Dict]:
    out = {}
    for team, rows in results_by_team.items():
        if not rows:
            out[team] = {
                'recent_goals_for_per_match': 1.2,
                'recent_goals_against_per_match': 1.0,
                'recent_points_per_match': 1.2,
            }
            continue
        gf = sum(r['goals_for'] for r in rows) / len(rows)
        ga = sum(r['goals_against'] for r in rows) / len(rows)
        pts = 0
        for r in rows:
            if r['outcome'] == 'W':
                pts += 3
            elif r['outcome'] == 'D':
                pts += 1
        ppm = pts / len(rows)
        out[team] = {
            'recent_goals_for_per_match': gf,
            'recent_goals_against_per_match': ga,
            'recent_points_per_match': ppm,
        }
    return out
