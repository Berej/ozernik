from discord.ext import commands
import random

class echo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.user in message.mentions:
            echo = ''
            messages = [message for message in [message.content async for message in self.bot.get_channel(722824270207516796).history(limit=500) if message.author.bot == False] if (2 <= len(message) <= 50) and (not any(c in '<>' for c in message))]
            for _ in range(random.randint(1, 5)):
                phrase = random.choice(messages)
                if phrase and not phrase[0].isupper():
                    echo += phrase[0].upper() + phrase[1:]
                else:
                    echo += phrase
                if phrase.endswith(('.', '!', '?')) == True:
                    echo += ' '
                elif phrase.endswith((')', '(')) == True:
                    break
                else:
                    echo += '. '
            print(echo)
            await message.reply(echo)


async def setup(bot):
    await bot.add_cog(echo(bot))