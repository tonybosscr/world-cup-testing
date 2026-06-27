from typing import Dict, List, Optional


def _score_model(row: Dict) -> float:
    acc = float(row.get('pick_accuracy', 0) or 0)
    brier = float(row.get('brier_score', 1.0) or 1.0)
    ece = float(row.get('ece', 1.0) or 1.0)
    # Higher is better overall after penalties.
    return (acc * 100.0) - (brier * 10.0) - (ece * 8.0)


def stable_best_model(
    comparison: Dict,
    comparison_history: List[Dict],
    fallback_model: str = 'baseline_main',
    min_evaluated_matches: int = 12,
    rolling_window: int = 5,
    switch_margin: float = 1.5,
    incumbent_model: Optional[str] = None,
) -> Dict:
    current_models = {m['model_name']: m for m in comparison.get('models', [])}
    eligible_current = {
        name: row for name, row in current_models.items()
        if int(row.get('evaluated_matches', 0) or 0) >= min_evaluated_matches
    }

    if not eligible_current:
        return {
            'selected_model': incumbent_model or fallback_model,
            'reason': 'No model met minimum evaluated match threshold.',
            'used_rolling_window': rolling_window,
        }

    # collect rolling scores from history
    score_series = {name: [] for name in current_models.keys()}
    for snapshot in comparison_history[-rolling_window:]:
        for row in snapshot.get('models', []):
            name = row.get('model_name')
            if name in score_series:
                score_series[name].append(_score_model(row))

    rolling_scores = {}
    for name, row in eligible_current.items():
        vals = score_series.get(name, [])
        current_score = _score_model(row)
        if vals:
            rolling_scores[name] = (sum(vals) + current_score) / (len(vals) + 1)
        else:
            rolling_scores[name] = current_score

    ranked = sorted(rolling_scores.items(), key=lambda x: x[1], reverse=True)
    best_name, best_score = ranked[0]

    if incumbent_model and incumbent_model in rolling_scores and incumbent_model != best_name:
        incumbent_score = rolling_scores[incumbent_model]
        if (best_score - incumbent_score) < switch_margin:
            return {
                'selected_model': incumbent_model,
                'reason': 'Incumbent retained because challenger did not clear switch margin.',
                'used_rolling_window': rolling_window,
                'rolling_scores': rolling_scores,
            }

    return {
        'selected_model': best_name,
        'reason': 'Best rolling smoothed model selected.',
        'used_rolling_window': rolling_window,
        'rolling_scores': rolling_scores,
    }
