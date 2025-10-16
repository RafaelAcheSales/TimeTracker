# TimeTracker Discord Bot

A Discord bot that automatically disconnects users with a specific role from voice channels at a scheduled time. Configure everything through simple Discord commands - no need to edit configuration files!

## Features

- 🕐 **Scheduled Disconnection**: Set a specific time (UTC) to automatically disconnect users
- 🎭 **Role-Based Targeting**: Target users by their Discord role
- 📢 **Notifications**: Automatic notification when disconnection occurs
- 🎯 **Channel Filtering**: Optionally target specific voice channels or all channels
- ⚙️ **Command-Based Setup**: Configure everything through Discord chat commands
- 🔧 **Per-Server Configuration**: Each Discord server has its own independent schedule

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
   
   Edit `.env` and set your bot token:
   ```env
   DISCORD_TOKEN=your_bot_token_here
   ```

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
   - Message Content Intent
6. Go to "OAuth2" → "URL Generator"
7. Select scopes: `bot`
8. Select bot permissions:
   - Move Members
   - View Channels
   - Send Messages
   - Embed Links
9. Use the generated URL to invite the bot to your server

## Usage

### Setting Up a Schedule

Use the `!schedule` command to create a scheduled disconnection task:

```
!schedule @RoleName HH:MM [#VoiceChannel1] [#VoiceChannel2] ...
```

**Examples:**

1. **Disconnect all users with "NightOwl" role at 3 AM from all voice channels:**
   ```
   !schedule @NightOwl 03:00
   ```

2. **Disconnect users only from specific voice channels:**
   ```
   !schedule @NightOwl 03:00 #General #Gaming
   ```

3. **Different time format:**
   ```
   !schedule @Student 22:30 #Study Room
   ```

**Notes:**
- Time must be in UTC 24-hour format (HH:MM)
- If no voice channels are specified, all voice channels are monitored
- Notifications will be sent to the channel where the command was used
- Only administrators can use this command

### Checking Current Schedule

Use `!status` to view the current configuration:

```
!status
```

This shows:
- Current schedule status (active or not)
- Target role
- Disconnect time (UTC)
- Target voice channels
- Notification channel
- Current UTC time

### Removing a Schedule

Use `!unschedule` to remove the scheduled task:

```
!unschedule
```

### Testing the Schedule

Use `!testdisconnect` to manually trigger a disconnection using the current schedule:

```
!testdisconnect
```

This is useful for testing your configuration before waiting for the scheduled time.

## Commands Reference

| Command | Description | Example |
|---------|-------------|---------|
| `!schedule @Role HH:MM [#Channels...]` | Create a scheduled disconnection task | `!schedule @NightOwl 03:00` |
| `!unschedule` | Remove the current schedule | `!unschedule` |
| `!status` | View current schedule configuration | `!status` |
| `!testdisconnect` | Manually trigger disconnection | `!testdisconnect` |

All commands require **Administrator** permission.

## How It Works

1. Administrator uses `!schedule` command to configure the disconnection task
2. The bot stores the configuration (role, time, channels) for that Discord server
3. Every minute, the bot checks if the current UTC time matches any scheduled time
4. When a match is found:
   - The bot finds all users with the specified role in the target voice channels
   - Disconnects them from the voice channels
   - Sends a notification embed to the configured channel

## Example Scenario

**Gaming Server - Enforce 3 AM Shutdown**

1. Admin runs command:
   ```
   !schedule @Gamer 03:00
   ```

2. Bot confirms with an embed showing the configuration

3. At 3:00 AM UTC every day:
   - All users with the "Gamer" role are disconnected from voice channels
   - A notification embed is posted in the channel where the schedule was created

## Troubleshooting

### Bot doesn't respond to commands
- Verify the bot has "Message Content Intent" enabled in Discord Developer Portal
- Check that the bot has permission to read messages in the channel
- Ensure you're using the correct command prefix (`!`)

### Users not disconnecting
- Verify the role name matches exactly (case-sensitive)
- Check that the bot has "Move Members" permission
- Ensure the bot's role is higher than the target role in the role hierarchy
- Verify the time is in UTC (not your local timezone)

### Notifications not sending
- The notification is sent to the channel where `!schedule` was used
- Ensure the bot has permission to send messages and embed links in that channel

### Schedule not working
- Use `!status` to verify the schedule is active
- Check that the time is in correct format (HH:MM)
- Remember: time must be in UTC

## Converting Time Zones to UTC

The bot uses UTC time. Convert your local time:

- **PST (UTC-8)**: 11:00 PM PST = 07:00 UTC (next day)
- **EST (UTC-5)**: 10:00 PM EST = 03:00 UTC (next day)
- **CET (UTC+1)**: 4:00 AM CET = 03:00 UTC
- **JST (UTC+9)**: 12:00 PM JST = 03:00 UTC

Use online time zone converters to help!

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.
