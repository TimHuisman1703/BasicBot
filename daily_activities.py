from datetime import datetime
import os
import random
import requests

import discord

DIRECTORY = os.path.realpath(os.path.dirname(__file__))
FILE_LAST_BOOTED_UP = DIRECTORY + "/data/database/da_last_booted_up.txt"
FILE_XKCD_CHANNEL = DIRECTORY + "/data/database/da_xkcd_channel.txt"

class DailyActivities:
    async def check(client: discord.Client):
        file = open(FILE_LAST_BOOTED_UP)
        last_booted_up = file.read()
        file.close()

        today = datetime.now().strftime("%Y-%m-%d")

        if last_booted_up != today:
            file = open(FILE_LAST_BOOTED_UP, "w")
            file.write(today)
            file.close()

            await DailyActivities.send_daily_xkcd(client)
    
    async def send_daily_xkcd(client: discord.Client):
        r = requests.get("https://xkcd.com/")
        html = r.content.__str__()

        start = html.index("Permanent link to this comic:")
        start = html.index("https://xkcd.com/", start)
        end = html.index("\"", start + 1)
        page_amount = int(html[start + 17:end])

        page_nr = random.randint(1, page_amount)

        file = open(FILE_XKCD_CHANNEL)
        for channel_id in file.read().strip().split("\n"):
            channel = await client.fetch_channel(int(channel_id))
            await channel.send(f"https://xkcd.com/{page_nr}/")
        file.close()

if __name__ == "__main__":
    print("You did it again, dummy!")