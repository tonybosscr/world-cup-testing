from pathlib import Path
from datetime import datetime, timezone
import json
from typing import Dict, List


def load_history(path: Path) -> List[Dict]:
    if path.exists():
        return json.loads(path.read_text(encoding='utf-8'))
    return []


def append_history(path: Path, report: Dict, provider: str) -> List[Dict]:
    history = load_history(path)
    history.append({
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'provider': provider,
        'evaluated_matches': report.get('evaluated_matches', 0),
        'pick_accuracy': report.get('pick_accuracy', 0.0),
        'brier_score': report.get('brier_score'),
        'log_loss': report.get('log_loss'),
    })
    path.write_text(json.dumps(history, indent=2), encoding='utf-8')
    return history


def append_model_comparison_history(path: Path, comparison: Dict) -> List[Dict]:
    history = load_history(path)
    history.append({
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'best_model': comparison.get('best_model'),
        'models': comparison.get('models', []),
    })
    path.write_text(json.dumps(history, indent=2), encoding='utf-8')
    return history


def summarize_history(history: List[Dict]) -> Dict:
    if not history:
        return {
            'runs': 0,
            'avg_pick_accuracy': 0.0,
            'avg_brier_score': None,
            'avg_log_loss': None,
            'latest': None,
        }
    runs = len(history)
    avg_acc = sum(float(h.get('pick_accuracy', 0) or 0) for h in history) / runs
    briers = [float(h['brier_score']) for h in history if h.get('brier_score') is not None]
    logs = [float(h['log_loss']) for h in history if h.get('log_loss') is not None]
    return {
        'runs': runs,
        'avg_pick_accuracy': avg_acc,
        'avg_brier_score': (sum(briers) / len(briers)) if briers else None,
        'avg_log_loss': (sum(logs) / len(logs)) if logs else None,
        'latest': history[-1],
    }
