import math
from datetime import datetime, timezone
from typing import Dict, List

from calibration import calibration_bins, expected_calibration_error
from model_variants import get_model_registry


def compare_models(matches: List[Dict], strengths: Dict[str, Dict], runs_per_model: int = 4000) -> Dict:
    registry = get_model_registry()
    results = []

    for model_name, simulate_fn in registry.items():
        evaluated = 0
        correct = 0
        brier_total = 0.0
        log_loss_total = 0.0
        calibration_records = []

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

            sim = simulate_fn(home, away, runs=runs_per_model)
            probs = {'H': sim['home_win_prob'], 'D': sim['draw_prob'], 'A': sim['away_win_prob']}
            pred = max(probs, key=probs.get)

            hg = int(m['home_score'])
            ag = int(m['away_score'])
            actual = 'H' if hg > ag else 'D' if hg == ag else 'A'

            evaluated += 1
            if pred == actual:
                correct += 1

            y = {'H': 0, 'D': 0, 'A': 0}
            y[actual] = 1
            brier_total += sum((probs[k] - y[k]) ** 2 for k in ['H', 'D', 'A'])
            p = max(min(probs[actual], 1 - 1e-15), 1e-15)
            log_loss_total += -math.log(p)

            calibration_records.append({
                'predicted_prob': probs[pred],
                'actual_hit': 1 if pred == actual else 0,
            })

        bins = calibration_bins(calibration_records, bin_size=0.1)
        ece = expected_calibration_error(bins)
        results.append({
            'model_name': model_name,
            'evaluated_matches': evaluated,
            'pick_accuracy': (correct / evaluated) if evaluated else 0.0,
            'brier_score': (brier_total / evaluated) if evaluated else None,
            'log_loss': (log_loss_total / evaluated) if evaluated else None,
            'ece': ece,
            'calibration_bins': bins,
        })

    ranked = sorted(
        results,
        key=lambda r: (
            -(r['pick_accuracy'] or 0),
            (r['brier_score'] if r['brier_score'] is not None else 999),
            (r['ece'] if r['ece'] is not None else 999),
        )
    )

    return {
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'models': ranked,
        'best_model': ranked[0]['model_name'] if ranked else None,
    }
