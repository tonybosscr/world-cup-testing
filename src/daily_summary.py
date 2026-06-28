from typing import Dict, List


def build_daily_summary_text(predictions: List[Dict], selected_model: str, backtest_summary: str, comparison: Dict = None) -> str:
    upcoming = [p for p in predictions][:5]
    lines = [
        '*🏆 World Cup Trading Desk — Daily Summary*',
        f'*Selected model:* {selected_model}',
        f'*Matches on radar today:* {len(predictions)}',
        ''
    ]

    if upcoming:
        lines.append('*Top edges today:*')
        for p in upcoming:
            lines.append(
                f"• *{p['home_team']} vs {p['away_team']}* → {p['predicted_outcome']} | Confidence: {p['confidence']:.1%}"
            )
        lines.append('')

    if comparison:
        best = comparison.get('best_model', 'N/A')
        lines.append(f'*Best active model:* {best}')
        lines.append('')

    lines.append(backtest_summary.strip())
    lines.append('')
    lines.append('_Use the dashboard button below to view today\'s full prediction board\._')
    return '\n'.join(lines)
