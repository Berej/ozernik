import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from discord import Embed
from config_loader import config
from utilities import Database

class KarmaDatabase:
    def __init__(self):
        self.db = Database()




class KarmaSistem(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        pass

async def setup(bot):
    await bot.add_cog(KarmaSistem(bot))