#!/usr/bin/env python3
"""
Telegram Bot for Channel Management with Movie Search and Copyright Protection
Main application entry point with Flask web interface
"""

import os
import logging
import asyncio
import threading
import sys
from flask import Flask, render_template, jsonify, request 
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
from bot.config import BOT_TOKEN

# Configure logging
def setup_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Create handlers
    file_handler = logging.FileHandler('bot.log')
    stream_handler = logging.StreamHandler()
    
    # Create formatters and add it to handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    
    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    
    return logger

logger = setup_logger(__name__)

class MaprGuildMovieBot:
    def __init__(self):
        self.logger = setup_logger("MaprGuildMovieBot")
        self.running = False
        
        if not BOT_TOKEN:
            self.logger.error("BOT_TOKEN environment variable not set!")
            raise ValueError("BOT_TOKEN environment variable not set!")
        
        # Create Telegram application
        self.application = Application.builder().token(BOT_TOKEN).build()
        
        # Register handlers
        self._register_handlers()
        self.logger.info("Bot initialized successfully")
    
    def _register_handlers(self):
        """Register all Telegram bot handlers"""
        # Basic commands
        self.application.add_handler(CommandHandler("start", start_handler))
        self.application.add_handler(CommandHandler("help", help_handler))
        self.application.add_handler(CommandHandler("contact", contact_handler))
        self.application.add_handler(CommandHandler("getid", get_id_handler))
        
        # Welcome message commands
        self.application.add_handler(CommandHandler("welcome", welcome_handler))
        self.application.add_handler(CommandHandler("setwelcome", set_welcome_handler))
        
        # Movie search commands
        self.application.add_handler(CommandHandler("search", movie_search_handler))
        self.application.add_handler(CommandHandler("download", download_handler))
        
        # Admin panel commands
        self.application.add_handler(CommandHandler("admin", admin_panel_handler))
        self.application.add_handler(CommandHandler("addadmin", add_admin_handler))
        self.application.add_handler(CommandHandler("removeadmin", remove_admin_handler))
        self.application.add_handler(CommandHandler("listadmins", list_admins_handler))
        self.application.add_handler(CommandHandler("adminstats", admin_stats_handler))
        
        # Channel management commands
        self.application.add_handler(CommandHandler("addchannel", add_channel_handler))
        self.application.add_handler(CommandHandler("removechannel", remove_channel_handler))
        self.application.add_handler(CommandHandler("listchannels", list_channels_handler))
        self.application.add_handler(CommandHandler("channelstats", channel_stats_handler))
        
        # Copyright protection commands
        self.application.add_handler(CommandHandler("addkeyword", add_keyword_handler))
        self.application.add_handler(CommandHandler("removekeyword", remove_keyword_handler))
        self.application.add_handler(CommandHandler("listkeywords", list_keywords_handler))
        self.application.add_handler(CommandHandler("testai", test_ai_detection_handler))
        
        # Message filter for copyright protection
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_filter_handler))
        
        # Callback query handler for inline buttons
        async def callback_query_handler(update, context):
            await update.callback_query.answer()
        
        self.application.add_handler(CallbackQueryHandler(callback_query_handler))
        
        # Add error handler
        async def error_handler(update, context):
            self.logger.error(f"Exception while handling an update: {context.error}")
        
        self.application.add_error_handler(error_handler)
    
    def start_polling(self):
        """Start the bot in polling mode"""
        self.logger.info("🤖 Starting bot polling...")
        self.running = True
        self.application.run_polling()
    
    def run(self):
        """Main run method"""
        try:
            self.logger.info("🔐 MaprGuild Movie Bot starting up...")
            self.logger.info(f"🌐 Server binding to port {os.getenv('PORT', 5000)}")
            
            # Start bot in a separate thread
            bot_thread = threading.Thread(target=self.start_polling, daemon=True)
            bot_thread.start()
            
            # Start Flask web server
            app = Flask(__name__, template_folder="templates", static_folder="static")
            
            # Setup Flask-SQLAlchemy
            app.secret_key = os.environ.get("FLASK_SECRET_KEY", "a_secret_key_for_bot")
            DATA_DIR = 'data'
            DATABASE_FILE = os.path.join(DATA_DIR, 'bot_data.json')
            
            @app.route("/")
            def index():
                return render_template("index.html")
            
            @app.route("/dashboard")
            def dashboard():
                return render_template("dashboard.html")
            
            @app.route("/health")
            def health():
                return jsonify({"status": "healthy", "bot_running": self.running})
            
            @app.route("/stats")
            def stats():
                # Get basic stats from database
                stats = {
                    'total_users': self.db.get_total_users(),
                    'total_channels': self.db.get_total_channels(),
                    'total_keywords': self.db.get_total_keywords(),
                    'blocked_messages': self.db.get_blocked_messages_count(),
                    'bot_running': self.running
                }
                return jsonify(stats)
            
            # Get port from environment (for deployment)
            PORT = int(os.environ.get("PORT", 5000))
            ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
            
               
        # Start health check server in separate thread
        health_thread = threading.Thread(target=run_health_server)
        health_thread.daemon = True
        health_thread.start()
        
        # Start bot with polling in main thread
        logger.info("Starting bot polling in production mode")
        application.run_polling()
    else:
        # Development mode: Use polling only
        logger.info("Running in development mode with polling")
        application.run_polling()

if __name__ == '__main__':
    main()
    
