import discord
from dotenv import load_dotenv
import os

from activity_handler import ActivityHandler
from daily_activities import DailyActivities
from dm_handler import DMHandler
from emoji_manager import EmojiManager
from good_morning import GoodMorning
from message_responder import MessageResponder
from minesweeper import Minesweeper
from sentence_generator import SentenceGenerator
from voice_handler import VoiceHandler

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

PREFIX = [
    "%"
]

client = discord.Client(intents=discord.Intents.all())

DIRECTORY = os.path.realpath(os.path.dirname(__file__))
if not os.path.exists(DIRECTORY + "/data/database"):
    os.mkdir(DIRECTORY + "/data/database")

@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord!\n\n-----\n")

    activity = await ActivityHandler.prepare_activity()
    await client.change_presence(status=discord.Status.online, activity=activity)

    await DailyActivities.check(client)

    await GoodMorning.check_good_morning()
    await EmojiManager.delete_outdated_emojis()
    await DMHandler.startup(client)
    await VoiceHandler.startup(client)

@client.event
async def on_message(message: discord.Message):
    global busy

    if message.author.bot:
        return
    
    if type(message.channel) == discord.channel.DMChannel:
        await DMHandler.process(message)
        return
    
    text = message.content

    for prefix in PREFIX:
        if text.startswith(prefix):
            text = text[len(prefix):]
            break
    else:
        await MessageResponder.process(message)
        return

    if message.channel.id in busy:
        return
    
    command = text.split()[0].lower()

    busy.add(message.channel.id)
    
    if command in ["ping"]:
        await send_ping(message.channel)
    if command in ["help", "?"]:
        await send_help_message(message.channel)
    if command in ["ms"]:
        await Minesweeper.process(message)
    if command in ["gm"]:
        await GoodMorning.process(message)
    if command in ["em"]:
        await EmojiManager.process(message)
    if command in ["sg"]:
        await SentenceGenerator.process(message)
    if command in ["vc"]:
        await VoiceHandler.process(message)
    
    busy.remove(message.channel.id)

saying_good_morning = set()

@client.event
async def on_member_update(before: discord.Member, after: discord.Member):
    if str(before.status) not in ["online", "idle"]:
        if str(after.status) in ["online", "idle"]:
            if after.guild not in saying_good_morning:
                saying_good_morning.add(after.guild)
                await GoodMorning.check_good_morning(after.guild, after)
                saying_good_morning.remove(after.guild)
    
    await EmojiManager.delete_outdated_emojis()

async def send_ping(channel: discord.abc.Messageable):
    await channel.send(f"`Ping: {round(1000 * client.latency)}ms`")

async def send_help_message(channel: discord.abc.Messageable):
    strings = [
        "#==============#",
        "#   BasicBot   #",
        "#==============#",
        "",
        "[Minesweeper][1]",
        "<Generates a game of Minesweeper.>",
        "* %ms help",
        "",
        "[Good Morning][2]",
        "<Wishes you a good morning.>",
        "* %gm help",
        "",
        "[Emoji Manager][3]",
        "<Manages emojis.>",
        "* %em help",
        "",
        "[Sentence Generator][4]",
        "<Generates a random sentence.>",
        "* %sg help",
        "",
        "[Voice Channel][5]",
        "<Handles Voice Channel interactions.>",
        "* %vc help",
    ]

    await channel.send("```md\n" + "\n".join(strings) + "```")

busy = set()

GoodMorning.startup(client)
EmojiManager.startup(client)
SentenceGenerator.startup(client)

client.run(TOKEN)