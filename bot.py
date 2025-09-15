# main.py
import discord
from discord.ext import commands
from datetime import timedelta, timezone
import os

import config

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# importing data from config.json
GUILD_ID = config.GUILD

bot = commands.Bot(command_prefix='.', intents=intents)

moscow_tz = timezone(timedelta(hours=3))


### cogs loading
cogs_folder = 'cogs'  # cogs directory name

async def load_extensions():
    for filename in os.listdir(cogs_folder):
        if filename.endswith(".py"):  # Looking for .py files
            try:
                await bot.load_extension(f"{cogs_folder}.{filename[:-3]}")
                print(f"[{filename}] Cogs loaded successful!")
            except Exception as e:
                print(f"[{filename}] Error on cogs load: {e}")

@bot.event
async def on_ready():
    print('Login: {}'.format(bot.user))

    await load_extensions()  # Call cogs loading
    guild = discord.Object(id=GUILD_ID)


    # Clearing global slash-commands
    # Global sync then local sync only for guild
    await bot.tree.sync()  # empy sync to delete global commands
    await bot.tree.sync(guild=guild)  # local sync

    print('Timezone setup:', moscow_tz)
    print('Ready!')


async def main():
    token = config.TOKEN

    async with bot:
        await bot.start(token)



if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
