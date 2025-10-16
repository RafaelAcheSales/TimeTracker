# TimeTracker Discord Bot

A Discord bot that automatically disconnects users with a specific role from voice channels at a scheduled time. Perfect for managing voice channel usage during off-hours or enforcing time-based access policies.

## Features

- 🕐 **Scheduled Disconnection**: Automatically disconnect users at a configured time (e.g., 3 AM UTC)
- 🎭 **Role-Based Targeting**: Only disconnects users with a specific role
- 📢 **Notifications**: Sends an embed notification when disconnection occurs
- 🎯 **Channel Filtering**: Optionally target specific voice channels
- ⚙️ **Admin Commands**: Check status and manually trigger disconnections
- 🔧 **Easy Configuration**: Environment variables for all settings

## Requirements

- Python 3.8 or higher
- Discord Bot Token (from [Discord Developer Portal](https://discord.com/developers/applications))
- Required Python packages (see `requirements.txt`)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/RafaelAcheSales/TimeTracker.git
   cd TimeTracker
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the bot**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and set your configuration:
   - `DISCORD_TOKEN`: Your bot token from Discord Developer Portal
   - `TARGET_ROLE_NAME`: Name of the role to target (default: "TimeTracked")
   - `DISCONNECT_TIME`: Time in UTC 24-hour format (default: "03:00")
   - `NOTIFICATION_CHANNEL_ID`: (Optional) Channel ID for notifications
   - `TARGET_VOICE_CHANNELS`: (Optional) Comma-separated voice channel IDs

4. **Run the bot**
   ```bash
   python bot.py
   ```

## Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the "Bot" section and create a bot
4. Copy the bot token and add it to your `.env` file
5. Enable the following **Privileged Gateway Intents**:
   - Server Members Intent
   - Presence Intent (optional)
6. Go to "OAuth2" → "URL Generator"
7. Select scopes: `bot`
8. Select bot permissions:
   - Move Members
   - View Channels
   - Send Messages
   - Embed Links
9. Use the generated URL to invite the bot to your server

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DISCORD_TOKEN` | Your Discord bot token | - | ✅ Yes |
| `TARGET_ROLE_NAME` | Role name to target for disconnection | TimeTracked | ❌ No |
| `DISCONNECT_TIME` | Time in UTC (HH:MM format) | 03:00 | ❌ No |
| `NOTIFICATION_CHANNEL_ID` | Channel ID for notifications | - | ❌ No |
| `TARGET_VOICE_CHANNELS` | Comma-separated voice channel IDs | All channels | ❌ No |

### Example Configuration

```env
DISCORD_TOKEN=your_actual_bot_token_here
TARGET_ROLE_NAME=NightOwl
DISCONNECT_TIME=02:30
NOTIFICATION_CHANNEL_ID=1234567890123456789
TARGET_VOICE_CHANNELS=1111111111111111111,2222222222222222222
```

## Commands

### `!status`
*Requires Administrator permission*

Displays the current bot status and configuration.

```
!status
```

### `!testdisconnect`
*Requires Administrator permission*

Manually triggers a disconnection event for testing purposes.

```
!testdisconnect
```

## How It Works

1. The bot connects to Discord and starts a scheduled task
2. Every minute, it checks if the current UTC time matches the configured `DISCONNECT_TIME`
3. When the time matches:
   - The bot searches for all users with the `TARGET_ROLE_NAME` in voice channels
   - If `TARGET_VOICE_CHANNELS` is configured, only those channels are checked
   - All matching users are disconnected from voice channels
   - A notification is sent to the configured notification channel (if set)

## Example Use Cases

- **Gaming Community**: Disconnect users at 3 AM to enforce server downtime
- **Study Group**: Automatically end study sessions at a specific time
- **Corporate Server**: Enforce off-hours policies for voice channels
- **Event Management**: Clear voice channels after scheduled events

## Troubleshooting

### Bot doesn't connect
- Verify your `DISCORD_TOKEN` is correct
- Check that the bot is invited to your server
- Ensure you have enabled required intents in Discord Developer Portal

### Users not disconnecting
- Verify the role name matches exactly (case-sensitive)
- Check that the bot has "Move Members" permission
- Ensure the bot's role is higher than the target role in the role hierarchy
- Verify the disconnect time is in UTC (not your local timezone)

### Notifications not sending
- Check that `NOTIFICATION_CHANNEL_ID` is correct
- Ensure the bot has permission to send messages in that channel
- Verify the bot has "Embed Links" permission

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.
