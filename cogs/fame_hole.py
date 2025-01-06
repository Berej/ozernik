import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import typing
from datetime import datetime
import asyncio

glory_mods = [779015800555176006, 725675581881974794, 1296437623761539146]
#glory_group = app_commands.Group(name='активность', description='Работа с "залом славы"')

#Checking and creating DB
def new_rank_base(guild):
    con = sqlite3.connect('base {}.db'.format(guild.id))
    con.execute('''CREATE TABLE IF NOT EXISTS "rank" (
"uid"	INTEGER NOT NULL,
"sum"	INTEGER NOT NULL DEFAULT 0,
"event"	INTEGER NOT NULL DEFAULT 0,
"sigame"	INTEGER NOT NULL DEFAULT 0,
"top 1"	INTEGER NOT NULL DEFAULT 0,
"top 3"	INTEGER NOT NULL DEFAULT 0,
"lib"	INTEGER NOT NULL DEFAULT 0,
"public"	INTEGER NOT NULL DEFAULT 0,
"role active"	INTEGER NOT NULL DEFAULT 0,
"role custom"	INTEGER NOT NULL DEFAULT 0,
"past seasons"	INTEGER NOT NULL DEFAULT 0
)''')
    con.close

#Moderator check
def is_gm(user_roles):
    for role in user_roles:
        if role.id in glory_mods:
            return True

##Leaderboard generator
def create_top(guild):
    top_embed = discord.Embed(title='Топ Зала славы', color=discord.Colour.red())
    new_rank_base(guild)
    glory_list = sqlite3.connect('base {}.db'.format(guild.id)).execute('SELECT "uid", "sum", "past seasons" FROM "rank" ORDER BY "sum" DESC LIMIT 25').fetchall()
    num = 1
    for row in glory_list:
        if row[1] != 0:
            try:
                if num > 3:
                    place = str(num)+'.'
                elif num == 1:
                    place = ':first_place:'
                elif num == 2:
                    place = ':second_place:'
                elif num == 3:
                    place = ':third_place:'
                top_embed.add_field(name='{place} {member}'.format(place = place, member = guild.get_member(row[0]).display_name), value='Баллов в сезоне: ***{season}*** \n-# Всего баллов: {total}'.format(season = row[1], total = row[1]+row[2]), inline=False)
                num += 1
            except:
                pass
    return top_embed

## Ranks stuff for DB
def OzRank(uid, guild, act, case, count):
    new_rank_base(guild)
    con = sqlite3.connect('base {}.db'.format(guild.id))
    cursor = con.execute("SELECT * FROM rank WHERE uid=?",(uid,))
    if cursor.fetchone() is None:
        con.close()
        return None
    else:
        cursor = con.execute('SELECT * FROM rank WHERE uid = {}'.format(uid))
        r = cursor.fetchone()
        old = r[case+1]
        if case == 1:
            n = count if count != None else 6
            new = old+n if act == 1 else old-n
            con.execute('UPDATE rank SET "event" = {new} WHERE uid={uid}'.format(new = new, uid = uid))
            resp = 'за победу в ивенте **{old}** -> **{new}**'.format(old = old, new = new)
        elif case == 2:
            n = count if count != None else 4
            new = old+n if act == 1 else old-n
            con.execute('UPDATE rank SET "sigame" = {new} WHERE uid={uid}'.format(new = new, uid = uid))
            resp = 'за победу в SIGame **{old}** -> **{new}**'.format(old = old, new = new)
        elif case == 3:
            n = count if count != None else 2
            new = old+n if act == 1 else old-n
            con.execute('UPDATE rank SET "top 1" = {new} WHERE uid={uid}'.format(new = new, uid = uid))
            resp = 'за топ-1 по опыту в неделе **{old}** -> **{new}**'.format(old = old, new = new)
        elif case == 4:
            n = count if count != None else 1
            new = old+n if act == 1 else old-n
            con.execute('UPDATE rank SET "top 3" = {new} WHERE uid={uid}'.format(new = new, uid = uid))
            resp = 'за топ-3 по опыту в неделе **{old}** -> **{new}**'.format(old = old, new = new)
        elif case == 5:
            new = old+1 if act == 1 else old-1
            con.execute('UPDATE rank SET "lib" = {new} WHERE uid={uid}'.format(new = new, uid = uid))
            resp = 'за публикацию в библиотеке **{old}** -> **{new}**'.format(old = old, new = new)
        elif case == 6:
            new = old+2 if act == 1 else old-2
            con.execute('UPDATE rank SET "public" = {new} WHERE uid={uid}'.format(new = new, uid = uid))
            resp = 'за публикацию в публикации **{old}** -> **{new}**'.format(old = old, new = new)
        elif case == 7:
            n = count if count != None else 3
            new = old+n if act == 1 else old-n
            con.execute('UPDATE rank SET "role active" = {new} WHERE uid={uid}'.format(new = new, uid = uid))
            resp = 'за кастомку (актив или заслуги) **{old}** -> **{new}**'.format(old = old, new = new)
        elif case == 8:
            n = count if count != None else 2
            new = old+n if act == 1 else old-n
            con.execute('UPDATE rank SET "role custom" = {new} WHERE uid={uid}'.format(new = new, uid = uid))
            resp = 'за кастомку "просто так" **{old}** -> **{new}**'.format(old = old, new = new)
        else:
            con.close()
            return False
        cursor = con.execute('SELECT * FROM rank WHERE uid = {}'.format(uid))
        r = cursor.fetchone()
        summa = r[2]+r[3]+r[4]+r[5]+r[6]+r[7]+r[8]+r[9]
        con.execute('UPDATE rank SET "sum" = {summa} WHERE uid={uid}'.format(summa = summa, uid = uid))
        con.commit()
        con.close()
        return resp

