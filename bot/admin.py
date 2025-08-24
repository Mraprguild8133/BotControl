"""
Admin functionality for the Telegram bot
"""

import json
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

def load_admin_ids():
    """Load admin IDs from file"""
    try:
        with open('data/admin_ids.json', 'r') as f:
            data = json.load(f)
            return data.get('admin_ids', [])
    except (FileNotFoundError, json.JSONDecodeError):
        # Default admin ID - replace with actual admin ID
        return []

def save_admin_ids(admin_ids):
    """Save admin IDs to file"""
    try:
        data = {
            'admin_ids': admin_ids,
            'last_updated': datetime.now().isoformat()
        }
        with open('data/admin_ids.json', 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving admin IDs: {e}")
        return False

def is_admin(user_id):
    """Check if user is an admin"""
    admin_ids = load_admin_ids()
    return user_id in admin_ids

def add_admin(user_id):
    """Add a new admin"""
    admin_ids = load_admin_ids()
    if user_id not in admin_ids:
        admin_ids.append(user_id)
        return save_admin_ids(admin_ids)
    return False

def remove_admin(user_id):
    """Remove an admin"""
    admin_ids = load_admin_ids()
    if user_id in admin_ids:
        admin_ids.remove(user_id)
        return save_admin_ids(admin_ids)
    return False

async def admin_panel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command - show admin panel"""
    if not update.message or not update.effective_user:
        return
        
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You don't have permission to access the admin panel.")
        return

    admin_ids = load_admin_ids()
    
    message = f"""
👑 **Admin Panel**

**Bot Status:** 🟢 Online
**Total Admins:** {len(admin_ids)}
**Your ID:** `{update.effective_user.id}`

**Available Commands:**
👤 `/addadmin [user_id]` - Add admin
❌ `/removeadmin [user_id]` - Remove admin
📋 `/listadmins` - List all admins
📊 `/adminstats` - Admin statistics

**Channel Management:**
📺 `/addchannel [channel_id]` - Add channel
🗑️ `/removechannel [channel_id]` - Remove channel
📋 `/listchannels` - List channels
📊 `/channelstats` - Channel statistics

**Copyright Protection:**
🚫 `/addkeyword [keyword]` - Add keyword
✅ `/removekeyword [keyword]` - Remove keyword

**Content Management:**
💬 `/setwelcome [message]` - Set welcome message
📝 `/welcome` - View current welcome message

**System:**
🔄 Bot restart - Contact developer
📊 View logs - Contact developer
"""
    
    keyboard = [
        [
            InlineKeyboardButton("📊 Statistics", callback_data="admin_stats"),
            InlineKeyboardButton("📋 Channels", callback_data="list_channels")
        ],
        [
            InlineKeyboardButton("🚫 Keywords", callback_data="copyright_keywords"),
            InlineKeyboardButton("💬 Welcome", callback_data="welcome_config")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        message,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def add_admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /addadmin command"""
    if not update.message or not update.effective_user:
        return
        
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return

    if not context.args:
        await update.message.reply_text("Usage: `/addadmin [user_id]`", parse_mode='Markdown')
        return

    try:
        new_admin_id = int(context.args[0])
        
        if add_admin(new_admin_id):
            await update.message.reply_text(f"✅ User `{new_admin_id}` has been added as admin.", parse_mode='Markdown')
            logger.info(f"Admin {update.effective_user.id} added new admin {new_admin_id}")
        else:
            await update.message.reply_text(f"❌ User `{new_admin_id}` is already an admin.", parse_mode='Markdown')
    
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID. Please provide a numeric user ID.")
    except Exception as e:
        logger.error(f"Error adding admin: {e}")
        await update.message.reply_text("❌ An error occurred while adding admin.")

async def remove_admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /removeadmin command"""
    if not update.message or not update.effective_user:
        return
        
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return

    if not context.args:
        await update.message.reply_text("Usage: `/removeadmin [user_id]`", parse_mode='Markdown')
        return

    try:
        remove_admin_id = int(context.args[0])
        
        # Prevent removing self
        if remove_admin_id == update.effective_user.id:
            await update.message.reply_text("❌ You cannot remove yourself as admin.")
            return
        
        if remove_admin(remove_admin_id):
            await update.message.reply_text(f"✅ User `{remove_admin_id}` has been removed from admins.", parse_mode='Markdown')
            logger.info(f"Admin {update.effective_user.id} removed admin {remove_admin_id}")
        else:
            await update.message.reply_text(f"❌ User `{remove_admin_id}` is not an admin.", parse_mode='Markdown')
    
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID. Please provide a numeric user ID.")
    except Exception as e:
        logger.error(f"Error removing admin: {e}")
        await update.message.reply_text("❌ An error occurred while removing admin.")

async def list_admins_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /listadmins command"""
    if not update.message or not update.effective_user:
        return
        
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return

    admin_ids = load_admin_ids()
    
    if not admin_ids:
        await update.message.reply_text("📋 No admins found.")
        return
    
    message = "👑 **Admin List**\n\n"
    for i, admin_id in enumerate(admin_ids, 1):
        status = "👤" if admin_id != update.effective_user.id else "👑 (You)"
        message += f"{i}. `{admin_id}` {status}\n"
    
    message += f"\n**Total Admins:** {len(admin_ids)}"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def admin_stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /adminstats command"""
    if not update.message or not update.effective_user:
        return
        
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return

    from .database import get_bot_stats
    
    admin_ids = load_admin_ids()
    stats = get_bot_stats()
    
    message = f"""
📊 **Bot Statistics**

👑 **Admins:** {len(admin_ids)}
📺 **Managed Channels:** {stats.get('channels', 0)}
🚫 **Copyright Keywords:** {stats.get('keywords', 0)}
👥 **Total Users:** {stats.get('users', 'N/A')}
📝 **Messages Processed:** {stats.get('messages', 'N/A')}
🔍 **Movie Searches:** {stats.get('searches', 'N/A')}
📥 **Download Requests:** {stats.get('downloads', 'N/A')}

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**System Info:**
🟢 Bot Status: Online
🔄 Uptime: {stats.get('uptime', 'N/A')}
💾 Memory Usage: {stats.get('memory', 'N/A')}
"""
    
    await update.message.reply_text(message, parse_mode='Markdown')
