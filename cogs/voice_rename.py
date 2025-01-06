import discord
from discord.ext import commands
from discord import app_commands

protected_channels = [1150378018771050537, #Создать [+]
                        1086264864474923038, #Трибуна
                        1265210153867677818, #RLU
                        1181442425881894972, #afk
                        ]

ALLOWED_ROLES = [1102221898793881710, 1283467964884189286]  # List of allowed role IDs

class voice_rename_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Send a message in a new voice channel to announce the /rename command
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        """Event handler for channel creation on the server"""
        if isinstance(channel, discord.VoiceChannel):
            # Print a message to the console
            print('Voice channel "{channel}" was created in server "{guild}".'.format(channel=channel.name, guild=channel.guild.name))
            await channel.send("To change the name of the voice channel, use /rename")

    @app_commands.command(name='rename', description='Changes the name of a voice channel')
    @app_commands.rename(new_name='name')
    @app_commands.describe(new_name='New channel name')
    async def rename_voice(self, interaction: discord.Interaction, new_name: str):
        # Get the user who invoked the command
        user = interaction.user

        # Check if the user has one of the required roles
        if not any(discord.utils.get(user.roles, id=role_id) for role_id in ALLOWED_ROLES):
            await interaction.response.send_message("You don't have the required role.", ephemeral=True)
            return

        # Check if the user is in a voice channel
        if user.voice is None or user.voice.channel is None:
            await interaction.response.send_message("You are not in a voice channel.", ephemeral=True)
            return

        voice_channel = user.voice.channel

        # Check if the channel is protected
        if voice_channel.id in protected_channels:
            await interaction.response.send_message("The name of this channel cannot be changed.", ephemeral=True)
            return

        # Change the channel name
        await voice_channel.edit(name=new_name)
        await interaction.response.send_message('{user} changes the channel name to **{new_name}**'.format(user=interaction.user.display_name, new_name=new_name))

async def setup(bot):
    await bot.add_cog(voice_rename_cog(bot))
