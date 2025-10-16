"""Discord bot for disconnecting users with specific role at scheduled time."""
import discord
from discord.ext import commands, tasks
from datetime import datetime, time
import config

# Set up intents
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.voice_states = True

# Create bot instance
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    """Event handler when bot is ready."""
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guild(s)')
    
    # Start the scheduled task
    disconnect_scheduler.start()
    print(f'Scheduled task started. Will disconnect users at {config.DISCONNECT_TIME} UTC')


@tasks.loop(minutes=1)
async def disconnect_scheduler():
    """Check every minute if it's time to disconnect users."""
    now = datetime.utcnow()
    target_hour, target_minute = config.get_disconnect_hour_minute()
    
    # Check if current time matches the disconnect time
    if now.hour == target_hour and now.minute == target_minute:
        print(f'Disconnect time reached: {now.strftime("%Y-%m-%d %H:%M:%S")} UTC')
        await disconnect_users_with_role()


async def disconnect_users_with_role():
    """Disconnect all users with the target role from voice channels."""
    disconnected_count = 0
    target_channels = config.get_target_channels()
    
    for guild in bot.guilds:
        # Find the target role
        target_role = discord.utils.get(guild.roles, name=config.TARGET_ROLE_NAME)
        
        if not target_role:
            print(f'Role "{config.TARGET_ROLE_NAME}" not found in guild: {guild.name}')
            continue
        
        print(f'Processing guild: {guild.name}')
        
        # Iterate through voice channels
        for voice_channel in guild.voice_channels:
            # Skip if specific channels are configured and this isn't one of them
            if target_channels and voice_channel.id not in target_channels:
                continue
            
            # Check each member in the voice channel
            for member in voice_channel.members:
                if target_role in member.roles:
                    try:
                        await member.move_to(None)  # Disconnect user
                        disconnected_count += 1
                        print(f'Disconnected {member.display_name} from {voice_channel.name}')
                    except discord.errors.HTTPException as e:
                        print(f'Failed to disconnect {member.display_name}: {e}')
        
        # Send notification if configured
        if config.NOTIFICATION_CHANNEL_ID:
            await send_notification(guild, disconnected_count)
    
    print(f'Total users disconnected: {disconnected_count}')


async def send_notification(guild, disconnected_count):
    """Send notification to the configured channel."""
    try:
        channel_id = int(config.NOTIFICATION_CHANNEL_ID)
        channel = guild.get_channel(channel_id)
        
        if not channel:
            print(f'Notification channel not found: {channel_id}')
            return
        
        # Create embed message
        embed = discord.Embed(
            title="🕐 Time Tracker - Disconnect Notice",
            description=f"Scheduled disconnection has been executed.",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(
            name="Users Disconnected",
            value=str(disconnected_count),
            inline=True
        )
        embed.add_field(
            name="Target Role",
            value=config.TARGET_ROLE_NAME,
            inline=True
        )
        embed.add_field(
            name="Time (UTC)",
            value=config.DISCONNECT_TIME,
            inline=True
        )
        
        await channel.send(embed=embed)
        print(f'Notification sent to channel: {channel.name}')
    
    except ValueError:
        print(f'Invalid notification channel ID: {config.NOTIFICATION_CHANNEL_ID}')
    except discord.errors.HTTPException as e:
        print(f'Failed to send notification: {e}')


@bot.command(name='status')
@commands.has_permissions(administrator=True)
async def status(ctx):
    """Check bot status and configuration (Admin only)."""
    target_hour, target_minute = config.get_disconnect_hour_minute()
    target_channels = config.get_target_channels()
    
    embed = discord.Embed(
        title="⚙️ Time Tracker Bot Status",
        color=discord.Color.green()
    )
    embed.add_field(
        name="Status",
        value="✅ Online and Running",
        inline=False
    )
    embed.add_field(
        name="Target Role",
        value=config.TARGET_ROLE_NAME,
        inline=True
    )
    embed.add_field(
        name="Disconnect Time (UTC)",
        value=f"{target_hour:02d}:{target_minute:02d}",
        inline=True
    )
    embed.add_field(
        name="Current Time (UTC)",
        value=datetime.utcnow().strftime("%H:%M:%S"),
        inline=True
    )
    
    if target_channels:
        channel_names = []
        for ch_id in target_channels:
            channel = ctx.guild.get_channel(ch_id)
            if channel:
                channel_names.append(channel.name)
        embed.add_field(
            name="Target Voice Channels",
            value=", ".join(channel_names) if channel_names else "Not found",
            inline=False
        )
    else:
        embed.add_field(
            name="Target Voice Channels",
            value="All voice channels",
            inline=False
        )
    
    await ctx.send(embed=embed)


@bot.command(name='testdisconnect')
@commands.has_permissions(administrator=True)
async def test_disconnect(ctx):
    """Manually trigger disconnection (Admin only)."""
    await ctx.send("⏳ Initiating manual disconnection...")
    await disconnect_users_with_role()
    await ctx.send("✅ Manual disconnection completed!")


def main():
    """Main function to run the bot."""
    if not config.DISCORD_TOKEN:
        print("ERROR: DISCORD_TOKEN not found in environment variables!")
        print("Please create a .env file with your bot token.")
        return
    
    try:
        bot.run(config.DISCORD_TOKEN)
    except discord.errors.LoginFailure:
        print("ERROR: Invalid Discord token!")
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {e}")


if __name__ == '__main__':
    main()