def get_rank(uid, guild):
    new_rank_base(guild)
    con = sqlite3.connect('base {}.db'.format(guild.id))
    cursor = con.execute("SELECT * FROM rank WHERE uid=?",(uid,))
    if cursor.fetchone() is None:
        con.close()
        return False
    else:
        cursor = con.execute('SELECT * FROM rank WHERE uid = {}'.format(uid))
        r = cursor.fetchone()
        con.close
        return r
    
## TOPS
# top 10
def top_10(guild):
    score_embed = discord.Embed(title='Топ-10 зала славы', color=discord.Color.red())
    new_rank_base(guild)
    con = sqlite3.connect('base {}.db'.format)
    cursor = con.execute('SELECT "uid", "sum", "past seasons" FROM rank ORDER BY "sum" DESC LIMIT 10')
    num = 1
    for row in cursor:
        try:
            score_embed.add_field(name='{num}. {user}'.format(num = num, user = guild.get_member(int(row[0])).display_name), value='**Баллов в сезоне: {sum}**\nВсего: {total}'.format(sum = row[1], total = row[1]+row[2]), inline=False)
            num += 1
        except:
            pass
    con.close()
    return score_embed
# global top
def top_all(guild):
    score_embed = discord.Embed(title='Полный топ зала славы', color=discord.Color.red())
    new_rank_base(guild)
    con = sqlite3.connect('base {}.db'.format)
    cursor = con.execute('SELECT "uid", "sum", "past seasons" FROM "rank" ORDER BY "sum" DESC LIMIT 25').fetchall()# [0] id   [1] сумма сезона   [2] прошлые сезоны
    num = 1
    for row in cursor:
        try:
            score_embed.add_field(name='{num}. {user}'.format(num = num, user = guild.get_member(int(row[0])).display_name), value='**Баллов в сезоне: {sum}**\nВсего: {total}'.format(sum = row[1], total = row[1]+row[2]), inline=False)
            num += 1
        except:
            pass
    con.close()
    return score_embed

class topView(discord.ui.View):
    # show top 10
    @discord.ui.button(label='Топ-10', disabled= True)
    async def top10(self, interaction:discord.Interaction, button:discord.ui.Button):
        button.disabled = True
        self.topall.disabled = False
        await interaction.response.edit_message(embed=top_10(interaction.guild), view=self)
    # show global top
    @discord.ui.button(label='Полный топ')
    async def topall(self, interaction:discord.Interaction, button:discord.ui.Button):
        button.disabled = True
        self.top10.disabled = False
        await interaction.response.edit_message(embed=top_all(interaction.guild), view=self)

