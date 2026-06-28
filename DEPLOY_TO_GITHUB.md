# GitHub Deployment Guide

## Bot commands now supported
- `/today`
- `/next`
- `/dashboard`
- `/summary`

The workflow sets these commands automatically when the bot runs.

## Upload structure
Upload the entire project contents into your GitHub repository root.

## Required secrets
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `TELEGRAM_WEB_APP_URL` \(optional until Pages is live\)

## Workflows included
- `.github/workflows/predict.yml`
- `.github/workflows/pages.yml`
