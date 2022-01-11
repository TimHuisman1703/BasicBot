import datetime
import os
import random
import re

import cv2
import discord
import numpy as np

DIRECTORY = "/".join(os.path.abspath(__file__).split("\\")[:-1])
FILE_TEMP_EMOJIS = DIRECTORY + "/data/database/em_temp_emojis.txt"

temp_emojis = dict()

class EmojiManager:
	def startup(client: discord.Client):
		EmojiManager.read_file_temp_emojis()

		EmojiManager.client = client

	async def process(message: discord.Message):
		args = message.content.split()[1:]

		channel = message.channel

		if len(args) == 0:
			await EmojiManager.send_help_message(channel)
			return
		
		if args[0].lower() in ["help", "?"]:
			await EmojiManager.send_help_message(channel)
			return
		if args[0].lower() in ["add", "create"]:
			await EmojiManager.add_emoji(message, False)
			return
		if args[0].lower() in ["temp"]:
			await EmojiManager.add_emoji(message, True)
			return
		if args[0].lower() in ["delete", "del", "remove"]:
			await EmojiManager.manually_delete_emoji(message)
			return
	
	async def add_emoji(message: discord.Message, temp: bool):
		args = message.content.split()[1:]
		guild = message.guild
		channel = message.channel

		attachments = message.attachments

		if len(message.attachments) == 0:
			await channel.send("Please send an image with your command.")
			return
		
		name = "emoji_" + str(random.randint(0, 9999999999)).zfill(10)
		if len(args) > 1 and len(args[1]) > 1:
			name = args[1]
		
		image = attachments[0]
		if image.content_type not in ["image/png", "image/jpeg", "image/gif"]:
			await channel.send("Please send a PNG or JPG.")
			return
		
		image_bytes = await image.read()
		
		if image.size > 256000:
			success = False

			if image.content_type in ["image/png", "image/jpeg"]:
				try:
					dim = (image.width, image.height)
					dim = (128 * dim[0] // max(dim), 128 * dim[1] // max(dim), )

					ext = ".png" if image.content_type == "image/png" else ".jpg"

					nparr = np.fromstring(image_bytes, np.uint8)
					image_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
					image_cv = cv2.resize(image_cv, dim, interpolation = cv2.INTER_AREA)
					success, nparr = cv2.imencode(ext, image_cv)
					
					if success:
						image_bytes = nparr.tobytes()
				except:
					pass
			
			if not success:
				await channel.send("This image is too big, please send a smaller image instead.")
				return

		emoji = None
		try:
			emoji = await guild.create_custom_emoji(name=name, image=image_bytes, reason=f"Requested by {message.author}")
		except:
			await channel.send("Something went wrong while trying to create the custom emoji...")
			return
		
		response = await channel.send(f"{emoji}")

		if response != None:
			await response.add_reaction(emoji)

		if temp:
			global temp_emojis

			tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
			tomorrow = tomorrow.strftime("%Y/%m/%d-%H:%M:%S")

			temp_emojis[f"{emoji.id}"] = tomorrow
			await EmojiManager.write_file_temp_emojis()
	
	async def manually_delete_emoji(message: discord.Message):
		args = message.content.split()[1:]
		guild = message.guild
		channel = message.channel

		if len(args) == 1:
			await EmojiManager.send_help_message(channel)
			return
		
		name = args[1]
		
		if re.match("<:.*:[0-9]{18}>", name):
			name = name.split(":")[1]

		emoji = discord.utils.find(lambda e: e.name == name, guild.emojis)

		if emoji == None:
			await channel.send("The emoji you wanted to delete doesn't seem to exist.")
			return

		try:
			await emoji.delete()
		except:
			await channel.send("Something went wrong...")
			return
		
		await channel.send(f"Deleted :{name}:")
	
	async def delete_outdated_emojis():
		now = datetime.datetime.today().strftime("%Y/%m/%d-%H:%M:%S")

		try:
			keys_to_pop = []
			
			for key, value in temp_emojis.items():
				if value < now:
					try:
						emoji = EmojiManager.client.get_emoji(int(key))
						await emoji.delete()

						keys_to_pop += [key]
					except:
						pass
			
			for key in keys_to_pop:
				temp_emojis.pop(key)
			
			await EmojiManager.write_file_temp_emojis()
		except:
			pass
	
	def read_file_temp_emojis():
		global temp_emojis

		try:
			with open(FILE_TEMP_EMOJIS, 'r') as f:
				strings = f.read().split("\n")

				for string in strings:
					key, value = string.split()
					temp_emojis[key] = value

				f.close()
		except:
			pass

	async def write_file_temp_emojis():
		global temp_emojis

		try:
			os.remove(FILE_TEMP_EMOJIS)
		except:
			pass

		with open(FILE_TEMP_EMOJIS, 'w') as f:
			strings = [f"{key} {value}" for key, value in temp_emojis.items()]

			f.write("\n".join(strings))
			f.close()
	
	async def send_help_message(channel: discord.abc.Messageable):
		strings = [
			"= DM Handler =",
			"",
			"* send [uid] [text]",
			"Sends a message to a user in DM.",
			"[uid] :: The ID of the user to DM.",
			"[text] :: The text to send.",
			"",
			"* send c[cid] [text]",
			"Sends a message to a channel.",
			"[cid] :: The ID of the channel to send to.",
			"[text] :: The text to send.",
			"",
			"* react [cid] [mid] [ename]",
			"Reacts to a message with an emoji.",
			"cid :: The ID of the channel the message is in.",
			"mid :: The ID of the message to react to.",
			"ename :: The name (or unicode character) of the emoji to react with.",
			"",
			"* unreact [cid] [mid] [ename]   <Removes a reaction from a message.>",
			"Removes a reaction from a message.",
			"cid :: The ID of the channel the message is in.",
			"mid :: The ID of the message to react to.",
			"ename :: The name (or unicode character) of the emoji to react with.",
		]

		strings = [
			"= Emoji Manager =",
			"",
			"* %em add [name] {image}",
			"Creates a new emoji.",
			"name :: The name of the emoji.",
			"image :: Attachment: The image to make an emoji from.",
			"",
			"* %em temp [name] {image}",
			"Creates a new temporary emoji (deleted in 24 hours).",
			"name :: The name of the emoji.",
			"image :: Attachment: The image to make an emoji from.",
			"",
			"* %em remove [name]",
			"Removes an emoji.",
			"name :: The name of the emoji."
		]

		await channel.send("```asciidoc\n" + "\n".join(strings) + "```")

if __name__ == "__main__":
	print("You did it again, dummy!")