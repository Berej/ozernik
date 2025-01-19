from discord.ext import commands
import random
import re

class echo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.user in message.mentions:
            async with message.channel.typing():
                echo = ''
                messages = [message for message in [message.content async for message in self.bot.get_channel(722824270207516796).history(limit=1000) if message.author.bot == False] if (2 <= len(message) <= 50)]
                sentence = int(random.randint(1, 8))
                if 1 < sentence <= 5:
                    url_pattern = r"http[s]?://\S+"
                    messages = [msg for msg in messages if (not re.search(url_pattern, msg)) and (not any(c in '<>' for c in msg))]
                    for i in range(sentence):
                        phrase = random.choice(messages)
                        messages.remove(phrase)
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
                elif sentence == 1:
                    echo = random.choice(['https://tenor.com/view/nuke-press-the-button-bomb-them-nuke-them-cat-gif-16361990', 'https://tenor.com/view/crunchy-luna-cat-crunch-cat-blinking-close-up-gif-26931104', 'https://tenor.com/view/cat-beach-slice-watermelon-gif-7944445'])
                else:
                    messages = [item for item in messages if not (item.startswith("<:") and item.endswith(">") and item not in map(str, message.guild.emojis)) and not re.compile(r"<@!?(\d+)>").search(item)]
                    echo = random.choice(messages)
            await message.reply(echo)


async def setup(bot):
    await bot.add_cog(echo(bot))