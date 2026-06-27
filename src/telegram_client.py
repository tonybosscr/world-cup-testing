import os
import requests


def send_telegram_message(bot_token: str, chat_id: str, text: str, web_app_url: str = None):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': True,
    }

    launch_url = web_app_url or os.getenv('TELEGRAM_WEB_APP_URL', '').strip()
    if launch_url:
        payload['reply_markup'] = {
            'inline_keyboard': [[
                {
                    'text': 'Open Dashboard',
                    'web_app': {'url': launch_url}
                }
            ]]
        }

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
