"""
Channel management functionality
"""

import json
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

from .admin import is_admin

logger = logging.getLogger(__name__)

def load_channels():
    """Load managed channels from file"""
    try:
        with open('data/channels.json', 'r') as f:
            data = json.load(f)
            return data.get('channels', [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_channels(channels):
    """Save channels to file"""
    try:
        data = {
            'channels': channels,
            'last_updated': datetime.now().isoformat()
        }
        with open('data/channels.json', 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving channels: {e}")
        return False

def add_channel(channel_id, channel_name=None):
    """Add a new channel to management"""
    channels = load_channels()
    
    # Check if channel already exists
    for channel in channels:
        if channel['id'] == channel_id:
            return False
    
    new_channel = {
        'id': channel_id,
        'name': channel_name or f"Channel {channel_id}",
        'added_date': datetime.now().isoformat(),
        'status': 'active'
    }
    
    channels.append(new_channel)
    return save_channels(channels)

def remove_channel(channel_id):
    """Remove a channel from management"""
    channels = load_channels()
    
    for i, channel in enumerate(channels):
        if channel['id'] == channel_id:
            channels.pop(i)
            return save_channels(channels)
    
    return False

def get_channel_by_id(channel_id):
    """Get channel information by ID"""
    channels = load_channels()
    for channel in channels:
        if channel['id'] == channel_id:
            return channel
    return None

async def add_channel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /addchannel command"""
    if not update.message or not update.effective_user:
        return
        
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return

    if not context.args:
        await update.message.reply_text(
            "Usage: `/addchannel [channel_id] [optional_name]`\n\n"
            "Example: `/addchannel @mychannel My Channel Name`",
            parse_mode='Markdown'
        )
        return

    channel_id = context.args[0]
    channel_name = ' '.join(context.args[1:]) if len(context.args) > 1 else None
    
    # Handle both @channel and -100123456789 formats
    if channel_id.startswith('@'):
        channel_id = channel_id[1:]  # Remove @
    
    try:
        if add_channel(channel_id, channel_name):
            await update.message.reply_text(
                f"✅ Channel `{channel_id}` has been added to management.",
                parse_mode='Markdown'
            )
            logger.info(f"Admin {update.effective_user.id} added channel {channel_id}")
        else:
            await update.message.reply_text(
                f"❌ Channel `{channel_id}` is already being managed.",
                parse_mode='Markdown'
            )
    
    except Exception as e:
        logger.error(f"Error adding channel: {e}")
        await update.message.reply_text("❌ An error occurred while adding the channel.")

async def remove_channel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /removechannel command"""
    if not update.message or not update.effective_user:
        return
        
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return

    if not context.args:
        await update.message.reply_text(
            "Usage: `/removechannel [channel_id]`\n\n"
            "Example: `/removechannel @mychannel`",
            parse_mode='Markdown'
        )
        return

    channel_id = context.args[0]
    
    # Handle both @channel and -100123456789 formats
    if channel_id.startswith('@'):
        channel_id = channel_id[1:]  # Remove @
    
    try:
        if remove_channel(channel_id):
            await update.message.reply_text(
                f"✅ Channel `{channel_id}` has been removed from management.",
                parse_mode='Markdown'
            )
            logger.info(f"Admin {update.effective_user.id} removed channel {channel_id}")
        else:
            await update.message.reply_text(
                f"❌ Channel `{channel_id}` is not being managed.",
                parse_mode='Markdown'
            )
    
    except Exception as e:
        logger.error(f"Error removing channel: {e}")
        await update.message.reply_text("❌ An error occurred while removing the channel.")

async def list_channels_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /listchannels command"""
    if not update.message or not update.effective_user:
        return
        
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return

    channels = load_channels()
    
    if not channels:
        await update.message.reply_text("📋 No channels are currently being managed.")
        return
    
    message = "📺 **Managed Channels**\n\n"
    
    for i, channel in enumerate(channels, 1):
        status_emoji = "🟢" if channel.get('status') == 'active' else "🔴"
        message += f"{i}. {status_emoji} `{channel['id']}`\n"
        message += f"   📝 Name: {channel.get('name', 'Not set')}\n"
        message += f"   📅 Added: {channel.get('added_date', 'Unknown')[:10]}\n\n"
    
    message += f"**Total Channels:** {len(channels)}"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def channel_stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /channelstats command"""
    if not update.message or not update.effective_user:
        return
        
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return

    channels = load_channels()
    
    if not channels:
        await update.message.reply_text("📊 No channel statistics available.")
        return
    
    active_channels = sum(1 for ch in channels if ch.get('status') == 'active')
    inactive_channels = len(channels) - active_channels
    
    message = f"""
📊 **Channel Statistics**

📺 **Total Channels:** {len(channels)}
🟢 **Active Channels:** {active_channels}
🔴 **Inactive Channels:** {inactive_channels}

**Recent Activity:**
"""
    
    # Show last 5 channels
    recent_channels = sorted(channels, key=lambda x: x.get('added_date', ''), reverse=True)[:5]
    
    for i, channel in enumerate(recent_channels, 1):
        status_emoji = "🟢" if channel.get('status') == 'active' else "🔴"
        message += f"{i}. {status_emoji} `{channel['id']}`\n"
        message += f"   📅 {channel.get('added_date', 'Unknown')[:10]}\n"
    
    if len(channels) > 5:
        message += f"\n... and {len(channels) - 5} more channels"
    
    message += f"\n\n**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    await update.message.reply_text(message, parse_mode='Markdown')
