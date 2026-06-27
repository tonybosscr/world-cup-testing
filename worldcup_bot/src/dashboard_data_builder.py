from pathlib import Path
import json
from typing import Dict, List


def read_json_if_exists(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding='utf-8'))
    return default


def build_dashboard_data(output_dir: Path):
    predictions_file = output_dir / 'predictions.json'
    backtest_file = output_dir / 'backtest_report.json'
    comparison_file = output_dir / 'model_comparison.json'
    summary_file = output_dir / 'performance_summary.json'
    selected_model_file = output_dir / 'selected_model.json'
    target = output_dir / 'dashboard_data.json'

    predictions = read_json_if_exists(predictions_file, {})
    backtest = read_json_if_exists(backtest_file, {})
    comparison = read_json_if_exists(comparison_file, {})
    summary = read_json_if_exists(summary_file, {})
    selected = read_json_if_exists(selected_model_file, {})

    payload = {
        'generated_at_utc': predictions.get('generated_at_utc'),
        'selected_model': selected.get('selected_model', predictions.get('selected_model')),
        'predictions_today': predictions.get('predictions', []),
        'summary': summary,
        'backtest': backtest,
        'model_comparison': comparison,
    }
    target.write_text(json.dumps(payload, indent=2), encoding='utf-8')
    return payload
