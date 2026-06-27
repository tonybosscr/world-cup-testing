from datetime import datetime, timezone
from typing import Dict, List

from model import simulate_match


def _parse_dt(value: str):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def backtest_predictions(matches: List[Dict], strengths: Dict[str, Dict], runs: int = 4000) -> Dict:
    evaluated = 0
    correct_pick = 0
    brier_total = 0.0
    log_loss_total = 0.0
    detailed = []

    for m in matches:
        status = str(m.get('status', '')).lower()
        if status not in {'ft', 'finished', 'fulltime', 'completed'}:
            continue
        if m.get('home_score') is None or m.get('away_score') is None:
            continue

        home = strengths.get(m['home_team'])
        away = strengths.get(m['away_team'])
        if not home or not away:
            continue

        sim = simulate_match(home, away, runs=runs)
        probs = {
            'H': sim['home_win_prob'],
            'D': sim['draw_prob'],
            'A': sim['away_win_prob'],
        }
        pred = max(probs, key=probs.get)

        hg = int(m['home_score'])
        ag = int(m['away_score'])
        actual = 'H' if hg > ag else 'D' if hg == ag else 'A'

        evaluated += 1
        if pred == actual:
            correct_pick += 1

        y = {'H': 0, 'D': 0, 'A': 0}
        y[actual] = 1
        brier = sum((probs[k] - y[k]) ** 2 for k in ['H', 'D', 'A'])
        brier_total += brier

        import math
        p = max(min(probs[actual], 1 - 1e-15), 1e-15)
        log_loss_total += -math.log(p)

        detailed.append({
            'match_id': m.get('match_id'),
            'home_team': m['home_team'],
            'away_team': m['away_team'],
            'predicted': pred,
            'actual': actual,
            'probabilities': probs,
            'score': f"{hg}-{ag}",
            'kickoff_utc': m['kickoff_utc'],
        })

    return {
        'evaluated_matches': evaluated,
        'pick_accuracy': (correct_pick / evaluated) if evaluated else 0.0,
        'brier_score': (brier_total / evaluated) if evaluated else None,
        'log_loss': (log_loss_total / evaluated) if evaluated else None,
        'details': detailed,
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
    }
