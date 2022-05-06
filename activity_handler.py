from datetime import datetime
import hashlib
import os

import discord

DIRECTORY = os.path.realpath(os.path.dirname(__file__))
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
                today = datetime.now().strftime("%Y-%m-%d")
                encoded = today.encode()
                idx = int(hashlib.md5(encoded).hexdigest(), 16) % len(choices)
                args = choices[idx].split()
                return args[0], " ".join(args[1:])
        except:
            return "nothing interesting", "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

if __name__ == "__main__":
    print("You did it again, dummy!")