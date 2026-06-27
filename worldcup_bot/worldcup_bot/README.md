# World Cup 2026 Prediction Bot

A GitHub Actions–powered Telegram prediction bot for FIFA World Cup 2026.

## New additions
- Telegram Web App / Mini App-ready dashboard
- Open Dashboard button in Telegram messages
- Daily Telegram summary

## Telegram Web App support
The bot now supports a hosted mini app dashboard.

Files:
- `mini_app/index.html`
- `mini_app/app.js`
- `mini_app/HOSTING_GUIDE.md`

If `TELEGRAM_WEB_APP_URL` is set, Telegram messages will include an **Open Dashboard** button.

## To enable it
1. Host the mini app.
2. Set:
   - `TELEGRAM_WEB_APP_URL`
3. Deploy the workflow.

## Dashboard features
- today’s predictions
- selected model
- model comparison
- backtest stats
- button to show current upcoming match prediction

## Security note
If your Telegram token was exposed, regenerate it in BotFather before deployment.
