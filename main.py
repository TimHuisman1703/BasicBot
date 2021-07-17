import os
from regular_message import RegularMessage

import discord
from dotenv import load_dotenv

from dm_handler import DMHandler
from emoji_manager import EmojiManager
from good_morning import GoodMorning
from minesweeper import Minesweeper
from sentence_generator import SentenceGenerator
from voice_handler import VoiceHandler
from regular_message import RegularMessage

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

PREFIX = [
	"%"
]

client = discord.Client(intents=discord.Intents.all())

DIRECTORY = "/".join(os.path.abspath(__file__).split("\\")[:-1])
if not os.path.exists(DIRECTORY + "/data/database"):
	os.mkdir(DIRECTORY + "/data/database")

@client.event
async def on_ready():
	print(f"{client.user} has connected to Discord!\n\n-----\n")

	activity = discord.Streaming(
		name="Undertale",
		url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
	)
	await client.change_presence(status=discord.Status.online, activity=activity)

	await GoodMorning.check_good_morning()
	await EmojiManager.delete_outdated_emojis()
	await DMHandler.startup(client)
	await VoiceHandler.startup(client)

@client.event
async def on_message(message):
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
		await RegularMessage.process(message)
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

@client.event
async def on_member_update(before, after):
	if str(before.status) != "online":
		if str(after.status) == "online":
			print(f"{after.name} is now online")
			await GoodMorning.check_good_morning(after.guild)
	
	await EmojiManager.delete_outdated_emojis()

async def send_ping(channel):
	await channel.send(f"`Ping: {round(1000 * client.latency)}ms`")

async def send_help_message(channel):
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