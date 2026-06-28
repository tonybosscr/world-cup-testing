import json
import os
from pathlib import Path
from datetime import datetime, timezone

import yaml

from backtest import backtest_predictions
from daily_summary import build_daily_summary_text
from dashboard import build_dashboard
from dashboard_data_builder import build_dashboard_data
from data_pipeline import fetch_matches_and_strengths
from model import build_predictions
from model_comparison import compare_models
from model_selection import select_best_model_name, select_stable_model
from performance_tracker import append_history, append_model_comparison_history, load_history, summarize_history
from publish_pages import publish_pages_files
from reporting import format_backtest_summary
from telegram_client import send_telegram_message, escape_md, set_bot_commands, get_updates
from telegram_commands import bot_commands, parse_command, format_today_response, format_next_response, format_dashboard_response, format_summary_response
from utils import ensure_dirs, should_send_pre_match_alert, iso_to_local, safe_json_dump

BASE = Path(__file__).resolve().parents[1]
CONFIG_PATH = BASE / 'config.yaml'
OUTPUT_DIR = BASE / 'output'
STATE_PATH = OUTPUT_DIR / 'sent_alerts.json'
HISTORY_PATH = OUTPUT_DIR / 'performance_history.json'
MODEL_COMPARISON_HISTORY_PATH = OUTPUT_DIR / 'model_comparison_history.json'
DASHBOARD_PATH = OUTPUT_DIR / 'backtest_dashboard.html'
SELECTED_MODEL_PATH = OUTPUT_DIR / 'selected_model.json'


def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_state():
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding='utf-8'))
    return {"sent_match_ids": [], "daily_summary_sent_dates": [], "telegram_update_offset": None}


def save_state(state):
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding='utf-8')


def format_prediction_message(pred):
    kickoff_local = escape_md(iso_to_local(pred['kickoff_utc'], pred['timezone']))
    stage = escape_md(pred.get('stage') or '-')
    venue = escape_md(pred.get('venue') or '-')
    group = escape_md(pred.get('group') or '-')
    home = escape_md(pred['home_team'])
    away = escape_md(pred['away_team'])
    outcome = escape_md(pred['predicted_outcome'])
    selected_model = escape_md(pred.get('selected_model', 'baseline_main'))
    top_scores = pred.get('top_scorelines', [])
    score_text = 'N/A'
    if top_scores:
        score_text = ', '.join([f"{escape_md(item['score'])} ({item['probability']:.1%})" for item in top_scores])
    return (
        f"*🏆 FIFA World Cup 2026 Prediction Alert*\n"
        f"*Match:* {home} vs {away}\n"
        f"*Kickoff:* {kickoff_local}\n"
        f"*Stage:* {stage} | *Group:* {group}\n"
        f"*Venue:* {venue}\n"
        f"*Model Used:* {selected_model}\n\n"
        f"*Win Probabilities*\n"
        f"• {home}: *{pred['home_win_prob']:.1%}*\n"
        f"• Draw: *{pred['draw_prob']:.1%}*\n"
        f"• {away}: *{pred['away_win_prob']:.1%}*\n\n"
        f"*Model Pick:* {outcome} \({pred['confidence']:.1%} confidence\)\n"
        f"*Expected Goals:* {pred['expected_goals_home']:.2f} - {pred['expected_goals_away']:.2f}\n"
        f"*Most Likely Scorelines:* {score_text}\n"
        f"*Simulation Runs:* {pred['simulation_runs']}\n\n"
        f"_{escape_md(pred['notes'])}_"
    )


def should_send_daily_summary(now_utc, sent_dates):
    date_key = now_utc.date().isoformat()
    return now_utc.hour >= 7 and date_key not in sent_dates


def handle_command_updates(bot_token, default_chat_id, predictions, daily_summary_text, state):
    try:
        updates = get_updates(bot_token, offset=state.get('telegram_update_offset'), timeout_seconds=1)
    except Exception:
        return state

    for item in updates.get('result', []):
        update_id = item.get('update_id')
        if update_id is not None:
            state['telegram_update_offset'] = update_id + 1

        msg = item.get('message', {})
        text = msg.get('text', '')
        chat_id = str((msg.get('chat') or {}).get('id') or default_chat_id)
        cmd = parse_command(text)

        if cmd == '/today':
            send_telegram_message(bot_token, chat_id, format_today_response(predictions))
        elif cmd == '/next':
            send_telegram_message(bot_token, chat_id, format_next_response(predictions))
        elif cmd == '/dashboard':
            send_telegram_message(bot_token, chat_id, format_dashboard_response())
        elif cmd == '/summary':
            send_telegram_message(bot_token, chat_id, format_summary_response(daily_summary_text))

    return state


