"""Discord bot for disconnecting users with specific role at scheduled time."""
import discord
from discord.ext import commands, tasks
from datetime import datetime
import config

# Set up intents
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.voice_states = True
intents.message_content = True

# Create bot instance
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    """Event handler when bot is ready."""
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guild(s)')
    
    # Start the scheduled task
    if not disconnect_scheduler.is_running():
        disconnect_scheduler.start()
        print('Scheduled task checker started')


@tasks.loop(minutes=1)
async def disconnect_scheduler():
    """Check every minute if it's time to disconnect users for any guild."""
    now = datetime.utcnow()
    current_time = f"{now.hour:02d}:{now.minute:02d}"
    
    for guild_id, task_config in config.scheduled_tasks.items():
        if task_config.get('time') == current_time:
            guild = bot.get_guild(guild_id)
            if guild:
                print(f'Disconnect time reached for guild {guild.name}: {current_time} UTC')
                await disconnect_users_in_guild(guild, task_config)


async def disconnect_users_in_guild(guild, task_config):
    """Disconnect all users with the target role from voice channels in a specific guild."""
    role_id = task_config.get('role')
    target_channels = task_config.get('channels', [])
    notification_channel_id = task_config.get('notification_channel')
    
    # Find the target role
    target_role = guild.get_role(role_id)
    
    if not target_role:
        print(f'Role ID {role_id} not found in guild: {guild.name}')
        return
    
    print(f'Processing guild: {guild.name}')
    disconnected_count = 0
    
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
    if notification_channel_id:
        await send_notification(guild, notification_channel_id, disconnected_count, target_role.name, task_config.get('time'))
    
    print(f'Guild "{guild.name}": {disconnected_count} users disconnected')


async def send_notification(guild, channel_id, disconnected_count, role_name, disconnect_time):
    """Send notification to the configured channel."""
    try:
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
            value=role_name,
            inline=True
        )
        embed.add_field(
            name="Time (UTC)",
            value=disconnect_time,
            inline=True
        )
        
        await channel.send(embed=embed)
        print(f'Notification sent to channel: {channel.name}')
    
    except discord.errors.HTTPException as e:
        print(f'Failed to send notification: {e}')


@bot.command(name='schedule')
@commands.has_permissions(administrator=True)
async def schedule_disconnect(ctx, role: discord.Role, time: str, *channels: discord.VoiceChannel):
    """
    Schedule automatic disconnection of users with a specific role.
    
    Usage: !schedule @RoleName HH:MM [#VoiceChannel1] [#VoiceChannel2] ...
    Example: !schedule @NightOwl 03:00 #General #Gaming
    
    If no channels are specified, all voice channels will be monitored.
    Time should be in UTC 24-hour format (HH:MM).
    """
    # Validate time format
    try:
        hour, minute = time.split(':')
        hour, minute = int(hour), int(minute)
        if not (0 <= hour < 24 and 0 <= minute < 60):
            raise ValueError
    except (ValueError, AttributeError):
        await ctx.send("❌ Invalid time format. Please use HH:MM format (e.g., 03:00)")
        return
    
    # Store the scheduled task
    guild_id = ctx.guild.id
    config.scheduled_tasks[guild_id] = {
        'role': role.id,
        'time': time,
        'channels': [ch.id for ch in channels] if channels else [],
        'notification_channel': ctx.channel.id
    }
    
    # Build response
    embed = discord.Embed(
        title="✅ Disconnect Schedule Created",
        color=discord.Color.green(),
        timestamp=datetime.utcnow()
    )
    embed.add_field(
        name="Target Role",
        value=role.mention,
        inline=True
    )
    embed.add_field(
        name="Disconnect Time (UTC)",
        value=time,
        inline=True
    )
    embed.add_field(
        name="Current Time (UTC)",
        value=datetime.utcnow().strftime("%H:%M:%S"),
        inline=True
    )
    
    if channels:
        channel_mentions = ", ".join([ch.mention for ch in channels])
        embed.add_field(
            name="Target Voice Channels",
            value=channel_mentions,
            inline=False
        )
    else:
        embed.add_field(
            name="Target Voice Channels",
            value="All voice channels",
            inline=False
        )
    
    embed.add_field(
        name="Notification Channel",
        value=ctx.channel.mention,
        inline=False
    )
    
    await ctx.send(embed=embed)
    print(f'Schedule created for guild {ctx.guild.name}: Role={role.name}, Time={time}')


@bot.command(name='unschedule')
@commands.has_permissions(administrator=True)
async def unschedule_disconnect(ctx):
    """
    Remove the scheduled disconnection task for this server.
    
    Usage: !unschedule
    """
    guild_id = ctx.guild.id
    
    if guild_id in config.scheduled_tasks:
        del config.scheduled_tasks[guild_id]
        await ctx.send("✅ Scheduled disconnection has been removed.")
        print(f'Schedule removed for guild {ctx.guild.name}')
    else:
        await ctx.send("❌ No scheduled disconnection found for this server.")


@bot.command(name='status')
@commands.has_permissions(administrator=True)
async def status(ctx):
    """Check bot status and current schedule configuration (Admin only)."""
    guild_id = ctx.guild.id
    
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
        name="Current Time (UTC)",
        value=datetime.utcnow().strftime("%H:%M:%S"),
        inline=True
    )
    
    if guild_id in config.scheduled_tasks:
        task_config = config.scheduled_tasks[guild_id]
        role = ctx.guild.get_role(task_config['role'])
        
        embed.add_field(
            name="Schedule Status",
            value="🟢 Active",
            inline=True
        )
        embed.add_field(
            name="Target Role",
            value=role.mention if role else "Unknown",
            inline=True
        )
        embed.add_field(
            name="Disconnect Time (UTC)",
            value=task_config['time'],
            inline=True
        )
        
        if task_config['channels']:
            channel_names = []
            for ch_id in task_config['channels']:
                channel = ctx.guild.get_channel(ch_id)
                if channel:
                    channel_names.append(channel.mention)
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
        
        notif_channel = ctx.guild.get_channel(task_config['notification_channel'])
        embed.add_field(
            name="Notification Channel",
            value=notif_channel.mention if notif_channel else "Unknown",
            inline=False
        )
    else:
        embed.add_field(
            name="Schedule Status",
            value="⚪ No active schedule",
            inline=False
        )
        embed.add_field(
            name="Info",
            value="Use `!schedule @Role HH:MM` to create a schedule",
            inline=False
        )
    
    await ctx.send(embed=embed)


@bot.command(name='testdisconnect')
@commands.has_permissions(administrator=True)
async def test_disconnect(ctx):
    """Manually trigger disconnection using current schedule (Admin only)."""
    guild_id = ctx.guild.id
    
    if guild_id not in config.scheduled_tasks:
        await ctx.send("❌ No scheduled disconnection found. Use `!schedule` first.")
        return
    
    await ctx.send("⏳ Initiating manual disconnection...")
    task_config = config.scheduled_tasks[guild_id]
    await disconnect_users_in_guild(ctx.guild, task_config)
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
