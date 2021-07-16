import os
from dotenv import load_dotenv

import discord

load_dotenv()
AUTHOR_ID = int(os.getenv("AUTHOR_ID"))
AUTHOR = None

class DMHandler:
	async def startup(client):
		global AUTHOR

		DMHandler.client = client
		AUTHOR = client.get_user(AUTHOR_ID)

	async def process(message):
		if message.author.id == AUTHOR_ID:
			await DMHandler.process_author(message)
		else:
			try:
				text = f"**{message.author} said:**\n{message.content}\n*{message.author.id}*"
				channel = await AUTHOR.create_dm()
				await channel.send(text)
			except:
				pass
	
	async def process_author(message):
			try:
				text = message.content.split()
				command, text = text[0], text[1:]

				if command == "send":
					channel_id, text = text[0], " ".join(text[1:])

					channel = None
					if channel_id[0] != "c":
						channel_id = int(channel_id)
						user = DMHandler.client.get_user(channel_id)
						if user == None:
							raise Exception()
						channel = await user.create_dm()
					else:
						channel_id = int(channel_id[1:])
						channel = DMHandler.client.get_channel(channel_id)
					
					await channel.send(text)
					await message.add_reaction("✅")
				elif command in ["react", "unreact"]:
					channel_id, message_id, emoji = int(text[0]), int(text[1]), text[2]
					channel = DMHandler.client.get_channel(channel_id)
					react_message = await channel.fetch_message(message_id)

					try:
						if command == "react":
							await react_message.add_reaction(emoji)
						else:
							await react_message.remove_reaction(emoji, DMHandler.client.user)
						
						await message.add_reaction("✅")
						return
					except:
						pass

					emoji = discord.utils.find(lambda e: e.name == emoji, channel.guild.emojis)

					if command == "react":
						await react_message.add_reaction(emoji)
					else:
						await react_message.remove_reaction(emoji, DMHandler.client.user)
					
					await message.add_reaction("✅")
				elif command == "help":
					channel = await AUTHOR.create_dm()
					await DMHandler.send_help_message(channel)
			except:
				try:
					channel = await AUTHOR.create_dm()
					await channel.send("Something went wrong.")
				except:
					pass
	
	async def send_help_message(channel):
		strings = [
			"# DM Handler",
			"",
			"* send [uid] [text]             <Sends a message to a user in DM.>",
			"* send c[cid] [text]            <Sends a message to a channel.>",
			"* react [cid] [mid] [ename]     <Reacts to a message with an emoji.>",
			"* unreact [cid] [mid] [ename]   <Removes a reaction from a message.>",
		]

		await channel.send("```md\n" + "\n".join(strings) + "```")

if __name__ == "__main__":
	print("You did it again, dummy!")