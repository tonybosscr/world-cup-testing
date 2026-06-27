# World Cup 2026 Prediction Bot

This repository is GitHub-ready.

## Important structure
GitHub workflow files are now correctly placed at repository root:
- `.github/workflows/predict.yml`
- `.github/workflows/pages.yml`

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
