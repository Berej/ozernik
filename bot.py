# main.py
import discord
from discord.ext import commands
from datetime import timedelta, timezone
import os
from colorama import Fore, Style, init
init()

from config_loader import config

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# importing data from config.json
GUILD_ID = config.GUILD

bot = commands.Bot(command_prefix='.', intents=intents)

moscow_tz = timezone(timedelta(hours=3))

### modules loading
modules_folder = 'modules'  # modules directory name

async def load_extensions():
    i = 1

    for folder in os.listdir(modules_folder):
        folder_path = os.path.join(modules_folder, folder)

        if not os.path.isdir(folder_path):
            continue
        if folder.startswith("_"):
            continue

        for filename in os.listdir(folder_path):
            if not filename.endswith(".py"):
                continue
            if filename.startswith("_"):
                continue

            module_path = f"{modules_folder}.{folder}.{filename[:-3]}"

            try:
                await bot.load_extension(module_path)
                print(
                    Fore.GREEN
                    + f"{i}. [{module_path}] Cog loaded successfully!"
                    + Style.RESET_ALL
                )
            except Exception as e:
                print(
                    Fore.RED
                    + f"{i}. [{module_path}] Error loading cog: {e}"
                    + Style.RESET_ALL
                )

            i += 1

@bot.event
async def on_ready():
    print('Login: {}'.format(bot.user))

    await load_extensions()  # Call modules loading
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
