"""
Configuration settings for the bot
"""

import os

# Bot Token from BotFather
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
PORT = os.getenv('5000")

# Contact Information
CONTACT_INFO = {
    'telegram': '@Sathishkumar33',
    'developer': 'Sathish Kumar'
}

# Channel Information
MOVIE_SEARCH_CHANNEL = 'https://t.me/mraprmoviesrequest'
MOVIE_DOWNLOAD_CHANNEL = 'https://t.me/mraprguildofficialmovies'

# External Services
SHORTENER_URL = 'https://www.mraprguilds.site'
GITHUB_URL = 'https://github.com/Mraprguild'

# API Keys
SHORTENER_API_KEY = os.getenv('SHORTENER_API_KEY', '')

# Bot Settings
BOT_NAME = 'MaprGuild Movie Bot'
BOT_USERNAME = os.getenv('BOT_USERNAME', 'mraprmoviebot')

# Database Settings
DATA_DIR = 'data'
DATABASE_FILE = os.path.join(DATA_DIR, 'bot_data.json')

# Rate Limiting
RATE_LIMIT_REQUESTS = 10  # requests per minute per user
RATE_LIMIT_WINDOW = 60    # seconds

# Copyright Protection Settings
COPYRIGHT_CHECK_ENABLED = True
SPAM_CHECK_ENABLED = True
AUTO_DELETE_VIOLATIONS = True

# Admin Settings
SUPER_ADMIN_ID = os.getenv('SUPER_ADMIN_ID', '')  # Main admin who can add/remove other admins

# Logging Settings
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = 'bot.log'

# Welcome Message Default
DEFAULT_WELCOME_MESSAGE = """
Welcome to MaprGuild Movie Bot! 🎬

Your one-stop destination for movie searches and downloads.
We provide high-quality movies with fast download links.

Use /help to see all available commands.
"""

DEFAULT_BOTTOM_TEXT = """
🌟 **Mrapr Guild - Your Entertainment Partner**

Visit our website and channels for more amazing content!
"""

# Movie Search Settings
MOVIES_PER_PAGE = 10
MAX_SEARCH_RESULTS = 50

# URL Shortener Settings
DEFAULT_EXPIRY_DAYS = 365
CUSTOM_ALIAS_LENGTH = 8

# Channel Management Settings
MAX_MANAGED_CHANNELS = 50

# Feature Flags
ENABLE_MOVIE_SEARCH = True
ENABLE_URL_SHORTENER = True
ENABLE_CHANNEL_MANAGEMENT = True
ENABLE_COPYRIGHT_FILTER = True
ENABLE_ADMIN_PANEL = True
ENABLE_STATISTICS = True

# File Upload Settings
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_FILE_TYPES = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv']

# Cache Settings
CACHE_TTL = 3600  # 1 hour
MAX_CACHE_SIZE = 1000

# Error Messages
ERROR_MESSAGES = {
    'no_permission': '❌ You don\'t have permission to use this command.',
    'invalid_command': '❌ Invalid command usage. Use /help for command list.',
    'rate_limit': '⏱️ You\'re sending messages too quickly. Please wait a moment.',
    'server_error': '❌ A server error occurred. Please try again later.',
    'not_found': '❌ The requested item was not found.',
    'already_exists': '❌ This item already exists.',
}

# Success Messages  
SUCCESS_MESSAGES = {
    'added': '✅ Successfully added!',
    'removed': '✅ Successfully removed!',
    'updated': '✅ Successfully updated!',
    'operation_complete': '✅ Operation completed successfully!',
}

# Validation Rules
MIN_PASSWORD_LENGTH = 8
MAX_USERNAME_LENGTH = 50
MAX_MESSAGE_LENGTH = 4096

# External API Timeouts
API_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
