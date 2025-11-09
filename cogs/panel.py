import asyncio
import discord
from discord import app_commands, Interaction
from discord.ext import commands
from discord import Embed
from config_loader import config

LOG_CHANNEL = config.LOG_CHANNEL_ID

ALLOWED_ROLES = [725675581881974794, 1398937618527293510]

class panel(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        Listen for the exact text ".bot_shutdown" in the main guild.
        If author is a guild member with one of ALLOWED_ROLES, acknowledge and shut the bot down.
        This is an emergency immediate shutdown — the bot will attempt to send a confirmation
        message and then call bot.close().
        """
        # ignore bots (including self)
        if message.author.bot:
            return

        # only react to the exact command (case-insensitive), trim whitespace
        if message.content.strip().lower() != ".bot_shutdown":
            return

        # require this to happen in the configured guild
        if message.guild is None or message.guild.id != config.GUILD:
            return

        # ensure author is a guild Member (has roles)
        if not isinstance(message.author, discord.Member):
            return

        # role check: user must have at least one allowed role
        if not any(role.id in ALLOWED_ROLES for role in message.author.roles):
            # polite refusal; auto-delete to avoid clutter
            try:
                await message.channel.send("You do not have permission to shut down the bot.", delete_after=8)
            except Exception:
                pass
            return

        # Acknowledge and shutdown (give a short delay to allow the message to be delivered)
        try:
            await message.channel.send(f"Shutdown command received from {message.author.mention}. Shutting down...", delete_after=5)
        except Exception:
            # If we can't send in-channel, try DM to the author as a last resort (best-effort)
            try:
                await message.author.send("Shutdown command received. Bot is shutting down.")
            except Exception:
                pass

        # small delay so Discord has time to deliver the confirmation message
        await asyncio.sleep(0.5)

        # Log and close the bot cleanly
        print(f"Shutdown initiated by {message.author} (id={message.author.id})")
        try:
            await self.bot.close()
        except Exception as e:
            # if close fails for some reason, log and force-exit the process
            print("Error while closing bot:", repr(e))
            try:
                # best-effort: stop the loop
                loop = asyncio.get_running_loop()
                loop.stop()
            except Exception:
                pass


    # --------- BOT TEXT MODERATION COMMANDS --------- 
    # Here are slash-commands to send and modify bot's messages



    # Send message with bot
    @app_commands.command(
        name='send_message',
        description='Отправить сообщение от имени Бота'
    )
    @app_commands.describe(channel='Канал отправки', content="Содержимое сообщения.")
    @app_commands.guilds(config.GUILD)
    async def send_message(self, interaction: Interaction, channel: discord.TextChannel, content: str):
        try:
                if not any(role.id in ALLOWED_ROLES for role in interaction.user.roles):
                    await interaction.response.send_message("Только для Администрации.", ephemeral=True)
                    return

                formatted_content = content.replace("\\n", "\n")
                if '\\n' in content:
                    log_content = content.replace("\\n", "\n\\n")
                else:
                    log_content = content.replace("\n", "\n\\n")


                # Sending message
                sent_message = await channel.send(formatted_content)

                # Get or create webhook for logs
                log_channel = interaction.guild.get_channel(LOG_CHANNEL)
                webhooks = await log_channel.webhooks()
                if webhooks:
                    webhook = webhooks[0]
                else:
                    webhook = await log_channel.create_webhook(name="Лилия, следящая за информацией")


                # Creating Embed
                embed = Embed(
                    title=f"Отправлено сообщение в #{channel.name}",
                    url=f"https://discord.com/channels/{interaction.guild.id}/{channel.id}/{sent_message.id}",
                    description=f"{formatted_content}",
                    color=0x3498db
                )
                embed.set_author(
                    name=interaction.user.name,
                    icon_url=interaction.user.display_avatar.url
                )
                embed.set_footer(text=f"{sent_message.id}")

                embed.add_field(name="Формат:", value=f'{log_content}', inline=False)

                # Send log with webhook
                await webhook.send(embed=embed)

                await interaction.response.send_message("Сообщение отправлено.", ephemeral=True)
        except Exception as e:
            print(f"Error send_message: {e}")
            await interaction.response.send_message("Произошла ошибка при отправке сообщения.", ephemeral=True)


    # Edit bot's message
    @app_commands.command(
        name='edit_message',
        description='Редактировать сообщение Бота.'
    )
    @app_commands.describe(
        channel="Канал сообщения.",
        message_id="ID сообщения.",
        content="Новое содержимое сообщения."
    )
    @app_commands.guilds(config.GUILD)
    async def edit_message(self, interaction: Interaction, channel: discord.TextChannel, message_id: str, content: str):
        try:
                # Проверка ролей
                if not any(role.id in ALLOWED_ROLES for role in interaction.user.roles):
                    await interaction.response.send_message("Только для Администрации.", ephemeral=True)
                    return

                # Проверка канала
                if not channel:
                    await interaction.response.send_message("Канал не найден.", ephemeral=True)
                    return

                # Получаем сообщение
                try:
                    message = await channel.fetch_message(int(message_id))
                except Exception as e:
                    await interaction.response.send_message(f"Сообщение не найдено: {e}", ephemeral=True)
                    return

                old_content = message.content or "*Пустое сообщение*"

                # Форматирование текста
                formatted_content = content.replace("\\n", "\n")
                if '\\n' in content:
                    log_content = content.replace("\\n", "\n\\n")
                else:
                    log_content = content.replace("\n", "\n\\n")

                log_old_content = message.content.replace("\n", "\n\\n")


                # Редактирование
                await message.edit(content=formatted_content)

                # Получаем или создаем вебхук для логов
                log_channel = interaction.guild.get_channel(LOG_CHANNEL)
                webhooks = await log_channel.webhooks()
                if webhooks:
                    webhook = webhooks[0]
                else:
                    webhook = await log_channel.create_webhook(
                        name="Лилия, следящая за информацией",
                        avatar=await interaction.user.display_avatar.read()
                    )

                # Формируем Embed
                embed = discord.Embed(
                    title=f"Изменено сообщение в #{channel.name}",
                    url=f"https://discord.com/channels/{interaction.guild.id}/{channel.id}/{message.id}",
                    color=0xF1C40F  # жёлтый (для изменения)
                )
                embed.set_author(
                    name=interaction.user.name,
                    icon_url=interaction.user.display_avatar.url
                )

                embed.add_field(name="Старое сообщение:", value=old_content, inline=False)
                embed.add_field(name="Формат:", value=log_old_content, inline=False)
                embed.add_field(name="Новое сообщение:", value=formatted_content, inline=False)
                embed.add_field(name="Формат:", value=log_content, inline=False)

                embed.set_footer(text=message.id)

                # Отправляем лог через вебхук
                await webhook.send(embed=embed)

                # Ответ пользователю
                await interaction.response.send_message("Сообщение изменено.", ephemeral=True)

        except Exception as e:
            print(f"Error edit_message: {e}")
            await interaction.response.send_message("Произошла ошибка при изменении сообщения.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(panel(bot))