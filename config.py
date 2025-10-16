"""Configuration module for the Discord bot."""
import os
from dotenv import load_dotenv

load_dotenv()

# Discord Bot Token
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Store scheduled tasks per guild
# Format: {guild_id: {'role': role_id, 'time': 'HH:MM', 'channels': [channel_ids], 'notification_channel': channel_id}}
scheduled_tasks = {}
