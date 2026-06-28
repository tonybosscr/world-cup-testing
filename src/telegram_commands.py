from typing import Dict, List, Tuple


def bot_commands():
    return [
        {'command': 'today', 'description': 'Show today\'s predictions'},
        {'command': 'next', 'description': 'Show the upcoming match prediction'},
        {'command': 'dashboard', 'description': 'Open the dashboard'},
        {'command': 'summary', 'description': 'Show the latest daily summary'},
    ]


def parse_command(text: str) -> str:
    if not text:
        return ''
    text = text.strip().split()[0].lower()
    return text


def format_today_response(predictions: List[Dict]) -> str:
    if not predictions:
        return '*🗓 Today\'s Predictions*\nNo predictions available right now\.'
    lines = ['*🗓 Today\'s Predictions*']
    for p in predictions[:8]:
        lines.append(f"• *{p['home_team']} vs {p['away_team']}* → {p['predicted_outcome']} \({p['confidence']:.1%}\)")
    return '\n'.join(lines)


def format_next_response(predictions: List[Dict]) -> str:
    if not predictions:
        return '*⏭ Upcoming Match*\nNo upcoming prediction available\.'
    p = predictions[0]
    return (
        '*⏭ Upcoming Match Prediction*\n'
        f"*{p['home_team']} vs {p['away_team']}*\n"
        f"Pick: {p['predicted_outcome']} \({p['confidence']:.1%}\)\n"
        f"Win board: {p['home_team']} {p['home_win_prob']:.1%} • Draw {p['draw_prob']:.1%} • {p['away_team']} {p['away_win_prob']:.1%}"
    )


def format_dashboard_response() -> str:
    return '*📊 Dashboard*\nUse the button below to open the live dashboard\.'


def format_summary_response(summary_text: str) -> str:
    return summary_text or '*📈 Summary*\nNo summary available yet\.'
