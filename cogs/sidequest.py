# tasks_sidequests_cog.py
import asyncio
import pickle
import os
import time
from dataclasses import dataclass, field
from typing import Dict, Optional

import discord
from discord.ext import commands
from discord import app_commands, Interaction

# Попробуй подставить из config_loader, иначе поменяй вручную тут:
try:
    from config_loader import config
    GUILD_ID = config.GUILD
    GENERAL_CHANNEL_ID = 1324397082404196515
    SAVE_FILE = "game_state.pkl"
    CATS_EMOJI_NAME = "skull"
    SIDEQUEST_CHANNEL_ID = 1448210668586139731
except Exception:
    GUILD_ID = None
    GENERAL_CHANNEL_ID = None
    SAVE_FILE = "game_state.pkl"
    CATS_EMOJI_NAME = "skull"
    SIDEQUEST_CHANNEL_ID = None

# Пороговые значения
TASK1_MESSAGES_REQUIRED = 50
TASK2_VOICE_SECONDS_REQUIRED = 15 * 60
TASK3_CATS_REQUIRED = 10

# --- Sidequest definitions (id -> dict) ---
SIDEQUEST_DEFS = {
    1: {"type": "messages", "required": 50,  "reward": 1, "desc": "Написать 50 сообщений в основной"},
    2: {"type": "messages", "required": 100, "reward": 2, "desc": "Написать 100 сообщений в основной"},
    3: {"type": "messages", "required": 150, "reward": 3, "desc": "Написать 150 сообщений в основной"},
    4: {"type": "voice",    "required": 15*60, "reward": 1, "desc": "Сидеть в войсе 15 минут"},
    5: {"type": "voice",    "required": 30*60, "reward": 2, "desc": "Сидеть в войсе 30 минут"},
    6: {"type": "voice",    "required": 60*60, "reward": 4, "desc": "Сидеть в войсе 60 минут"},
    7: {"type": "reactions","required": 10,   "reward": 1, "desc": "Поставить суммарно 10 реакций"},
    8: {"type": "cats",     "required": 10,   "reward": 2, "desc": "Поставить 10 реакций :Cats:"},
}

# number emoji mapping for selection message (1..8)
NUMBER_EMOJIS = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣"]

@dataclass
class Player:
    user_id: int
    active_task: int = 1
    tasks: Dict[int, Dict] = field(default_factory=lambda: {
        1: {"status": "in_progress", "messages": 0},
        2: {"status": "in_progress", "voice_seconds": 0.0},
        3: {"status": "in_progress", "cats": 0}
    })
    # sidequest fields:
    side_selected: Optional[int] = None  # quest id 1..8 or None
    side_progress: float = 0.0           # generic: messages / seconds / reactions count
    side_status: str = "idle"            # "idle", "in_progress", "completed", "failed"
    ornaments: int = 0                   # количество новогодних игрушек

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "active_task": self.active_task,
            "tasks": self.tasks,
            "side_selected": self.side_selected,
            "side_progress": self.side_progress,
            "side_status": self.side_status,
            "ornaments": self.ornaments
        }

    @classmethod
    def from_dict(cls, d):
        p = cls(d["user_id"], d.get("active_task",1))
        p.tasks = d.get("tasks", p.tasks)
        p.side_selected = d.get("side_selected")
        p.side_progress = d.get("side_progress", 0.0)
        p.side_status = d.get("side_status", "idle")
        p.ornaments = d.get("ornaments", 0)
        return p

