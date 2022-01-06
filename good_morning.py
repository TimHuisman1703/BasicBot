import os
from datetime import datetime

import discord

DIRECTORY = "/".join(os.path.abspath(__file__).split("\\")[:-1])
FILE_LAST_SENT = DIRECTORY + "/data/database/gm_last_sent.txt"
FILE_DAILY_CHANNEL = DIRECTORY + "/data/database/gm_daily_channel.txt"
FILE_USER_PHRASE = DIRECTORY + "/data/database/gm_user_phrase.txt"
FILE_EVENT_LOG = DIRECTORY + "/data/database/gm_event_log.txt"

STANDARD_PHRASE = "Good morning, <NAME>!"

last_sent = {}
daily_channel = {}
user_phrase = {}
event_log = {}

class GoodMorning:
	def startup(client: discord.Client):
		GoodMorning.client = client

		GoodMorning.read_file_last_sent()
		GoodMorning.read_file_daily_channel()
		GoodMorning.read_file_user_phrase()
		GoodMorning.read_file_event_log()

	async def check_good_morning(search_guild: discord.Guild = None, search_user: discord.User = None):
		global last_sent

		now = datetime.today()

		if now.hour < 6 or now.hour >= 18:
			return

		today = now.strftime("%Y-%m-%d")

		for key, value in last_sent.items():
			if value < today:
				guild_id, user_id = key.split("-")

				if search_guild != None and str(search_guild.id) != guild_id:
					continue
				
				if search_user != None and str(search_user.id) != user_id:
					continue

				if guild_id in daily_channel.keys():
					guild = search_guild
					if guild == None:
						guild = GoodMorning.client.get_guild(int(guild_id))
					
					channel_id = daily_channel[guild_id]
					channel = await GoodMorning.client.fetch_channel(int(channel_id))
					
					user = discord.utils.find(lambda m: m.id == int(user_id), guild.members)

					if user == None:
						continue
					if user.status != discord.Status.online:
						continue

					await GoodMorning.create_message(channel, guild, user)

					last_sent[key] = today
					if key not in event_log:
						event_log[key] = []
					event_log[key].append(now)
		
		await GoodMorning.write_file_last_sent()
		await GoodMorning.write_file_event_log()

	async def process(message: discord.Message):
		args = message.content.split()[1:]

		channel = message.channel

		if len(args) == 0:
			guild = message.guild
			user = message.author
			await GoodMorning.create_message(channel, guild, user)
		elif args[0].lower() in ["help", "?"]:
			await GoodMorning.send_help_message(channel)
		elif args[0].lower() in ["join"]:
			await GoodMorning.join_user(message)
		elif args[0].lower() in ["leave"]:
			await GoodMorning.leave_user(message)
		elif args[0].lower() in ["phrase"]:
			await GoodMorning.update_phrase(message)
		elif args[0].lower() in ["here"]:
			await GoodMorning.set_channel(message)
		elif args[0].lower() in ["nowhere"]:
			await GoodMorning.reset_channel(message)
		elif args[0].lower() in ["to"]:
			user = " ".join(args[1:])
			await GoodMorning.send_message(channel, STANDARD_PHRASE, user)
		elif args[0].lower() in ["stats"]:
			await GoodMorning.share_stats(message)

	async def join_user(message: discord.Message):
		print(f"{message.author} in {message.guild} joined")

		key = f"{message.guild.id}-{message.author.id}"
		value = datetime.today().strftime("%Y-%m-%d")

		if key in last_sent:
			await message.channel.send("You are already receiving daily good mornings.")
		else:
			last_sent[key] = value
			await message.channel.send("You will now receive daily good mornings!")

		await GoodMorning.write_file_last_sent()

	async def leave_user(message: discord.Message):
		print(f"{message.author} in {message.guild} left")

		key = f"{message.guild.id}-{message.author.id}"

		if key in last_sent:
			last_sent.pop(key)
			await message.channel.send("You will no longer receive daily good mornings.")
		else:
			await message.channel.send("You are currently not receiving daily good mornings.")

		await GoodMorning.write_file_last_sent()
	
	async def update_phrase(message: discord.Message):
		key = f"{message.guild.id}-{message.author.id}"
		phrase = " ".join(message.content.split()[2:])

		user_phrase[key] = phrase

		await message.channel.send(f"From now on I'll greet you with \"{phrase.replace('<NAME>', message.author.display_name)}\"")

		print(f"{message.author} in {message.guild} updated phrase to \"{phrase}\"")

		await GoodMorning.write_file_user_phrase()

	async def set_channel(message: discord.Message):
		print(f"Channel in {message.guild} set to {message.channel}")

		key = f"{message.guild.id}"
		value = f"{message.channel.id}"
		daily_channel[key] = value

		await message.channel.send("Daily good mornings will now be sent here!")

		await GoodMorning.write_file_daily_channel()
	
	async def reset_channel(message: discord.Message):
		print(f"Channel in {message.guild} reset")

		key = f"{message.guild.id}"
		daily_channel.pop(key)

		await message.channel.send("Reset daily good mornings.")

		await GoodMorning.write_file_daily_channel()

	async def create_message(channel: discord.abc.Messageable, guild: discord.Guild, user: discord.User):
		key = f"{guild.id}-{user.id}"

		phrase = STANDARD_PHRASE
		if key in user_phrase:
			phrase = user_phrase[key]
		
		await GoodMorning.send_message(channel, phrase, user.display_name)
		
	async def send_message(channel: discord.abc.Messageable, phrase: str, username: str):
		await channel.send(phrase.replace("<NAME>", username))
	
	async def share_stats(message: discord.Message):
		channel = message.channel
		key = f"{message.guild.id}-{message.author.id}"
		name = message.author.display_name

		string = f"# {name}'s Statistics\n"

		if key in event_log:
			total = len(event_log[key])
			string += f"\n- Times woken up:         {total}"

			if total:
				average = sum(3600 * t.hour + 60 * t.minute + t.second for t in event_log[key]) // total
				h, m, s = average // 3600, average // 60 % 60, average % 60
				string += f"\n- Usually wakes up at:    {h:02}:{m:02}:{s:02}"

				dates = sorted(event_log[key], key=lambda x: 3600 * x.hour + 60 * x.minute + x.second)
				string += f"\n- Earliest wake-up time:  " + dates[0].strftime("%H:%M:%S on %d-%m-%Y")
				string += f"\n- Latest wake-up time:    " + dates[-1].strftime("%H:%M:%S on %d-%m-%Y")
		else:
			string += "\nAbsolutely nothing..."

		await channel.send("```md\n" + string + "```")

	def read_file_last_sent():
		global last_sent

		try:
			with open(FILE_LAST_SENT, 'r') as f:
				strings = f.read().split("\n")

				for string in strings:
					key, value = string.split()
					last_sent[key] = value

				f.close()
		except:
			pass

	async def write_file_last_sent():
		global last_sent

		try:
			os.remove(FILE_LAST_SENT)
		except:
			pass

		with open(FILE_LAST_SENT, 'w') as f:
			strings = [f"{key} {value}" for key, value in last_sent.items()]

			f.write("\n".join(strings))
			f.close()

	def read_file_daily_channel():
		global daily_channel

		try:
			with open(FILE_DAILY_CHANNEL, 'r') as f:
				strings = f.read().split("\n")

				for string in strings:
					key, value = string.split()
					daily_channel[key] = value

				f.close()
		except:
			pass

	async def write_file_daily_channel():
		global daily_channel

		try:
			os.remove(FILE_DAILY_CHANNEL)
		except:
			pass

		with open(FILE_DAILY_CHANNEL, 'w') as f:
			strings = [f"{key} {value}" for key, value in daily_channel.items()]

			f.write("\n".join(strings))
			f.close()

	def read_file_user_phrase():
		global user_phrase

		try:
			with open(FILE_USER_PHRASE, 'r', encoding="utf8") as f:
				strings = f.read().split("\n")

				for string in strings:
					args = string.split()
					user_phrase[args[0]] = " ".join(args[1:])

				f.close()
		except:
			pass

	async def write_file_user_phrase():
		global user_phrase

		try:
			os.remove(FILE_USER_PHRASE)
		except:
			pass

		with open(FILE_USER_PHRASE, 'w', encoding="utf8") as f:
			strings = [f"{key} {value}" for key, value in user_phrase.items()]

			f.write("\n".join(strings))
			f.close()

	def read_file_event_log():
		global event_log

		try:
			with open(FILE_EVENT_LOG, 'r') as f:
				strings = f.read().split("\n\n")
				
				for string in strings:
					args = string.split("\n")
					key = args[0]

					event_log[key] = []
					for value in args[1:]:
						time = datetime(*[int(j) for j in value.split()])
						event_log[key].append(time)

				f.close()
		except:
			pass

	async def write_file_event_log():
		global event_log

		try:
			os.remove(FILE_EVENT_LOG)
		except:
			pass

		with open(FILE_EVENT_LOG, 'w') as f:
			strings = []
			for key in event_log:
				string = key
				for time in event_log[key]:
					string += "\n" + time.strftime("%Y %m %d %H %M %S")
				strings.append(string)

			f.write("\n\n".join(strings))
			f.close()

	async def send_help_message(channel: discord.abc.Messageable):
		strings = [
			"= Good Morning =",
			"",
			"* %gm",
			"Offers an instant good morning.",
			"",
			"* %gm join",
			"Sends the user a good morning everyday.",
			"",
			"* %gm leave",
			"Stops sending the user a daily good morning.",
			"",
			"* %gm phrase [phrase]",
			"Changes the good morning phrase of the user.",
			"phrase :: The phrase to say. \"<NAME>\" will be replaced with your username.",
			"",
			"* %gm here",
			"Selects the current channel for daily messages.",
			"",
			"* %gm nowhere",
			"Disables daily messages.",
			"",
			"* %gm to [name]",
			"Wishes someone a good morning.",
			"name :: The person to wish a good morning to.",
			"",
			"* %gm stats",
			"Shares the Good Morning-statistics of the user."
		]

		await channel.send("```asciidoc\n" + "\n".join(strings) + "```")

if __name__ == "__main__":
	print("You did it again, dummy!")