import random
import os

import discord

DIRECTORY = "/".join(os.path.abspath(__file__).split("\\")[:-1])
FILE_MUSIC_LIST = DIRECTORY + "/data/database/ah_music_list.txt"

class ActivityHandler:
	async def prepare_activity() -> discord.Activity:
		url, name = await ActivityHandler.pick_song()

		activity = discord.Streaming(
			url=url,
			name=name
		)

		return activity

	async def pick_song():
		try:
			with open(FILE_MUSIC_LIST, 'r', encoding="utf8") as f:
				choices = f.read().split("\n")
				args = rand_list(choices).split()
				return args[0], " ".join(args[1:])
		except:
			return "nothing interesting", "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

def rand_list(l: list):
	return l[random.randint(0, len(l)-1)]

if __name__ == "__main__":
	print("You did it again, dummy!")