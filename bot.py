import discord
from discord.ext import commands
from datetime import timedelta, timezone
import os


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

TESTSERVER_ID = 1324396791965417513
OZERNIK_ID = 722824269683359877
GUILD_ID = 0 # initialization


# Don't forget to change DEBUG_MODE while working, dear developers :)
DEBUG_MODE = True

if DEBUG_MODE:
    GUILD_ID = TESTSERVER_ID 
else:
    GUILD_ID = OZERNIK_ID


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
    await bot.tree.sync()  # пустой sync — это глобальная синхронизация
    await bot.tree.sync(guild=guild)  # локальная синхронизация


    print('Установлен часовой пояс:', moscow_tz)
    print('Всё готово!')


async def main():
    # Loading token from files
    try:
        with open("token.txt", "r") as token_file:
            token = token_file.read().strip()  # reading token and clearing from spaces
    except FileNotFoundError:
        print("Файл token.txt не найден. Убедитесь, что он существует и содержит токен.")
        return
    except Exception as e:
        print(f"Ошибка при чтении файла с токеном: {e}")
        return

    async with bot:
        await bot.start(token)



if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
