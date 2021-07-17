import os
from datetime import datetime

import discord

DIRECTORY = "/".join(os.path.abspath(__file__).split("\\")[:-1])
FILE_LAST_SENT = DIRECTORY + "/data/database/gm_last_sent.txt"
FILE_DAILY_CHANNEL = DIRECTORY + "/data/database/gm_daily_channel.txt"

last_sent = {}
daily_channel = {}

class GoodMorning:
	def startup(client):
		GoodMorning.client = client

		GoodMorning.read_file_daily_channel()
		GoodMorning.read_file_last_sent()

	async def check_good_morning(search_guild=None):
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

					await GoodMorning.create_message(channel, user.display_name)

					last_sent.update({key: today})
		
		await GoodMorning.write_file_last_sent()

	async def process(message):
		args = message.content.split()[1:]

		channel = message.channel

		if len(args) == 0:
			user = message.author.display_name
			await GoodMorning.create_message(channel, user)
			return
		
		if args[0].lower() in ["help", "?"]:
			await GoodMorning.send_help_message(channel)
			return

		if args[0].lower() in ["join"]:
			await GoodMorning.join_user(message)
			return

		if args[0].lower() in ["leave"]:
			await GoodMorning.leave_user(message)
			return

		if args[0].lower() in ["here"]:
			await GoodMorning.set_channel(message)
			return

		if args[0].lower() in ["nowhere"]:
			await GoodMorning.reset_channel(message)
			return

		if args[0].lower() in ["to"]:
			user = " ".join(args[1:])
			await GoodMorning.create_message(channel, user)
			return

	async def join_user(message):
		print(f"{message.author} in {message.guild} joined")

		key = f"{message.guild.id}-{message.author.id}"
		value = datetime.today().strftime("%Y-%m-%d")

		if key in last_sent:
			await message.channel.send("You are already receiving daily good mornings.")
		else:
			last_sent.update({key: value})
			await message.channel.send("You will now receive daily good mornings!")

		await GoodMorning.write_file_last_sent()

	async def leave_user(message):
		print(f"{message.author} in {message.guild} left")

		key = f"{message.guild.id}-{message.author.id}"

		if key in last_sent:
			last_sent.pop(key)
			await message.channel.send("You will no longer receive daily good mornings.")
		else:
			await message.channel.send("You are currently not receiving daily good mornings.")

		await GoodMorning.write_file_last_sent()

	async def set_channel(message):
		print(f"Channel in {message.guild} set to {message.channel}")

		key = f"{message.guild.id}"
		value = f"{message.channel.id}"
		daily_channel.update({key: value})

		await message.channel.send("Daily good mornings will now be sent here!")

		await GoodMorning.write_file_daily_channel()
	
	async def reset_channel(message):
		print(f"Channel in {message.guild} reset")

		key = f"{message.guild.id}"
		daily_channel.pop(key)

		await message.channel.send("Reset daily good mornings.")

		await GoodMorning.write_file_daily_channel()

	async def create_message(channel, user):
		await channel.send(f"Good morning, {user}!")

	def read_file_daily_channel():
		global daily_channel

		try:
			with open(FILE_DAILY_CHANNEL, 'r') as f:
				strings = f.read().split("\n")

				for string in strings:
					key, value = string.split()
					daily_channel.update({key: value})

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

	def read_file_last_sent():
		global last_sent

		try:
			with open(FILE_LAST_SENT, 'r') as f:
				strings = f.read().split("\n")

				for string in strings:
					key, value = string.split()
					last_sent.update({key: value})

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

	async def send_help_message(channel):
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
			"* %gm here",
			"Selects the current channel for daily messages."
			"",
			"* %gm nowhere",
			"Disables daily messages.",
			"",
			"* %gm to [name]",
			"Wishes someone a good morning.",
			"name :: The person to wish a good morning to."
		]

		await channel.send("```asciidoc\n" + "\n".join(strings) + "```")

if __name__ == "__main__":
	print("You did it again, dummy!")