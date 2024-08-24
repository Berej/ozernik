import discord
import os
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=".", intents=intents)

load_dotenv(".env")
TOKEN: str = os.getenv("TOKEN")

@bot.event #Синхронизация команд
async def on_ready():
    print(f'Login: {bot.user}')

    guild = discord.Object(id='722824269683359877')
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild) 

async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
            print(f"Loaded: {filename}")

async def main():
    await load()
    await bot.start(TOKEN)

if __name__ == "__main__":
    # Check if there is an existing event loop
    if not asyncio.get_event_loop().is_running():
        asyncio.run(main())
    else:
        # Use a different way to start the bot if an event loop is already running
        loop = asyncio.get_event_loop()
        loop.create_task(main())
        loop.run_forever()
