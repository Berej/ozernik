# main.py
import discord
from discord.ext import commands
from datetime import timedelta, timezone
import os

import botconfig  # наш новый конфиг

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Используем GUILD из config (целое число)
GUILD_ID = botconfig.GUILD

bot = commands.Bot(command_prefix='.', intents=intents)

moscow_tz = timezone(timedelta(hours=3))


### cogs loading
cogs_folder = 'cogs'  # cogs directory name

async def load_extensions():
    for filename in os.listdir(cogs_folder):
        if filename.endswith(".py"):  # searching .py files
            try:
                await bot.load_extension(f"{cogs_folder}.{filename[:-3]}")
                print(f"[{filename}] Загружен успешно!")
            except Exception as e:
                print(f"[{filename}] Ошибка при загрузке: {e}")

@bot.event
async def on_ready():
    print('Login: {}'.format(bot.user))

    await load_extensions()  # Call cogs loading
    guild = discord.Object(id=GUILD_ID)

    # Чистим глобальные команды (если вдруг остались от прошлого запуска)
    # Сначала глобальная синхронизация, затем локальная — как у тебя было
    await bot.tree.sync()  # пустой sync — это глобальная синхронизация
    await bot.tree.sync(guild=guild)  # локальная синхронизация

    print('Установлен часовой пояс:', moscow_tz)
    print('Всё готово!')


async def main():
    token = botconfig.TOKEN

    async with bot:
        await bot.start(token)



if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
