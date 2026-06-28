# World Cup 2026 Prediction Bot

This repository is GitHub-ready.

## Telegram command menu
The bot now registers these commands:
- `/today` — today’s predictions
- `/next` — next upcoming match prediction
- `/dashboard` — open dashboard prompt
- `/summary` — latest daily summary

These are set automatically during scheduled runs.

## Main app files
- `src/`
- `mini_app/`
- `pages/`
- `output/`
- `data/`
- `config.yaml`
- `requirements.txt`

## Setup
1. Add GitHub Actions secrets:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - `TELEGRAM_WEB_APP_URL` \(after Pages is live\)
2. Open the repo Actions tab.
3. Run `World Cup Prediction Bot`.
4. Then deploy `Deploy GitHub Pages`.

## Mini app URL for your repo
Expected Pages URL:
- `https://tonybosscr.github.io/world-cup-testing/mini_app/`

## Security
Regenerate your Telegram bot token before deployment.
