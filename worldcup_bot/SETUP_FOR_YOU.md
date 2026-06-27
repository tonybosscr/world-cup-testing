# Setup Notes For You

## 1. Regenerate your Telegram bot token first
Your previous bot token was exposed in chat. For safety:
- open BotFather on Telegram
- revoke the old token
- create a new token
- use the new one in GitHub Secrets

## 2. GitHub Secrets to add
- `TELEGRAM_BOT_TOKEN` = your new regenerated token
- `TELEGRAM_CHAT_ID` = `7925309509`

## 3. Recommended free deployment
Use **GitHub Actions**.

## 4. Current upgraded features
- real API integration structure
- default free World Cup 2026 data provider
- Elo/form-based simulation model
- professional Telegram alert message formatting
- scheduled background runs

## 5. Next possible upgrades
- connect a paid/deeper football stats API
- add real recent-results ingestion
- add backtesting dashboard
- add confidence calibration report
