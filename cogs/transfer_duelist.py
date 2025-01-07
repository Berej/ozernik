import discord
from discord.ext import commands
from discord import app_commands

# Role list
duel_1 = set()
duel_2 = set()
duel_3 = set()
duel_4 = set()
duel_5 = set()
duel_role_list = set()

# Function to initialize roles
def set_dl(bot):
    global duel_1, duel_2, duel_3, duel_4, duel_5, duel_role_list
    duel_1 = bot.get_guild(722824269683359877).get_role(730790262300868738)  # Level 1
    duel_2 = bot.get_guild(722824269683359877).get_role(1163757921524535378)  # Level 2
    duel_3 = bot.get_guild(722824269683359877).get_role(1163757933960626236)  # Level 3
    duel_4 = bot.get_guild(722824269683359877).get_role(1163757939098669096)  # Level 4
    duel_5 = bot.get_guild(722824269683359877).get_role(1161337472609943632)  # Level 5
    duel_role_list = [duel_1, duel_2, duel_3, duel_4, duel_5]  # Role list (1-5 levels)

# Duelist role checker
def is_duelist(roles):
    for role in roles:
        if role in duel_role_list:
            return role

# Class for transfer handling
class Transfer:
    free = True
    duelist_1 = None
    duelist_2 = None
    duelist_role_1 = None
    duelist_role_2 = None

# Class to represent a transfer request
class ConfirmTransfer(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(label='Принять', style=discord.ButtonStyle.green)
    async def accept_transfer(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != Transfer.duelist_2:
            await interaction.response.send_message(f'Принять предложение может только {Transfer.duelist_2.mention}', ephemeral=True)
        else:
            # Transfer roles
            if Transfer.duelist_role_1 != duel_1:
                await Transfer.duelist_1.add_roles(duel_role_list[duel_role_list.index(Transfer.duelist_role_1)-1])
            await Transfer.duelist_1.remove_roles(Transfer.duelist_role_1)

            if Transfer.duelist_role_2 is None:
                await Transfer.duelist_2.add_roles(duel_1)
            else:
                await Transfer.duelist_2.add_roles(duel_role_list[duel_role_list.index(Transfer.duelist_role_2)+1])
                await Transfer.duelist_2.remove_roles(Transfer.duelist_role_2)

            # Allow new requests
            Transfer.free = True
            await interaction.response.edit_message(content=f'{Transfer.duelist_1} передал дуэлянта {Transfer.duelist_2}', view=None)

    @discord.ui.button(label='Отменить', style=discord.ButtonStyle.red)
    async def cancel_transfer(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == Transfer.duelist_1 or interaction.user == Transfer.duelist_2:
            await interaction.response.edit_message(content='Передача отменена.', view=None)
            Transfer.free = True
        else:
            await interaction.response.send_message(f'Отменить передачу могут только {Transfer.duelist_1.mention} и {Transfer.duelist_2.mention}', ephemeral=True)

    def on_timeout(self):
        Transfer.free = True

# Cog class for transfer
class DuelistTransferCog(commands.GroupCog, name = 'transfer'):
    def __init__(self, bot):
        self.bot = bot
        set_dl(self.bot)  # Initialize roles

    @app_commands.command(name="duelist", description="Передать уровень дуэлянта другому человеку")
    @app_commands.rename(recipient="получатель")
    @app_commands.describe(recipient="Человек, который получит от вас уровень дуэлянта")
    async def transfer(self, interaction: discord.Interaction, recipient: discord.Member):
        d1_role = is_duelist(interaction.user.roles)
        d2_role = is_duelist(recipient.roles)

        if interaction.user != recipient:
            if Transfer.free:
                if d1_role:
                    if d2_role != duel_5:
                        Transfer.free = False
                        Transfer.duelist_1, Transfer.duelist_2 = interaction.user, recipient
                        Transfer.duelist_role_1, Transfer.duelist_role_2 = d1_role, d2_role
                        await interaction.response.send_message(f'{Transfer.duelist_1} хочет передать уровень дуэлянта {Transfer.duelist_2}', view=ConfirmTransfer())
                    else:
                        await interaction.response.send_message('Отправка невозможна. У получателя уже максимальный уровень', ephemeral=True)
                else:
                    await interaction.response.send_message('Вы не дуэлянт, и поэтому не можете использовать эту команду', ephemeral=True)
            else:
                await interaction.response.send_message('Передача роли сейчас невозможна. Попробуйте позже', ephemeral=True)
        else:
            await interaction.response.send_message('Интересный ход, но вы не можете передать роль самому себе', ephemeral=True)

async def setup(bot):
    await bot.add_cog(DuelistTransferCog(bot))
