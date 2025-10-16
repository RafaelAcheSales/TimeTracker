"""Configuration module for the Discord bot."""
import os
from dotenv import load_dotenv

load_dotenv()

# Discord Bot Token
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Target role name for disconnection
TARGET_ROLE_NAME = os.getenv('TARGET_ROLE_NAME', 'TimeTracked')

# Disconnect time in UTC (HH:MM format)
DISCONNECT_TIME = os.getenv('DISCONNECT_TIME', '03:00')

# Notification channel ID
NOTIFICATION_CHANNEL_ID = os.getenv('NOTIFICATION_CHANNEL_ID')

# Target voice channels (comma-separated IDs)
TARGET_VOICE_CHANNELS = os.getenv('TARGET_VOICE_CHANNELS', '')

def get_target_channels():
    """Parse and return list of target voice channel IDs."""
    if not TARGET_VOICE_CHANNELS:
        return []
    return [int(ch_id.strip()) for ch_id in TARGET_VOICE_CHANNELS.split(',') if ch_id.strip()]

def get_disconnect_hour_minute():
    """Parse disconnect time and return (hour, minute) tuple."""
    try:
        hour, minute = DISCONNECT_TIME.split(':')
        return int(hour), int(minute)
    except (ValueError, AttributeError):
        # Default to 3:00 AM if parsing fails
        return 3, 0
