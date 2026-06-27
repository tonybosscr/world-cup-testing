from pathlib import Path
from typing import Dict, List


def _metric_card(title: str, value: str, subtitle: str = '') -> str:
    return f'''
    <div class="card">
      <div class="label">{title}</div>
      <div class="value">{value}</div>
      <div class="sub">{subtitle}</div>
    </div>
    '''


def _history_rows(history: List[Dict]) -> str:
    rows = []
    for item in reversed(history[-30:]):
        rows.append(
            f"<tr>"
            f"<td>{item.get('generated_at_utc','')}</td>"
            f"<td>{item.get('provider','')}</td>"
            f"<td>{item.get('evaluated_matches','')}</td>"
            f"<td>{(item.get('pick_accuracy',0) or 0):.1%}</td>"
            f"<td>{'' if item.get('brier_score') is None else round(item.get('brier_score'),4)}</td>"
            f"<td>{'' if item.get('log_loss') is None else round(item.get('log_loss'),4)}</td>"
            f"</tr>"
        )
    return '\n'.join(rows)


def _model_rows(models: List[Dict]) -> str:
    rows = []
    for item in models:
        rows.append(
            f"<tr>"
            f"<td>{item.get('model_name','')}</td>"
            f"<td>{item.get('evaluated_matches','')}</td>"
            f"<td>{(item.get('pick_accuracy',0) or 0):.1%}</td>"
            f"<td>{'' if item.get('brier_score') is None else round(item.get('brier_score'),4)}</td>"
            f"<td>{'' if item.get('log_loss') is None else round(item.get('log_loss'),4)}</td>"
            f"<td>{'' if item.get('ece') is None else round(item.get('ece'),4)}</td>"
            f"</tr>"
        )
    return '\n'.join(rows)


def _calibration_rows(bins: List[Dict]) -> str:
    rows = []
    for b in bins:
        rows.append(
            f"<tr>"
            f"<td>{b.get('bin_start',0):.1f}-{b.get('bin_end',0):.1f}</td>"
            f"<td>{b.get('count',0)}</td>"
            f"<td>{'' if b.get('avg_predicted') is None else format(b.get('avg_predicted'), '.3f')}</td>"
            f"<td>{'' if b.get('actual_frequency') is None else format(b.get('actual_frequency'), '.3f')}</td>"
            f"<td>{'' if b.get('gap') is None else format(b.get('gap'), '.3f')}</td>"
            f"</tr>"
        )
    return '\n'.join(rows)


def _sparkline_points(values: List[float], width: int = 500, height: int = 100) -> str:
    if not values:
        return ''
    min_v = min(values)
    max_v = max(values)
    spread = (max_v - min_v) or 1
    pts = []
    for i, v in enumerate(values):
        x = (i / max(1, len(values)-1)) * width
        y = height - (((v - min_v) / spread) * (height - 10)) - 5
        pts.append(f"{x:.1f},{y:.1f}")
    return ' '.join(pts)


