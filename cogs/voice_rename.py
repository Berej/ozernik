import discord
from discord.ext import commands
from discord import app_commands

# ID list of channels, which users can't rename
protected_channels = [1150378018771050537, #Создать [+]
                        1086264864474923038, #Трибуна
                        1265210153867677818, #RLU
                        1181442425881894972, #afk
                        ]

ALLOWED_ROLES = [1102221898793881710, 1283467964884189286]  # list of allowed roles (IDs)

class voice_rename_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #Send message in new voice channel to announce about /rename command
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        """Обработчик события создания канала на сервере"""
        if isinstance(channel, discord.VoiceChannel):
            print('Голосовой канал "{channel}" был создан в сервере "{guild}".'.format(channel = channel.name, guild = channel.guild.name))
            await channel.send("Чтобы изменить название голосового канала используйте /rename")

    @app_commands.command(name='rename', description='Меняет название голосового канала')
    @app_commands.rename(new_name = 'название')
    @app_commands.describe(new_name = 'Новое название канала')
    async def rename_voice(self, interaction: discord.Interaction, new_name: str):
        # Get user (command call owner)
        user = interaction.user

        # Check if user have ALLOWED_ROLES
        if not any(discord.utils.get(user.roles, id=role_id) for role_id in ALLOWED_ROLES):
            await interaction.response.send_message("Вы не имеете нужной роли.", ephemeral=True)
            return

        # Check if user is in voice
        if user.voice is None or user.voice.channel is None:
            await interaction.response.send_message("Вы не находитесь в голосовом канале.", ephemeral=True)
            return

        voice_channel = user.voice.channel

        # Check if user is in protected_channels
        if voice_channel.id in protected_channels:
            await interaction.response.send_message("Название этого канала нельзя изменить.", ephemeral=True)
            return

        # Rename voice
        await voice_channel.edit(name=new_name)
        await interaction.response.send_message('{user} меняет название канала на **{new_name}**'.format(user = interaction.user.display_name, new_name = new_name))

async def setup(bot):
    await bot.add_cog(voice_rename_cog(bot))