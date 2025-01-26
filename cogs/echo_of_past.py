from discord.ext import commands
import random
import re

echo_channel_list = [
    722824270207516796, #основной
    777816563738738699, #озёрники
    785123760206118933, #спам
    727527717125226526, #оффтоп
    1189392913092853831 #боты - канал на тестовом сервере
]

def choice_phrase(messages):
    phrase = random.choice(messages)
    messages.remove(phrase)
    if phrase and not phrase[0].isupper():
        phrase = phrase[0].upper() + phrase[1:]
    else:
        phrase = phrase
    return phrase

class echo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if (self.bot.user in message.mentions) and (message.channel.id in echo_channel_list):
            async with message.channel.typing():
                echo = ''
                messages = [message for message in [message.content async for message in self.bot.get_channel(722824270207516796).history(limit=1000) if message.author.bot == False] if (2 <= len(message) <= 50)]
                sentence = int(random.randint(1, 20))
                if sentence == 1:
                    echo = random.choice([
                    'https://tenor.com/view/sleepy-kitty-sleepy-cat-sleepy-sad-sad-cat-gif-13665137351453051889',
                    'https://tenor.com/view/sad-crying-kitty-sad-crying-kitten-sad-kitty-sad-kitten-crying-kitty-gif-14257501369475522884',
                    'https://tenor.com/view/crunchy-luna-cat-crunch-cat-blinking-close-up-gif-26931104',
                    'https://tenor.com/view/cat-beach-slice-watermelon-gif-7944445',
                    'https://tenor.com/view/uni-cat-bowtie-cute-hi-gif-500744924715907421',
                    'https://tenor.com/view/nuke-press-the-button-bomb-them-nuke-them-cat-gif-16361990',
                    'https://tenor.com/view/yourarchivist-black-cat-orange-cat-black-cat-and-orange-cat-cat-cuddle-gif-11630674910872813960',
                    'https://tenor.com/view/cat-ears-cat-eyes-cat-hiding-hiding-cat-gif-8389763803474549606',
                    'https://tenor.com/view/brown-cat-kitten-kitty-cute-gif-2303282369115442960',
                    'https://tenor.com/view/cat-cute-exercise-bed-kitty-gif-17932354043745241231',
                    'https://tenor.com/view/youtube-yt-cat-kitten-kitty-gif-3729377368206038814',
                    'https://tenor.com/view/little-kitty-kitten-looking-a-phone-wth-huh-confused-gif-9511786994202518313',
                    'https://tenor.com/view/cat-black-cat-cute-meow-cute-cat-gif-9183068753430650279',
                    'https://tenor.com/view/meow-kitty-happy-cat-kitty-cat-gif-4532088786446233986',
                    'https://tenor.com/view/sleepy-cat-cute-kitty-sleepy-kitten-sleepy-kitty-sleepytime-gif-15922126068799997734'])
                elif 1 < sentence <= 6:
                    url_pattern = r"http[s]?://\S+"
                    messages = [msg for msg in messages if (not re.search(url_pattern, msg)) and (not any(c in '<>' for c in msg))]
                    for i in range((sentence)-1):
                        phrase = choice_phrase(messages)
                        echo += phrase
                        if phrase.endswith(('.', '!', '?')) == True:
                            echo += ' '
                        elif phrase.endswith((')', '(')) == True:
                            break
                        else:
                            echo += '. '
                    echo += choice_phrase(messages)
                else:
                    messages = [item for item in messages if not (item.startswith("<:") and item.endswith(">") and item not in map(str, message.guild.emojis)) and not re.compile(r"<@!?(\d+)>").search(item)]
                    echo = choice_phrase(messages)
            await message.reply(echo, mention_author=False)


async def setup(bot):
    await bot.add_cog(echo(bot))
