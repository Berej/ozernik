import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from discord import Embed
from config_loader import config

class KarmaSistem(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

async def setup(bot):
    await bot.add_cog(KarmaSistem(bot))