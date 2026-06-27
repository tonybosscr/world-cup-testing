import json
from pathlib import Path
from typing import Dict

from model import simulate_match
from model_variants import get_model_registry
from stable_selection import stable_best_model


def load_previous_selected_model(path: Path, fallback: str = 'baseline_main') -> str:
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
            return data.get('selected_model', fallback)
        except Exception:
            return fallback
    return fallback


def select_best_model_name(comparison: Dict, fallback: str = 'baseline_main') -> str:
    best = (comparison or {}).get('best_model')
    if best:
        return best
    return fallback


def select_stable_model(
    comparison: Dict,
    comparison_history: list,
    selected_model_path: Path,
    fallback_model: str = 'baseline_main',
    min_evaluated_matches: int = 12,
    rolling_window: int = 5,
    switch_margin: float = 1.5,
) -> Dict:
    incumbent = load_previous_selected_model(selected_model_path, fallback=fallback_model)
    result = stable_best_model(
        comparison=comparison,
        comparison_history=comparison_history,
        fallback_model=fallback_model,
        min_evaluated_matches=min_evaluated_matches,
        rolling_window=rolling_window,
        switch_margin=switch_margin,
        incumbent_model=incumbent,
    )
    return result


def run_selected_model(model_name: str, home: Dict, away: Dict, runs: int = 20000) -> Dict:
    registry = get_model_registry()
    if model_name == 'baseline_main':
        return simulate_match(home, away, runs=runs)
    fn = registry.get(model_name)
    if not fn:
        return simulate_match(home, away, runs=runs)
    return fn(home, away, runs=runs)
