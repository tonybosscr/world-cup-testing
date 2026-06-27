# GitHub Deployment Guide

## Upload structure
Upload the entire `worldcup_bot` folder into your GitHub repository.

## Required secrets
Go to:
**GitHub → Your Repo → Settings → Secrets and variables → Actions**

Add:
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

Optional for Telegram Mini App button:
- `TELEGRAM_WEB_APP_URL`

## Workflows included
- `.github/workflows/predict.yml` — generates predictions and outputs
- `.github/workflows/pages.yml` — deploys the Pages-ready mini app

## Pages-ready hosting structure
Already prepared in:
- `worldcup_bot/pages/`

Important files:
- `worldcup_bot/pages/index.html`
- `worldcup_bot/pages/mini_app/index.html`
- `worldcup_bot/pages/mini_app/app.js`
- `worldcup_bot/pages/data/dashboard_data.json`

## Recommended first test
1. Run the prediction workflow once.
2. Run or wait for the Pages deploy workflow.
3. Open the GitHub Pages URL.
4. Put that URL into `TELEGRAM_WEB_APP_URL`.
5. Confirm Telegram messages show Open Dashboard.