def build_dashboard(output_path: Path, history: List[Dict], summary: Dict, latest_report: Dict, model_comparison: Dict = None):
    acc_values = [float(h.get('pick_accuracy', 0) or 0) for h in history]
    brier_values = [float(h.get('brier_score', 0) or 0) for h in history if h.get('brier_score') is not None]
    log_values = [float(h.get('log_loss', 0) or 0) for h in history if h.get('log_loss') is not None]

    best_model = (model_comparison or {}).get('best_model') if model_comparison else None
    models = (model_comparison or {}).get('models', []) if model_comparison else []
    best_bins = models[0].get('calibration_bins', []) if models else []

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>World Cup Bot Backtest Dashboard</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; background:#0b1020; color:#e8eefc; }}
    h1,h2 {{ margin: 0 0 12px; }}
    .grid {{ display:grid; grid-template-columns: repeat(auto-fit,minmax(220px,1fr)); gap:16px; margin: 18px 0 24px; }}
    .card {{ background:#141b34; border:1px solid #263259; border-radius:16px; padding:16px; }}
    .label {{ color:#9cb0e0; font-size:13px; margin-bottom:8px; }}
    .value {{ font-size:28px; font-weight:700; }}
    .sub {{ color:#8da0cc; font-size:12px; margin-top:6px; }}
    table {{ width:100%; border-collapse:collapse; background:#141b34; border-radius:16px; overflow:hidden; }}
    th,td {{ padding:12px; border-bottom:1px solid #263259; text-align:left; font-size:14px; }}
    th {{ color:#a9bbe8; background:#10172e; }}
    .panel {{ background:#141b34; border:1px solid #263259; border-radius:16px; padding:16px; margin: 18px 0; }}
    .charts {{ display:grid; grid-template-columns:1fr; gap:16px; }}
    .muted {{ color:#97a8d2; }}
    svg {{ width:100%; height:auto; background:#0f1530; border-radius:10px; }}
  </style>
</head>
<body>
  <h1>🏆 World Cup Prediction Bot Dashboard</h1>
  <div class="muted">Backtesting, calibration analysis, and long-term performance tracking</div>

  <div class="grid">
    {_metric_card('Tracked runs', str(summary.get('runs',0)), 'Total historical backtest snapshots')}
    {_metric_card('Average pick accuracy', f"{summary.get('avg_pick_accuracy',0):.1%}", 'Across saved runs')}
    {_metric_card('Average Brier score', 'N/A' if summary.get('avg_brier_score') is None else f"{summary.get('avg_brier_score'):.4f}", 'Lower is better')}
    {_metric_card('Average log loss', 'N/A' if summary.get('avg_log_loss') is None else f"{summary.get('avg_log_loss'):.4f}", 'Lower is better')}
  </div>

  <div class="grid">
    {_metric_card('Latest evaluated matches', str((summary.get('latest') or {}).get('evaluated_matches',0)), 'Completed matches in latest backtest')}
    {_metric_card('Latest pick accuracy', f"{((summary.get('latest') or {}).get('pick_accuracy',0) or 0):.1%}", 'Latest snapshot')}
    {_metric_card('Latest Brier score', 'N/A' if (summary.get('latest') or {}).get('brier_score') is None else f"{(summary.get('latest') or {}).get('brier_score'):.4f}", 'Latest snapshot')}
    {_metric_card('Best model', best_model or 'N/A', 'Current comparison winner')}
  </div>

  <div class="charts">
    <div class="panel">
      <h2>Pick Accuracy Trend</h2>
      <svg viewBox="0 0 500 100" preserveAspectRatio="none">
        <polyline fill="none" stroke="#62d0ff" stroke-width="3" points="{_sparkline_points(acc_values)}"></polyline>
      </svg>
    </div>
    <div class="panel">
      <h2>Brier Score Trend</h2>
      <svg viewBox="0 0 500 100" preserveAspectRatio="none">
        <polyline fill="none" stroke="#7ef29a" stroke-width="3" points="{_sparkline_points(brier_values)}"></polyline>
      </svg>
    </div>
    <div class="panel">
      <h2>Log Loss Trend</h2>
      <svg viewBox="0 0 500 100" preserveAspectRatio="none">
        <polyline fill="none" stroke="#ffb86c" stroke-width="3" points="{_sparkline_points(log_values)}"></polyline>
      </svg>
    </div>
  </div>

  <div class="panel">
    <h2>Model Comparison</h2>
    <table>
      <thead>
        <tr>
          <th>Model</th>
          <th>Evaluated Matches</th>
          <th>Pick Accuracy</th>
          <th>Brier Score</th>
          <th>Log Loss</th>
          <th>ECE</th>
        </tr>
      </thead>
      <tbody>
        {_model_rows(models)}
      </tbody>
    </table>
  </div>

  <div class="panel">
    <h2>Calibration Table \(Best Model\)</h2>
    <table>
      <thead>
        <tr>
          <th>Confidence Bin</th>
          <th>Count</th>
          <th>Avg Predicted</th>
          <th>Actual Frequency</th>
          <th>Gap</th>
        </tr>
      </thead>
      <tbody>
        {_calibration_rows(best_bins)}
      </tbody>
    </table>
  </div>

  <div class="panel">
    <h2>Recent Backtest History</h2>
    <table>
      <thead>
        <tr>
          <th>Generated At (UTC)</th>
          <th>Provider</th>
          <th>Evaluated Matches</th>
          <th>Pick Accuracy</th>
          <th>Brier Score</th>
          <th>Log Loss</th>
        </tr>
      </thead>
      <tbody>
        {_history_rows(history)}
      </tbody>
    </table>
  </div>
</body>
</html>'''
    output_path.write_text(html, encoding='utf-8')
