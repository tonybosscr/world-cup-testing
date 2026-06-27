# Hosting the Telegram Mini App

## Easiest option: GitHub Pages-ready structure included
This project now includes a publish-ready folder:
- `worldcup_bot/pages/`

It contains:
- `pages/index.html`
- `pages/mini_app/index.html`
- `pages/mini_app/app.js`
- `pages/data/dashboard_data.json`

The bot copies fresh dashboard data into the Pages folder automatically during runs.

## Recommended setup
1. Push the project to GitHub.
2. Enable GitHub Pages permissions if prompted.
3. Use the included workflow:
   - `.github/workflows/pages.yml`
4. After deployment, your app URL will look like:
   - `https://yourusername.github.io/yourrepo/mini_app/`
   or the repo Pages base URL redirecting into the mini app.

## Telegram setup
Set this secret or variable:
- `TELEGRAM_WEB_APP_URL`

Point it to your GitHub Pages mini app URL.

## BotFather note
You can also set your bot menu button in BotFather to open the same web app URL.
