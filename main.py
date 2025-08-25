#!/usr/bin/env python3
"""
Telegram Bot for Channel Management with Movie Search and Copyright Protection
Main application entry point
"""

import os
import logging
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from aiohttp import web
from aiohttp.web_runner import GracefulExit

from bot.handlers import (
    start_handler, help_handler, contact_handler, welcome_handler,
    set_welcome_handler, movie_search_handler, download_handler, get_id_handler
)
from bot.admin import (
    admin_panel_handler, add_admin_handler, remove_admin_handler,
    list_admins_handler, admin_stats_handler
)
from bot.channel_manager import (
    add_channel_handler, remove_channel_handler, list_channels_handler,
    channel_stats_handler
)
from bot.copyright_filter import message_filter_handler, add_keyword_handler, remove_keyword_handler, list_keywords_handler, test_ai_detection_handler

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = os.environ.get("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 5000))

async def health_check(request):
    """Health check endpoint for Render.com"""
    return web.Response(text="Bot is running", status=200)

async def webhook_handler(request):
    """Handle webhook updates from Telegram"""
    return web.Response(text="Webhook received", status=200)

async def start_production_server(port):
    """Start health check server for production"""
    # Create web application for health checks
    web_app = web.Application()
    web_app.router.add_get("/health", health_check)
    web_app.router.add_post("/webhook", webhook_handler)
    
    # Create and start web server for health checks
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    
    logger.info(f"Health check server started on 0.0.0.0:{port}")
    logger.info("Bot running in production mode with polling + health server")
    
    return runner

async def run_bot():
    """Run the Telegram bot"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN environment variable not set!")
        return

    # Get environment mode
    ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
    
    logger.info(f"Starting bot in {ENVIRONMENT} mode on port {PORT}")

    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Basic commands
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("contact", contact_handler))
    application.add_handler(CommandHandler("getid", get_id_handler))
    
    # Welcome message commands
    application.add_handler(CommandHandler("welcome", welcome_handler))
    application.add_handler(CommandHandler("setwelcome", set_welcome_handler))
    
    # Movie search commands
    application.add_handler(CommandHandler("search", movie_search_handler))
    application.add_handler(CommandHandler("download", download_handler))
    
    # Admin panel commands
    application.add_handler(CommandHandler("admin", admin_panel_handler))
    application.add_handler(CommandHandler("addadmin", add_admin_handler))
    application.add_handler(CommandHandler("removeadmin", remove_admin_handler))
    application.add_handler(CommandHandler("listadmins", list_admins_handler))
    application.add_handler(CommandHandler("adminstats", admin_stats_handler))
    
    # Channel management commands
    application.add_handler(CommandHandler("addchannel", add_channel_handler))
    application.add_handler(CommandHandler("removechannel", remove_channel_handler))
    application.add_handler(CommandHandler("listchannels", list_channels_handler))
    application.add_handler(CommandHandler("channelstats", channel_stats_handler))
    
    # Copyright protection commands
    application.add_handler(CommandHandler("addkeyword", add_keyword_handler))
    application.add_handler(CommandHandler("removekeyword", remove_keyword_handler))
    application.add_handler(CommandHandler("listkeywords", list_keywords_handler))
    application.add_handler(CommandHandler("testai", test_ai_detection_handler))
    
    # Message filter for copyright protection
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_filter_handler))
    
    # Callback query handler for inline buttons
    async def callback_query_handler(update, context):
        await update.callback_query.answer()
    
    application.add_handler(CallbackQueryHandler(callback_query_handler))

    # Add error handler
    async def error_handler(update, context):
        logger.error(f"Exception while handling an update: {context.error}")
    
    application.add_error_handler(error_handler)
    
    logger.info("Bot handlers configured successfully!")
    
    # Check if running in production or development
    if ENVIRONMENT == "production":
        # Start health check server
        runner = await start_production_server(PORT)
        
        try:
            # Start the bot with polling
            logger.info("Starting bot polling in production mode")
            await application.initialize()
            await application.start()
            await application.updater.start_polling()
            
            # Keep both services running
            while True:
                await asyncio.sleep(3600)  # Sleep for 1 hour
                
        except (KeyboardInterrupt, GracefulExit):
            logger.info("Shutting down bot and health server...")
        finally:
            # Cleanup
            await application.updater.stop()
            await application.stop()
            await application.shutdown()
            await runner.cleanup()
    else:
        # Development mode: Use polling only
        logger.info("Running in development mode with polling")
        await application.run_polling()

def main():
    """Main entry point"""
    asyncio.run(run_bot())

if __name__ == '__main__':
    main()
