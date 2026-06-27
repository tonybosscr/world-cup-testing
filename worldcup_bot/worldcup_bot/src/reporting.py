from typing import Dict


def format_backtest_summary(report: Dict) -> str:
    n = report.get('evaluated_matches', 0)
    if not n:
        return 'Backtest summary: no completed matches available yet.'
    return (
        'Backtest summary\n'
        f"- Evaluated matches: {n}\n"
        f"- Pick accuracy: {report.get('pick_accuracy', 0):.1%}\n"
        f"- Brier score: {report.get('brier_score')}\n"
        f"- Log loss: {report.get('log_loss')}"
    )
