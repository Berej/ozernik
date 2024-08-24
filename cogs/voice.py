import discord
from discord.ext import commands
from discord.ext import tasks


# Список ID каналов, названия которых изменять нельзя
protected_channels = [1150378018771050537, #Создать [+]
                       1086264864474923038, #Трибуна
                       1265210153867677818, #RLU
                       1181442425881894972, #afk
                       ]

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def test(self, ctx):
        await ctx.send("test")


    @commands.hybrid_command(name="rename", description="Меняет название голосового канала")
    async def rename(self, interaction: discord.Interaction, voice: str):
        # Получаем пользователя, который вызвал команду
        user = interaction.user

        # Проверяем, есть ли у пользователя нужная роль
        role = discord.utils.get(user.roles, id=1102221898793881710)
        if role is None:
            await interaction.response.send_message("Вы не Озёрник", ephemeral=True)
            return

        # Проверяем, находится ли пользователь в голосовом канале
        if user.voice is None or user.voice.channel is None:
            await interaction.response.send_message("Вы не находитесь в голосовом канале.", ephemeral=True)
            return

        voice_channel = user.voice.channel

        # Проверяем, не является ли канал защищённым
        if voice_channel.id in protected_channels:
            await interaction.response.send_message("Название этого канала нельзя изменить.", ephemeral=True)
            return

        # Изменяем название канала
        await voice_channel.edit(name=voice)
        
        await interaction.response.send_message(f"Название канала изменено на {voice}")




    #Send message in new voice channel to announce about /rename command
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        if isinstance(channel, discord.VoiceChannel):
            # Печатает сообщение в консоль
            print(f"Голосовой канал '{channel.name}' был создан в сервере '{channel.guild.name}'.")
            await channel.send("Чтобы изменить название голосового канала используйте /rename")



async def setup(bot):
    await bot.add_cog(Voice(bot))
