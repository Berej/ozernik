import asyncio
import discord
from discord.ext import commands

import config

class VoiceManager(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # Check if the member joined a voice channel
        if before.channel is None and after.channel is not None:
            print(f'{member.display_name} has joined voice channel: {after.channel.name}')
            # You can add further actions here, like sending a message or playing a sound
            # Example: await after.channel.send(f"Welcome, {member.display_name}!")
        
        # Optional: Check if the member left a voice channel
        elif before.channel is not None and after.channel is None:
            print(f'{member.display_name} has left voice channel: {before.channel.name}')

        elif before.channel is not None and after.channel is not None and before.channel != after.channel:
            print(f'{member.display_name} moved from {before.channel.name} to {after.channel.name}')
            # channel = bot.get_channel(YOUR_TEXT_CHANNEL_ID)
            # await channel.send(f'{member.display_name} moved from {before.channel.name} to {after.channel.name}')


async def setup(bot):
    await bot.add_cog(VoiceManager(bot))