class Game:
    def __init__(self):
        self.players: Dict[int, Player] = {}
        # sidequest global state
        self.side_active: bool = False
        self.side_started_at: Optional[float] = None
        self.side_ends_at: Optional[float] = None
        self.side_message_id: Optional[int] = None
        self.side_channel_id: Optional[int] = None
        # selections stored per-player in Player.side_selected

    def get_player(self, user_id: int) -> Player:
        p = self.players.get(user_id)
        if p is None:
            p = Player(user_id=user_id)
            self.players[user_id] = p
        return p

    # --- legacy tasks updates (non-sidequests) ---
    def update_messages(self, user_id: int, amount: int = 1) -> Optional[str]:
        p = self.get_player(user_id)
        if p.tasks[1]["status"] == "completed":
            return None
        p.tasks[1]["messages"] += amount
        if p.tasks[1]["messages"] >= TASK1_MESSAGES_REQUIRED:
            p.tasks[1]["status"] = "completed"
            return "task1_completed"
        return None

    def update_voice(self, user_id: int, seconds: float) -> Optional[str]:
        p = self.get_player(user_id)
        if p.tasks[2]["status"] == "completed":
            return None
        p.tasks[2]["voice_seconds"] += seconds
        if p.tasks[2]["voice_seconds"] >= TASK2_VOICE_SECONDS_REQUIRED:
            p.tasks[2]["status"] = "completed"
            return "task2_completed"
        return None

    def update_cats(self, user_id: int, amount: int = 1) -> Optional[str]:
        p = self.get_player(user_id)
        if p.tasks[3]["status"] == "completed":
            return None
        p.tasks[3]["cats"] += amount
        if p.tasks[3]["cats"] >= TASK3_CATS_REQUIRED:
            p.tasks[3]["status"] = "completed"
            return "task3_completed"
        return None

    def reset_all(self):
        for p in self.players.values():
            p.active_task = 1
            p.tasks = {
                1: {"status": "in_progress", "messages": 0},
                2: {"status": "in_progress", "voice_seconds": 0.0},
                3: {"status": "in_progress", "cats": 0}
            }

    # --- sidequest helpers ---
    def start_sidequests(self, start_ts: float, end_ts: float, channel_id: int, message_id: int):
        self.side_active = True
        self.side_started_at = start_ts
        self.side_ends_at = end_ts
        self.side_channel_id = channel_id
        self.side_message_id = message_id
        # reset per-player side fields to allow new selections
        for p in self.players.values():
            p.side_selected = None
            p.side_progress = 0.0
            p.side_status = "in_progress"

    def end_sidequests(self):
        # finalize: for players who selected and completed, reward already given on completion.
        self.side_active = False
        self.side_started_at = None
        self.side_ends_at = None
        self.side_message_id = None
        self.side_channel_id = None
        # players who didn't finish remain as-is (status can be "in_progress" or "completed")
        # you may want to mark unfinished as "failed"
        for p in self.players.values():
            if p.side_selected and p.side_status != "completed":
                p.side_status = "failed"

    # update player's sidequest progress (only when side_active and before deadline)
    def update_side_progress(self, user_id: int, delta):
        p = self.get_player(user_id)
        if not self.side_active:
            return None
        if p.side_selected is None:
            return None
        if p.side_status == "completed":
            return None
        # generic addition, interpretation done externally
        p.side_progress += delta
        quest = SIDEQUEST_DEFS.get(p.side_selected)
        if not quest:
            return None
        if p.side_progress >= quest["required"]:
            # award
            p.side_status = "completed"
            p.ornaments += quest["reward"]
            return {"completed": p.side_selected, "reward": quest["reward"]}
        return None

    # --- pickle helpers ---
    def save_to_path(self, path: str):
        tmp = path + ".tmp"
        with open(tmp, "wb") as f:
            pickle.dump(self, f, protocol=pickle.HIGHEST_PROTOCOL)
        os.replace(tmp, path)

    @classmethod
    def load_from_path(cls, path: str) -> "Game":
        if not os.path.exists(path):
            return cls()
        with open(path, "rb") as f:
            obj = pickle.load(f)
            if isinstance(obj, cls):
                return obj
            if isinstance(obj, dict):
                g = cls()
                for k,v in obj.get("players",{}).items():
                    g.players[int(k)] = Player.from_dict(v)
                return g
            return cls()


class SidequestsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.save_file = SAVE_FILE
        self.game: Game = Game()
        self._save_lock = asyncio.Lock()
        self._voice_joins: Dict[int, float] = {}
        self._side_task_handle: Optional[asyncio.Task] = None
        bot.loop.create_task(self._load_state())

    async def _load_state(self):
        try:
            g = await asyncio.to_thread(Game.load_from_path, self.save_file)
            self.game = g
            print(f"[SidequestsCog] Loaded game state from {self.save_file}, players={len(self.game.players)}")
            # if sidequests active and there's an end time, schedule background watcher
            if self.game.side_active and self.game.side_ends_at:
                # schedule task to end it
                self._schedule_side_end_checker()
        except Exception as e:
            print("Failed to load game state:", e)
            self.game = Game()

    async def _save_state(self):
        async with self._save_lock:
            try:
                await asyncio.to_thread(self.game.save_to_path, self.save_file)
            except Exception as e:
                print("Failed to save game state:", e)

    def _schedule_side_end_checker(self):
        # cancel previous
        if self._side_task_handle and not self._side_task_handle.done():
            self._side_task_handle.cancel()
        # schedule new
        self._side_task_handle = asyncio.create_task(self._side_end_watcher())

    async def _side_end_watcher(self):
        try:
            now = time.time()
            end = self.game.side_ends_at or now
            delay = max(0, end - now)
            await asyncio.sleep(delay)
            # time's up -> finalize
            await self._finalize_sidequests()
        except asyncio.CancelledError:
            return
        except Exception as e:
            print("Error in side end watcher:", e)

    async def _finalize_sidequests(self):
        # mark failed those not completed, notify channel
        channel = None
        if self.game.side_channel_id:
            channel = self.bot.get_channel(self.game.side_channel_id)
        msg_lines = ["Сайд-квесты закончились. Результаты:"]
        completed_count = 0
        for p in self.game.players.values():
            if p.side_selected:
                if p.side_status == "completed":
                    msg_lines.append(f"<@{p.user_id}> — выполнил(а) ({SIDEQUEST_DEFS[p.side_selected]['desc']}) — получил(а) {SIDEQUEST_DEFS[p.side_selected]['reward']} 🎁")
                    completed_count += 1
                else:
                    msg_lines.append(f"<@{p.user_id}> — не выполнил(а) ({SIDEQUEST_DEFS[p.side_selected]['desc']})")
        if channel and channel.permissions_for(channel.guild.me).send_messages:
            try:
                # send in pieces if длинное
                for i in range(0, len(msg_lines), 20):
                    await channel.send("\n".join(msg_lines[i:i+20]))
            except Exception:
                pass
        # clear state
        self.game.end_sidequests()
        await self._save_state()

    # ----- Listeners -----
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if message.guild is None:
            return
        if GUILD_ID and message.guild.id != GUILD_ID:
            return
        # only count messages in GENERAL_CHANNEL_ID for message-type quests
        is_general = (GENERAL_CHANNEL_ID is None) or (message.channel.id == GENERAL_CHANNEL_ID)
        if is_general:
            # legacy task
            self.game.update_messages(message.author.id, amount=1)
            # sidequest message counting
            # if sidequest active and user selected a messages quest, increase progress by 1
            if self.game.side_active:
                p = self.game.get_player(message.author.id)
                if p.side_selected:
                    q = SIDEQUEST_DEFS.get(p.side_selected)
                    if q and q["type"] == "messages" and time.time() <= (self.game.side_ends_at or float('inf')):
                        res = self.game.update_side_progress(message.author.id, 1)
                        if res and res.get("completed"):
                            # notify user/channel
                            try:
                                await message.channel.send(f"{message.author.mention} — вы выполнили сайд-квест и получили {res['reward']} 🎁")
                            except Exception:
                                pass
            await self._save_state()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        # ignore bots
        if payload.member and payload.member.bot:
            return
        if payload.guild_id is None:
            return
        if GUILD_ID and payload.guild_id != GUILD_ID:
            return

        # 1) Selection handling: if reaction is on side_message and side active -> interpret as selection
        if self.game.side_active and payload.message_id == self.game.side_message_id:
            # if emoji is number 1..8
            emoji_str = str(payload.emoji)
            if emoji_str in NUMBER_EMOJIS:
                selected_index = NUMBER_EMOJIS.index(emoji_str) + 1
                # set player's selection (allow change until end)
                p = self.game.get_player(payload.user_id)
                p.side_selected = selected_index
                p.side_progress = 0.0
                p.side_status = "in_progress"
                await self._save_state()
                # optional: notify user via DM (best effort)
                try:
                    user = self.bot.get_user(payload.user_id)
                    if user:
                        await user.send(f"Вы выбрали сайд-квест: {SIDEQUEST_DEFS[selected_index]['desc']}. У вас есть до {time.ctime(self.game.side_ends_at)}.")
                except Exception:
                    pass
            return

        # 2) Reaction counting for quests (including cats)
        # Check cats quest: custom by name or unicode (we check name match or string match)
        # update generic reactions quest (7) and cats quest (8)
        # For cats: if emoji name matches CATS_EMOJI_NAME (for custom), or string matches :Cats: or emoji char
        emoji_name = getattr(payload.emoji, "name", None)
        is_cats = False
        if emoji_name == CATS_EMOJI_NAME or str(payload.emoji) == f":{CATS_EMOJI_NAME}:" or str(payload.emoji) == CATS_EMOJI_NAME:
            is_cats = True

        # generic reaction increment (quest 7 counts any reaction)
        # Award progress only if sidequests are active, selection matches and within time
        if self.game.side_active and time.time() <= (self.game.side_ends_at or float('inf')):
            p = self.game.get_player(payload.user_id)
            if p.side_selected:
                q = SIDEQUEST_DEFS.get(p.side_selected)
                if q:
                    if q["type"] == "reactions":
                        res = self.game.update_side_progress(payload.user_id, 1)
                        if res and res.get("completed"):
                            # notify in guild text channel if possible
                            guild = self.bot.get_guild(payload.guild_id)
                            if guild:
                                for ch in guild.text_channels:
                                    if ch.permissions_for(guild.me).send_messages:
                                        try:
                                            await ch.send(f"<@{payload.user_id}> — вы выполнили сайд-квест и получили {res['reward']} 🎁")
                                        except Exception:
                                            pass
                                        break
                            await self._save_state()
                    elif q["type"] == "cats" and is_cats:
                        res = self.game.update_side_progress(payload.user_id, 1)
                        if res and res.get("completed"):
                            guild = self.bot.get_guild(payload.guild_id)
                            if guild:
                                for ch in guild.text_channels:
                                    if ch.permissions_for(guild.me).send_messages:
                                        try:
                                            await ch.send(f"<@{payload.user_id}> — вы выполнили сайд-квест и получили {res['reward']} 🎁")
                                        except Exception:
                                            pass
                                        break
                            await self._save_state()

        # legacy counting: if cats reaction, update legacy task too
        if is_cats:
            self.game.update_cats(payload.user_id, amount=1)
            await self._save_state()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if member.bot:
            return
        if member.guild is None:
            return
        if GUILD_ID and member.guild.id != GUILD_ID:
            return

        uid = member.id
        # join
        if before.channel is None and after.channel is not None:
            self._voice_joins[uid] = time.monotonic()
            return
        # leave
        if before.channel is not None and after.channel is None:
            joined_at = self._voice_joins.pop(uid, None)
            if not joined_at:
                return
            elapsed = time.monotonic() - joined_at
            # legacy update
            self.game.update_voice(uid, elapsed)
            # sidequest update if active & selected is voice-type & before deadline
            if self.game.side_active and time.time() <= (self.game.side_ends_at or float('inf')):
                p = self.game.get_player(uid)
                if p.side_selected:
                    q = SIDEQUEST_DEFS.get(p.side_selected)
                    if q and q["type"] == "voice":
                        res = self.game.update_side_progress(uid, elapsed)
                        if res and res.get("completed"):
                            # try notify in any text channel
                            guild = member.guild
                            for ch in guild.text_channels:
                                if ch.permissions_for(guild.me).send_messages:
                                    try:
                                        await ch.send(f"{member.mention} — вы выполнили сайд-квест и получили {res['reward']} 🎁")
                                    except Exception:
                                        pass
                                    break
            await self._save_state()
            return

    # ----- Admin commands -----
    @commands.command(name="sidequests_start", help="Запустить сайд-квесты (админ). / !sidequests_start [channel_id]")
    @commands.has_guild_permissions(administrator=True)
    @app_commands.guilds(config.GUILD)
    async def cmd_sidequests_start(self, ctx: commands.Context, channel: discord.TextChannel = None, days: int = 3):
        # choose channel
        channel = channel or (self.bot.get_channel(SIDEQUEST_CHANNEL_ID) if SIDEQUEST_CHANNEL_ID else ctx.channel)
        if channel is None:
            await ctx.reply("Канал не найден.", mention_author=False)
            return
        # create message with options
        lines = ["Сайд-квесты начались! Выберите одно задание реакцией (1️⃣–8️⃣). У вас есть {} дней.".format(days),
                 ""]
        for i in range(1, len(SIDEQUEST_DEFS)+1):
            lines.append(f"{i}. {SIDEQUEST_DEFS[i]['desc']} — награда: {SIDEQUEST_DEFS[i]['reward']} 🎁")
        msg = await channel.send("\n".join(lines))
        # add reactions 1..n
        for i in range(len(SIDEQUEST_DEFS)):
            try:
                await msg.add_reaction(NUMBER_EMOJIS[i])
            except Exception:
                pass
        # set game state
        start_ts = time.time()
        end_ts = start_ts + days*24*3600
        self.game.start_sidequests(start_ts, end_ts, channel.id, msg.id)
        self._schedule_side_end_checker()
        await self._save_state()
        await ctx.reply(f"Сайд-квесты запущены и будут доступны до {time.ctime(end_ts)} в {channel.mention}.", mention_author=False)

    @commands.command(name="sidequests_end", help="Принудительно завершить сайд-квесты (админ).")
    @commands.has_guild_permissions(administrator=True)
    @app_commands.guilds(config.GUILD)
    async def cmd_sidequests_end(self, ctx: commands.Context):
        if not self.game.side_active:
            await ctx.reply("Сайд-квесты не запущены.", mention_author=False)
            return
        # cancel watcher
        if self._side_task_handle and not self._side_task_handle.done():
            self._side_task_handle.cancel()
        await self._finalize_sidequests()
        await ctx.reply("Сайд-квесты завершены принудительно.", mention_author=False)

    @commands.command(name="sidequests_status", help="Показать статус сайдквеста игрока.")
    @app_commands.guilds(config.GUILD)
    async def cmd_sidequests_status(self, ctx: commands.Context, member: discord.Member = None):
        member = member or ctx.author
        p = self.game.get_player(member.id)
        lines = [f"Статус сайд-квеста для {member.mention}:"]
        if self.game.side_active:
            lines.append(f"- Событие активно до {time.ctime(self.game.side_ends_at)}")
        else:
            lines.append("- Событие не активно.")
        if p.side_selected:
            q = SIDEQUEST_DEFS.get(p.side_selected)
            lines.append(f"- Выбрано: {p.side_selected}. {q['desc']}")
            lines.append(f"- Прогресс: {int(p.side_progress)}/{q['required']}")
            lines.append(f"- Статус: {p.side_status}")
        else:
            lines.append("- Вы не выбрали сайд-квест.")
        lines.append(f"- Игрушек (накоплено): {p.ornaments}")
        await ctx.reply("\n".join(lines), mention_author=False)

    # legacy save/reset commands
    @app_commands.command(name="tasks_save")
    @commands.has_guild_permissions(administrator=True)
    @app_commands.guilds(config.GUILD)
    async def cmd_save(self, ctx: commands.Context):
        print("tester")
        await self._save_state()
        await ctx.reply("Состояние сохранено.", mention_author=False)

    @app_commands.command(name="tasks_reset")
    @commands.has_guild_permissions(administrator=True)
    @app_commands.guilds(config.GUILD)
    async def cmd_reset(self, ctx: commands.Context):
        self.game.reset_all()
        await self._save_state()
        await ctx.reply("Прогресс всех игроков сброшен.", mention_author=False)

    def cog_unload(self):
        try:
            asyncio.create_task(self._save_state())
        except Exception:
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(SidequestsCog(bot))
