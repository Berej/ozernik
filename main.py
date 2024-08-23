import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv(".env")
TOKEN: str = os.getenv("TOKEN")

