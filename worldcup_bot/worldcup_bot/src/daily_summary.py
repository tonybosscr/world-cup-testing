from typing import Dict, List


def build_daily_summary_text(predictions: List[Dict], selected_model: str, backtest_summary: str, comparison: Dict = None) -> str:
    upcoming = [p for p in predictions][:5]
    lines = [
        '*📊 Daily World Cup Bot Summary*',
        f'*Selected model:* {selected_model}',
        f'*Matches tracked today:* {len(predictions)}',
        ''
    ]

    if upcoming:
        lines.append('*Top upcoming predictions:*')
        for p in upcoming:
            lines.append(
                f"• {p['home_team']} vs {p['away_team']} → {p['predicted_outcome']} ({p['confidence']:.1%})"
            )
        lines.append('')

    if comparison:
        best = comparison.get('best_model', 'N/A')
        lines.append(f'*Best compared model:* {best}')
        lines.append('')

    lines.append(backtest_summary.strip())
    return '\n'.join(lines)