def main():
    ensure_dirs([OUTPUT_DIR, BASE / 'data', BASE / 'mini_app', BASE / 'pages'])
    config = load_config()
    matches, strengths, recent_results = fetch_matches_and_strengths(config, BASE / 'data')

    comparison = None
    selection_meta = {'selected_model': config.get('model_comparison', {}).get('fallback_model', 'baseline_main'), 'selection_mode': 'fallback', 'reason': 'Backtest/model comparison disabled'}

    if config.get('backtest', {}).get('enabled', True):
        comparison = compare_models(matches=matches, strengths=strengths, runs_per_model=int(config.get('model_comparison', {}).get('simulation_runs', 4000)))
        safe_json_dump(OUTPUT_DIR / 'model_comparison.json', comparison)
        append_model_comparison_history(MODEL_COMPARISON_HISTORY_PATH, comparison)

        if config.get('model_comparison', {}).get('auto_select_best_model', True):
            if config.get('model_comparison', {}).get('stable_selection', {}).get('enabled', True):
                stable_cfg = config.get('model_comparison', {}).get('stable_selection', {})
                selection_meta = select_stable_model(comparison=comparison, comparison_history=load_history(MODEL_COMPARISON_HISTORY_PATH), selected_model_path=SELECTED_MODEL_PATH, fallback_model=config.get('model_comparison', {}).get('fallback_model', 'baseline_main'), min_evaluated_matches=int(stable_cfg.get('min_evaluated_matches', 12)), rolling_window=int(stable_cfg.get('rolling_window', 5)), switch_margin=float(stable_cfg.get('switch_margin', 1.5)))
                selection_meta['selection_mode'] = 'stable'
            else:
                selection_meta = {'selected_model': select_best_model_name(comparison, fallback=config.get('model_comparison', {}).get('fallback_model', 'baseline_main')), 'selection_mode': 'instant', 'reason': 'Best current model selected without stability smoothing.'}

    selected_model_name = selection_meta['selected_model']
    safe_json_dump(SELECTED_MODEL_PATH, {'selected_model': selected_model_name, 'auto_selected': bool(config.get('model_comparison', {}).get('auto_select_best_model', True)), 'selection_mode': selection_meta.get('selection_mode', 'unknown'), 'reason': selection_meta.get('reason', ''), 'rolling_scores': selection_meta.get('rolling_scores', {}), 'generated_at_utc': datetime.now(timezone.utc).isoformat()})

    predictions = build_predictions(matches=matches, strengths=strengths, config=config, selected_model_name=selected_model_name)
    timestamp = datetime.now(timezone.utc).isoformat()
    provider_name = config.get('data_provider', {}).get('name', 'worldcup26_free')
    safe_json_dump(OUTPUT_DIR / 'predictions.json', {'generated_at_utc': timestamp, 'provider': provider_name, 'selected_model': selected_model_name, 'predictions': predictions})

    backtest_summary_text = 'Backtest summary: unavailable.'
    if config.get('backtest', {}).get('enabled', True):
        report = backtest_predictions(matches=matches, strengths=strengths, runs=int(config.get('backtest', {}).get('simulation_runs', 4000)))
        safe_json_dump(OUTPUT_DIR / 'backtest_report.json', report)
        backtest_summary_text = format_backtest_summary(report)
        (OUTPUT_DIR / 'backtest_summary.txt').write_text(backtest_summary_text, encoding='utf-8')
        history = append_history(HISTORY_PATH, report, provider_name)
        history_summary = summarize_history(history)
        safe_json_dump(OUTPUT_DIR / 'performance_summary.json', history_summary)
        build_dashboard(DASHBOARD_PATH, history, history_summary, report, comparison)

    build_dashboard_data(OUTPUT_DIR)
    publish_pages_files(BASE, OUTPUT_DIR)

    bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '').strip()
    chat_id = os.getenv('TELEGRAM_CHAT_ID', '').strip()
    state = load_state()

    daily_summary_text = build_daily_summary_text(predictions, selected_model_name, backtest_summary_text, comparison)

    if bot_token and chat_id:
        try:
            set_bot_commands(bot_token, bot_commands())
        except Exception:
            pass

        sent_ids = set(state.get('sent_match_ids', []))
        for pred in predictions:
            if should_send_pre_match_alert(pred['kickoff_utc'], config.get('timezone', 'Africa/Lagos'), hours_before=config['schedule']['pre_match_alert_hours']):
                match_key = f"{pred['match_id']}:{pred['kickoff_utc']}"
                if match_key not in sent_ids:
                    send_telegram_message(bot_token, chat_id, format_prediction_message(pred))
                    sent_ids.add(match_key)
        state['sent_match_ids'] = sorted(sent_ids)

        now_utc = datetime.now(timezone.utc)
        sent_dates = set(state.get('daily_summary_sent_dates', []))
        if should_send_daily_summary(now_utc, sent_dates):
            send_telegram_message(bot_token, chat_id, daily_summary_text)
            date_key = now_utc.date().isoformat()
            sent_dates.add(date_key)
            state['daily_summary_sent_dates'] = sorted(sent_dates)

        state = handle_command_updates(bot_token, chat_id, predictions, daily_summary_text, state)
        save_state(state)

    summary_lines = [
        f"Generated {len(predictions)} predictions at {timestamp}",
        f"Provider: {provider_name}",
        f"Timezone: {config.get('timezone', 'Africa/Lagos')}",
        f"Recent-results teams: {len(recent_results)}",
        f"Selected model: {selected_model_name}",
        f"Selection mode: {selection_meta.get('selection_mode', 'unknown')}",
        f"Selection reason: {selection_meta.get('reason', '')}",
        f"Best model from comparison: {comparison.get('best_model') if comparison else 'N/A'}",
    ]
    (OUTPUT_DIR / 'summary.txt').write_text('\n'.join(summary_lines), encoding='utf-8')


if __name__ == '__main__':
    main()