## Report (game hall (hole :D))
def create_report(interaction):
    report_path = "Отчёт зал славы {season} ({date}).csv".format(season = sqlite3.connect('base {}.db'.format(interaction.guild.id)).execute('SELECT "season" FROM "glory settings"').fetchone()[0], date = datetime.now().strftime("%d%m%Y%H%M%S"))
    with open(report_path, 'a') as tab:
        tab.write('Участник;Ивенты;Сигеймы;Топ-1;Топ-3;Библиотека;Публикации;Роль за актив;Роль просто так;Сумма сезона;Прошлые сезоны')
        for row in sqlite3.connect('base {}.db'.format(interaction.guild.id)).execute('SELECT * FROM "rank" ORDER BY "sum" DESC').fetchall():
            try:
                tab.write('\n{user} ({id});{event};{sigame};{top1};{top3};{lib};{posts};{roleactive};{rolejust};{sum};{pastseasons}'.format(user = interaction.guild.get_member(row[0]).display_name, id = interaction.guild.get_member(row[0]), event = row[2], sigame = row[3], top1 = row[4], top3 = row[5], lib = row[6], posts = row[7], roleactive = row[8], rolejust = row[9], sum = row[1], pastseasons = row[10]))
            except:
                tab.write('\nПотеряный пользователь ({id});{event};{sigame};{top1};{top3};{lib};{posts};{roleactive};{rolejust};{sum};{pastseasons}'.format(id = interaction.guild.get_member(row[0]), event = row[2], sigame = row[3], top1 = row[4], top3 = row[5], lib = row[6], posts = row[7], roleactive = row[8], rolejust = row[9], sum = row[1], pastseasons = row[10]))
    return report_path
    
async def upd_wall(self, guild):
    try:
        channel = sqlite3.connect('base {}.db'.format(guild.id)).execute('SELECT "glory channel" FROM "glory settings"').fetchone()[0]
        message = sqlite3.connect('base {}.db'.format(guild.id)).execute('SELECT "glory message" FROM "glory settings"').fetchone()[0]
        print(channel, message)
        await self.bot.get_channel(channel).get_partial_message(message).edit(embed=create_top(guild))
    except:
        pass
    
