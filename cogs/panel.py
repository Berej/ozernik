import asyncio
import discord
from discord.ext import commands

import botconfig

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
        if message.guild is None or message.guild.id != botconfig.GUILD:
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

async def setup(bot):
    await bot.add_cog(panel(bot))