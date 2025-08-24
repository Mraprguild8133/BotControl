"""
Utility functions for the bot
"""

import os
import re
import logging
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from functools import wraps

logger = logging.getLogger(__name__)

def validate_user_id(user_id: Any) -> bool:
    """Validate if user_id is a valid Telegram user ID"""
    try:
        user_id = int(user_id)
        return 0 < user_id < 2**63 - 1  # Valid Telegram user ID range
    except (ValueError, TypeError):
        return False

def validate_channel_id(channel_id: str) -> bool:
    """Validate if channel_id is a valid format"""
    if not channel_id:
        return False
    
    # Check for @username format
    if channel_id.startswith('@') and len(channel_id) > 1:
        return bool(re.match(r'^@[a-zA-Z0-9_]{5,32}$', channel_id))
    
    # Check for numeric ID format (-100...)
    if channel_id.startswith('-100') and len(channel_id) > 4:
        return validate_user_id(channel_id)
    
    # Check for plain username
    if re.match(r'^[a-zA-Z0-9_]{5,32}$', channel_id):
        return True
    
    return False

def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes = size_bytes / 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def format_duration(seconds: int) -> str:
    """Format duration in human-readable format"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove multiple underscores
    sanitized = re.sub(r'_{2,}', '_', sanitized)
    
    # Trim and ensure it's not empty
    sanitized = sanitized.strip('_. ')
    
    if not sanitized:
        sanitized = "untitled"
    
    return sanitized

def extract_movie_year(title: str) -> Optional[str]:
    """Extract year from movie title"""
    year_pattern = r'\b(19|20)\d{2}\b'
    matches = re.findall(year_pattern, title)
    
    if matches:
        # Return the last year found (most likely the release year)
        return matches[-1]
    
    return None

def clean_movie_title(title: str) -> str:
    """Clean movie title by removing quality indicators, years, etc."""
    # Remove quality indicators
    quality_patterns = [
        r'\b(720p|1080p|4K|HD|BluRay|BRRip|DVDRip|WEBRip|CAM|TS|TC)\b',
        r'\b(x264|x265|HEVC|H\.264|H\.265)\b',
        r'\[\w+\]',  # Remove [tags]
        r'\(\d{4}\)',  # Remove (year)
    ]
    
    cleaned = title
    for pattern in quality_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    # Clean up extra spaces
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned

def generate_short_id(length: int = 8) -> str:
    """Generate a random short ID"""
    import random
    import string
    
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def hash_string(text: str) -> str:
    """Generate SHA-256 hash of a string"""
    return hashlib.sha256(text.encode()).hexdigest()

def is_valid_url(url: str) -> bool:
    """Check if URL is valid"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return url_pattern.match(url) is not None

def rate_limit(max_calls: int = 10, window: int = 60):
    """Rate limiting decorator"""
    calls = {}
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user_id from update
            update = args[0] if args else None
            if not hasattr(update, 'effective_user') or not update.effective_user:
                return await func(*args, **kwargs)
            
            user_id = update.effective_user.id
            now = datetime.now()
            
            # Clean old entries
            cutoff = now - timedelta(seconds=window)
            calls[user_id] = [call_time for call_time in calls.get(user_id, []) if call_time > cutoff]
            
            # Check rate limit
            if len(calls.get(user_id, [])) >= max_calls:
                if update.message:
                    await update.message.reply_text(
                        f"⏱️ Too many requests! Please wait {window} seconds before trying again."
                    )
                return
            
            # Add current call
            calls.setdefault(user_id, []).append(now)
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

def log_command_usage(command_name: str, user_id: int, success: bool = True):
    """Log command usage for analytics"""
    from .database import add_user_activity
    
    try:
        add_user_activity(
            user_id=user_id,
            activity='command_used',
            details={
                'command': command_name,
                'success': success,
                'timestamp': datetime.now().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Error logging command usage: {e}")

def escape_markdown(text: str) -> str:
    """Escape special characters for Markdown"""
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    
    return text

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def parse_time_string(time_str: str) -> Optional[int]:
    """Parse time string like '1h30m' or '90m' into seconds"""
    time_pattern = r'(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?'
    match = re.match(time_pattern, time_str.lower())
    
    if not match:
        return None
    
    hours, minutes, seconds = match.groups()
    
    total_seconds = 0
    if hours:
        total_seconds += int(hours) * 3600
    if minutes:
        total_seconds += int(minutes) * 60
    if seconds:
        total_seconds += int(seconds)
    
    return total_seconds if total_seconds > 0 else None

def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return os.path.splitext(filename.lower())[1]

def is_image_file(filename: str) -> bool:
    """Check if file is an image"""
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']
    return get_file_extension(filename) in image_extensions

def is_video_file(filename: str) -> bool:
    """Check if file is a video"""
    video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v']
    return get_file_extension(filename) in video_extensions

def format_user_mention(user) -> str:
    """Format user mention for display"""
    if hasattr(user, 'username') and user.username:
        return f"@{user.username}"
    elif hasattr(user, 'first_name'):
        name = user.first_name
        if hasattr(user, 'last_name') and user.last_name:
            name += f" {user.last_name}"
        return name
    else:
        return f"User {user.id}"

def get_system_info() -> Dict[str, Any]:
    """Get basic system information"""
    import psutil
    import platform
    
    try:
        return {
            'platform': platform.system(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': format_file_size(psutil.virtual_memory().total),
            'memory_available': format_file_size(psutil.virtual_memory().available),
            'disk_usage': format_file_size(psutil.disk_usage('/').used),
        }
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return {'error': 'Unable to retrieve system information'}

def create_pagination_buttons(current_page: int, total_pages: int, callback_prefix: str):
    """Create pagination buttons for inline keyboard"""
    from telegram import InlineKeyboardButton
    
    buttons = []
    
    if current_page > 1:
        buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"{callback_prefix}_{current_page - 1}"))
    
    buttons.append(InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="page_info"))
    
    if current_page < total_pages:
        buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"{callback_prefix}_{current_page + 1}"))
    
    return [buttons] if buttons else []
