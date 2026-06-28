import os
import requests
from typing import List, Dict


def build_reply_markup(web_app_url: str = None):
    launch_url = web_app_url or os.getenv('TELEGRAM_WEB_APP_URL', '').strip()
    if not launch_url:
        return None
    return {
        'inline_keyboard': [
            [
                {'text': '📊 Open Dashboard', 'web_app': {'url': launch_url}},
                {'text': '🗓 Predictions Today', 'web_app': {'url': launch_url}},
            ]
        ]
    }


def send_telegram_message(bot_token: str, chat_id: str, text: str, web_app_url: str = None):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': True,
    }
    reply_markup = build_reply_markup(web_app_url)
    if reply_markup:
        payload['reply_markup'] = reply_markup
    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def set_bot_commands(bot_token: str, commands: List[Dict]):
    url = f"https://api.telegram.org/bot{bot_token}/setMyCommands"
    response = requests.post(url, json={'commands': commands}, timeout=30)
    response.raise_for_status()
    return response.json()


def get_updates(bot_token: str, offset: int = None, timeout_seconds: int = 1):
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    payload = {'timeout': timeout_seconds}
    if offset is not None:
        payload['offset'] = offset
    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def escape_md(text: str) -> str:
    if text is None:
        return ''
    chars = r'_[]()~`>#+-=|{}.!'
    out = str(text)
    for ch in chars:
        out = out.replace(ch, f'\\{ch}')
    return out