## End of season
# Cancel permission (5 minutes before cancellation)
ready_reset = False
class season_view(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    @discord.ui.button(label='Отмена', style=discord.ButtonStyle.red)
    async def cancel_reset(self, interaction:discord.Interaction, button:discord.ui.Button):
        ready_reset = False
        await interaction.response.edit_message('Сброс сезона был отменён', view=None)

# Score in context
@app_commands.context_menu(name='Зал славы')
async def ctx_glory(interaction:discord.Interaction, user:discord.User):
    exrank = get_rank(user.id, interaction.guild)#ищет участника в базе
    if exrank == False:
        await interaction.response.send_message('Участник не учавствует в рейтинге:confused:', ephemeral=True)
    elif exrank == None:
        await interaction.response.send_message('Что-то пошло не так:anguished:\nПопробуйте ещё раз. Если это не помогает - обратитесь к <@685425244051079222>', ephemeral=True)
    else:
        rank_embed = discord.Embed(title='Баллы активности {}'.format(user.display_name), color=discord.Color.random())
        rank_embed.set_thumbnail(url = user.display_avatar)
        rank_embed.add_field(name='Баллы в сезоне: {}'.format(exrank[1]), value='\
* Победы в ивенте: {event}\n\
* Победы в SIGame: {sigame}\n\
* Топ-1 недели: {top1}\n\
* Топ-3 недели: {top3}\n\
* Посты в библиотеке: {lib}\n\
* Посты в публикациях: {posts}\n\
* Кастомки за заслуги: {roleactive}\n\
* Кастомки "просто так": {rolejust}\n\
\n\
*Баллы в прошлах сезонах: {pastseasons}*\n\
-# Всего баллов: {total}'.format(event = exrank[2], sigame = exrank[3] , top1 = exrank[4], top3 = exrank[5], lib = exrank[6], posts = exrank[7], roleactive = exrank[8], rolejust = exrank[9], pastseasons = exrank[10], total = exrank[1] + exrank[10]))
        await interaction.response.send_message(embed = rank_embed, ephemeral=True)

class GloryGroup(commands.GroupCog, name="активность", ):
    def __init__(self, bot):
        self.bot = bot
        # Init commands group
    #Check and creating DB
    # Wall

    # Init setup wall
    @app_commands.command(name='запуск', description='Запустить "Зал славы"')
    @app_commands.rename(channel='канал')
    @app_commands.describe(channel='Канал "Зал славы", в котором публикуется таблица лидеров')
    async def start_glory(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if is_gm(interaction.user.roles) == True:
            con = sqlite3.connect('base {}.db'.format(interaction.guild.id))
            con.execute('''CREATE TABLE IF NOT EXISTS "glory settings" ("glory channel" INTEGER, "glory message" INTEGER, "season" INTEGER NOT NULL DEFAULT 2)''')
            try:
                restore_season = con.execute('SELECT "season" FROM "glory settings"').fetchone()
                if restore_season == None:
                    restore_season = 2
                else:
                    restore_season = restore_season[0]
                print("Сохранённый сезон", restore_season)
                con.execute('DELETE FROM "glory settings"')
            except:
                pass
            try:
                wall_msg = await channel.send(embed=create_top(interaction.guild))
                con.execute('INSERT INTO "glory settings" ("glory channel", "glory message", "season") VALUES ({channel}, {msg}, {season})'.format(channel = channel.id, msg = wall_msg.id, season = restore_season))#вписать какнал и соо
                con.commit()
                await interaction.response.send_message('Топ запущен {}'.format(channel.get_partial_message(wall_msg.id).jump_url), ephemeral=True)
            except:
                print('ОШИБКА ФАЙЛА ЗАЛА СЛАВЫ!!!')
        else:
            await interaction.response.send_message('У Вас нет доступа к этой команде', ephemeral=True)

    @app_commands.command(name="модерация", description="Изменение баллов участника")
    @app_commands.rename(user="участник", action="действие", reason="причина", count="сумма")
    @app_commands.describe(
        user="Участник, которому нужно изменить баллы",
        action="Добавить или отнять баллы",
        reason="Причина, по которой происходит изменение баллов",
        count="Заполнять, если требуется изменить на нестандартное число"
    )
    @app_commands.choices(
        action=[
            app_commands.Choice(name="Добавить", value=1),
            app_commands.Choice(name="Отнять", value=2),
        ],
        reason=[
            app_commands.Choice(name="Победа в ивенте (6 баллов)", value=1),
            app_commands.Choice(name="Победа в SIGame (4 балла)", value=2),
            app_commands.Choice(name="Топ-1 по опыту в неделе (2 балла)", value=3),
            app_commands.Choice(name="Топ-3 по опыту в неделе (1 балл)", value=4),
            app_commands.Choice(name="Публикация в библиотеке (1 балл)", value=5),
            app_commands.Choice(name="Публикация в публикации (2 балла)", value=6),
            app_commands.Choice(name="Кастомка за актив или заслуги (3 балла)", value=7),
            app_commands.Choice(name="Кастомка 'просто так' (2 балла)", value=8),
        ]
    )
    async def mod_score(
        self,
        interaction: discord.Interaction,
        user: discord.User,
        action: app_commands.Choice[int],
        reason: app_commands.Choice[int],
        count: typing.Optional[int] = None,
    ):
        if is_gm(interaction.user.roles) == True:
            # Looking for user in DB
            exrank = OzRank(user.id, interaction.guild, action.value, reason.value, count)
            if exrank == None:
                await interaction.response.send_message('Участник не учавствует в рейтинге:confused:', ephemeral=True)
            elif exrank == False:
                await interaction.response.send_message('Что-то пошло не так:anguished:\nПопробуйте ещё раз', ephemeral=True)
            else:
                await upd_wall(self, interaction.guild)
                await interaction.response.send_message('Изменены баллы {user} {exrank}'.format(user = user.display_name, exrank = exrank))
        else:
            await interaction.response.send_message('У Вас нет доступа к этой команде', ephemeral=True)
            
    @app_commands.command(name='добавить', description='Добавить участника в "Зал славы"')
    async def add_member(self, interaction:discord.Interaction, user:discord.Member):
        if  is_gm(interaction.user.roles) == True:
            con = sqlite3.connect('base {}.db'.format(interaction.guild.id))
            con.row_factory = lambda cursor, row: row[0]
            if user.id in con.execute('SELECT "uid" FROM "rank"').fetchall():
                await interaction.response.send_message('Участник уже есть в списке', ephemeral=True)
            else:
                con.execute('INSERT INTO "rank" (uid) VALUES ({})'.format(user.id))
                con.commit()
                await interaction.response.send_message('{} добавлен в список'.format(user.mention), ephemeral=True)
        else:
            await interaction.response.send_message('У Вас нет доступа к этой команде', ephemeral=True)
    
    @app_commands.command(name='топ', description='Топ зала славы')
    async def topscore(self, interaction:discord.Interaction):
        await interaction.response.send_message(embed=top_10(interaction.guild), view=topView(), ephemeral=True)

    # Personal score
    @app_commands.command(name='баллы', description='Показывает баллы участника в зале славы')
    @app_commands.rename(user='озёрник')
    @app_commands.describe(user='Озёрник, баллы которого Вы хотите узнать')
    async def uscore(self, interaction: discord.Interaction, user: typing.Optional[discord.User] = None):
        # If the user is not specified, we use the author of the command
        user = user or interaction.user
        exrank = get_rank(user.id, interaction.guild)#Looking for user in DB
        if exrank == False:
            await interaction.response.send_message('Участник не учавствует в рейтинге:confused:', ephemeral=True)
        elif exrank == None:
            await interaction.response.send_message('Что-то пошло не так:anguished:\nПопробуйте ещё раз. Если это не помогает - обратитесь к <@685425244051079222>', ephemeral=True)
        else:
            rank_embed = discord.Embed(title='Баллы активности {}'.format(user.display_name), color=discord.Color.random())
            rank_embed.set_thumbnail(url = user.display_avatar)
            rank_embed.add_field(name='Баллы в сезоне: {}'.format(exrank[1]), value='\
* Победы в ивенте: {event}\n\
* Победы в SIGame: {sigame}\n\
* Топ-1 недели: {top1}\n\
* Топ-3 недели: {top3}\n\
* Посты в библиотеке: {lib}\n\
* Посты в публикациях: {posts}\n\
* Кастомки за заслуги: {roleactive}\n\
* Кастомки "просто так": {rolejust}\n\
\n\
*Баллы в прошлах сезонах: {pastseasons}*\n\
-# Всего баллов: {total}'.format(event = exrank[2], sigame = exrank[3] , top1 = exrank[4], top3 = exrank[5], lib = exrank[6], posts = exrank[7], roleactive = exrank[8], rolejust = exrank[9], pastseasons = exrank[10], total = exrank[1] + exrank[10]))
            await interaction.response.send_message(embed = rank_embed, ephemeral=True)

    @app_commands.command(name='отчёт', description='Запросить таблицу Зала славы')
    async def glory_report(self, interaction:discord.Interaction):
        if is_gm(interaction.user.roles) == True:
            report_path = create_report(interaction)
            print('Отправка отчёта')
            with open(report_path, 'rb') as report:
                await interaction.response.send_message(file=discord.File(report, report_path))
        else:
            await interaction.response.send_message('У Вас нет доступа к этой команде', ephemeral=True)

    # 
    @app_commands.command(name='сброс', description='Завершить сезон')
    async def reset_season(self, interaction:discord.Interaction):
        if is_gm(interaction.user.roles) == True:
            con = sqlite3.connect('base {}.db'.format(interaction.guild.id))
            # recount
            con.execute('UPDATE rank SET "sum" = "event"+"sigame"+"top 1"+"top 3"+"lib"+"public"+"role active"+"role custom"')
            con.commit()
            ready_reset = True
            # report
            report_path = create_report(interaction)
            with open(report_path, 'rb') as report:
                await interaction.response.send_message('Зал славы будет сброшен через ***5 минут***', view=season_view(), file=discord.File(report, 'Зал славы отчёт сезона {}.csv'.format(con.execute('SELECT "season" FROM "glory settings"').fetchone()[0])))
            # transfer
            await asyncio.sleep(300)
            if ready_reset == True:
                con.execute('UPDATE rank SET "past seasons"="past seasons"+"sum"')
                con.execute('UPDATE rank SET "sum" = 0, "event" = 0, "sigame" = 0, "top 1" = 0, "top 3" = 0, "lib" = 0, "public" = 0, "role active" = 0, "role custom" = 0')
                con.execute('UPDATE "glory settings" SET "season" = "season"+1')
                con.commit()
        else:
            await interaction.response.send_message('У Вас нет доступа к этой команде', ephemeral=True)
# Registering a group in the command tree
async def setup(bot):
    await bot.add_cog(GloryGroup(bot))
