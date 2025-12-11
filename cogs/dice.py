import discord, random, time
from discord import app_commands, Interaction
from discord.ext import commands
from config_loader import config

number_emoji = {0: "⬛", 1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣", 6: "6️⃣", }

class ConfirmView(discord.ui.View):
    def __init__(self, opponent: discord.User):
        super().__init__(timeout=60)
        self.confirmed = False
        self.opponent = opponent

    @discord.ui.button(label="Принять дуэль", style=discord.ButtonStyle.success) # noqa
    async def confirm(self, interaction: Interaction, button: discord.ui.Button): # noqa
        if interaction.user.id != self.opponent.id:
            await interaction.response.send_message("Не тебя вызвали.", ephemeral=True)
            return
        await interaction.response.defer()
        self.confirmed = True
        self.stop()

class TimeCancelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="Время истекло", style=discord.ButtonStyle.gray, disabled=True))
class ConfirmedView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="Дуэль принята", style=discord.ButtonStyle.gray, disabled=True))


class Squares(discord.ui.View):
    def __init__(self, matrix: dict | None = None, en_matrix: dict | None = None, dice: int | None = None):
        try:
            super().__init__(timeout=None)
            self.dice = dice

            if matrix is None:
                matrix = [[0, 0, 0],
                          [0, 0, 0],
                          [0, 0, 0]]
            if en_matrix is None:
                en_matrix = [[0, 0, 0],
                             [0, 0, 0],
                             [0, 0, 0]]

            self.matrix = matrix
            self.en_matrix = en_matrix

            score = [0, 0, 0]
            for i, column in enumerate(matrix):
                a, b, c = column
                if a == b == c:
                    score[i] = (a + b + c) * 3
                elif a == b:
                    score[i] = (a + b) * 2 + c
                elif a == c:
                    score[i] = (a + c) * 2 + b
                elif b == c:
                    score[i] = (b + c) * 2 + a
                else:
                    score[i] = a + b + c

            full_score = sum(score)

            for value in score:
                self.add_item(discord.ui.Button(
                    label=str(value),
                    style=discord.ButtonStyle.gray,
                    disabled=True,
                    row=0
                ))

            self.add_item(discord.ui.Button(
                label=str(full_score),
                style=discord.ButtonStyle.gray,
                disabled=True,
                row=0
            ))

            style = discord.ButtonStyle.gray
            if dice is not None:
                style = discord.ButtonStyle.green

            for col, values in enumerate(matrix):
                for row, value in enumerate(values, start=1):
                    disabled_ = value != 0 or dice is None

                    btn = discord.ui.Button(
                        style=style,
                        emoji=number_emoji[value],
                        disabled=disabled_,
                        row=row,
                        custom_id=f"square_{col}_{row}"
                    )

                    btn.callback = self.on_click
                    self.add_item(btn)

            if dice is not None:
                btn = discord.ui.Button(
                    label=f'{number_emoji[dice]}',
                    style=discord.ButtonStyle.primary,
                    disabled=True,
                    row=1
                )
                self.add_item(btn)
        except Exception as error:
            print(error)

    # ---- CALLBACK ----

    async def on_click(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer()
            custom_id = interaction.data["custom_id"]  # 'square_1_2'
            _, col, row = custom_id.split("_")
            col = int(col)
            row = int(row) - 1

            self.matrix[col][row] = self.dice
            for i in range(len(self.en_matrix[col])):
                if self.en_matrix[col][i] == self.dice:
                    self.en_matrix[col][i] = 0

            self.stop()
        except Exception as error:
            print(error)


class MirrorSquares(discord.ui.View):
    def __init__(self, matrix: dict | None = None, dice: int | None = None):
        try:
            super().__init__(timeout=None)
            self.dice = dice

            if matrix is None:
                matrix = [[0, 0, 0],
                          [0, 0, 0],
                          [0, 0, 0]]

            score = [0, 0, 0]
            for i, column in enumerate(matrix):
                a, b, c = column
                if a == b == c:
                    score[i] = (a + b + c) * 3
                elif a == b:
                    score[i] = (a + b) * 2 + c
                elif a == c:
                    score[i] = (a + c) * 2 + b
                elif b == c:
                    score[i] = (b + c) * 2 + a
                else:
                    score[i] = a + b + c


            full_score = 0
            for value in score:
                self.add_item(discord.ui.Button(label=f"{value}", style=discord.ButtonStyle.gray, disabled=True, row=0))
                full_score += value
            self.add_item(discord.ui.Button(label=f"{full_score}", style=discord.ButtonStyle.gray, disabled=True, row=0))

            style = discord.ButtonStyle.gray
            if dice is not None:
                style = discord.ButtonStyle.green

            for column in matrix:
                for n, value in enumerate(column, start=1):
                    self.add_item(discord.ui.Button(style=style, disabled=True, emoji=number_emoji[value], row=n))

            if dice is not None:
                btn = discord.ui.Button(
                    label=f'{number_emoji[dice]}',
                    style=discord.ButtonStyle.primary,
                    disabled=True,
                    row=1
                )
                self.add_item(btn)
        except Exception as error:
            print(error)


class Dice(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.guilds(discord.Object(id=config.GUILD))
    @app_commands.command(name="dice_duel", description="Вызвать человека на дуэль костей.")
    @app_commands.describe(opponent="Оппонент.")
    async def ping(self, interaction: Interaction, opponent: discord.User):
        if interaction.user == opponent:
            await interaction.response.send_message(content='Нельзя вызвать на дуэль самого себя.', ephemeral=True)
            return
        if opponent.bot:
            await interaction.response.send_message(content='Нельзя вызвать на дуэль бота.', ephemeral=True)
            return

        player1 = interaction.user
        player2 = opponent

        view = ConfirmView(player2)
        await interaction.response.send_message(content=f"{player1.mention} инициирует дуэль с {player2.mention} на костях!", view=view)

        await view.wait()
        if view.confirmed:
            confirm_view = ConfirmedView()
            await interaction.edit_original_response(content=f"{player1.mention} инициировал дуэль с {player2.mention} на костях!", view=confirm_view)
        else:
            cancel_view = TimeCancelView()
            await interaction.edit_original_response(content=f"{player1.mention} инициирует дуэль с {player2.mention} на костях!", view=cancel_view)
            return

        player1_matrix = [[0, 0, 0],
                          [0, 0, 0],
                          [0, 0, 0]]

        player2_matrix = [[0, 0, 0],
                          [0, 0, 0],
                          [0, 0, 0]]

        winner = None

        player1_enemy = await player1.send("**Оппонент:**")
        player1_panel = await player1.send("**Ты:**")
        player2_enemy = await player2.send("**Оппонент:**")
        player2_panel = await player2.send("**Ты:**")

        player1_panel_view = Squares()
        await player1_panel.edit(content="**Ты:**", view=player1_panel_view)

        player1_enemy_view = MirrorSquares()
        await player1_enemy.edit(content="**Оппонент:**", view=player1_enemy_view)

        player2_panel_view = Squares()
        await player2_panel.edit(content="**Ты:**", view=player2_panel_view)

        player2_enemy_view = MirrorSquares()
        await player2_enemy.edit(content="**Оппонент:**", view=player2_enemy_view)

        players = [player1, player2]
        turn = 0

        def no_zeros(matrix):
            return not any(0 in row for row in matrix)

        while winner is None:
            player = players[turn % 2]
            if player == player1 and not no_zeros(player1_matrix) and not no_zeros(player2_matrix):
                random.seed(int(time.time() * 1000))
                dice = random.randint(1, 6)

                player1_panel_view = Squares(matrix=player1_matrix, en_matrix=player2_matrix, dice=dice)
                player2_enemy_view = MirrorSquares(matrix=player1_matrix, dice=dice)

                await player2_enemy.edit(content="**Оппонент:**", view=player2_enemy_view)
                await player1_panel.edit(content="**Ты:**", view=player1_panel_view)

                await player1_panel_view.wait()
                player1_matrix = player1_panel_view.matrix
                player2_matrix = player1_panel_view.en_matrix

                player1_panel_view = Squares(matrix=player1_matrix)
                player2_enemy_view = MirrorSquares(matrix=player1_matrix)

                await player1_panel.edit(content="**Ты:**", view=player1_panel_view)
                await player2_enemy.edit(content="**Оппонент:**", view=player2_enemy_view)

                turn += 1
            elif player == player2 and not no_zeros(player1_matrix) and not no_zeros(player2_matrix):
                random.seed(int(time.time() * 1000))
                dice = random.randint(1, 6)

                player2_panel_view = Squares(matrix=player2_matrix, en_matrix=player1_matrix, dice=dice)
                player1_enemy_view = MirrorSquares(matrix=player2_matrix, dice=dice)

                await player1_enemy.edit(content="**Оппонент:**", view=player1_enemy_view)
                await player2_panel.edit(content="**Ты:**", view=player2_panel_view)

                await player2_panel_view.wait()
                player2_matrix = player2_panel_view.matrix
                player1_matrix = player2_panel_view.en_matrix

                player2_panel_view = Squares(matrix=player2_matrix)
                player1_enemy_view = MirrorSquares(matrix=player2_matrix)

                await player2_panel.edit(content="**Ты:**", view=player2_panel_view)
                await player1_enemy.edit(content="**Оппонент:**", view=player1_enemy_view)

                turn += 1
            else:
                player1_score = [0, 0, 0]
                for i, column in enumerate(player1_matrix):
                    a, b, c = column
                    if a == b == c:
                        player1_score[i] = (a + b + c) * 3
                    elif a == b:
                        player1_score[i] = (a + b) * 2 + c
                    elif a == c:
                        player1_score[i] = (a + c) * 2 + b
                    elif b == c:
                        player1_score[i] = (b + c) * 2 + a
                    else:
                        player1_score[i] = a + b + c
                full_player1_score = sum(player1_score)

                player2_score = [0, 0, 0]
                for i, column in enumerate(player2_matrix):
                    a, b, c = column
                    if a == b == c:
                        player2_score[i] = (a + b + c) * 3
                    elif a == b:
                        player2_score[i] = (a + b) * 2 + c
                    elif a == c:
                        player2_score[i] = (a + c) * 2 + b
                    elif b == c:
                        player2_score[i] = (b + c) * 2 + a
                    else:
                        player2_score[i] = a + b + c
                full_player2_score = sum(player2_score)

                winner_score = None
                lose_score = None
                loser = None
                if full_player1_score > full_player2_score:
                    winner = player1
                    loser = player2
                    winner_score = full_player1_score
                    lose_score = full_player2_score
                elif full_player1_score < full_player2_score:
                    winner = player2
                    loser = player1
                    winner_score = full_player2_score
                    lose_score = full_player1_score
                else:
                    winner = False
                    lose_score = full_player1_score

                if winner:
                    await interaction.followup.send(f'## {winner.mention} — {winner_score}!\n## {loser.mention} — {lose_score}.')
                else:
                    await interaction.followup.send(f'# Ничья!\n ## {player1.mention} и {player2.mention} — {lose_score}!')
                return

async def setup(bot):
    await bot.add_cog(Dice(bot))