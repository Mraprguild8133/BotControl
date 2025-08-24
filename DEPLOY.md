# Render.com Deployment Guide

## Quick Deploy to Render.com

1. **Fork/Upload your code** to GitHub
2. **Connect Render.com** to your GitHub repository
3. **Set Environment Variables** in Render.com:
   - `ENVIRONMENT` = `production`
   - `BOT_TOKEN` = Your Telegram bot token
   - `SHORTENER_API_KEY` = Your shortener API key (optional)
   - `SUPER_ADMIN_ID` = Your Telegram user ID
   - `BOT_USERNAME` = Your bot's username

4. **Deploy**: Render.com will automatically use the `render.yaml` configuration

## Environment Variables Required

```
ENVIRONMENT=production
BOT_TOKEN=your_bot_token_here
PORT=10000 (automatically set by Render.com)
```

## Health Check

The bot includes a health check endpoint at `/health` that Render.com will use to monitor the service.

## Development vs Production

- **Development**: Uses polling mode (local development)
- **Production**: Uses webhook server mode (Render.com compatible)

The bot automatically detects the environment and switches modes accordingly.