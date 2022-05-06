import random

import discord

SPIDER_KEYWORDS = [
    "spider",
    "spidur",
    "spidey",
]
SPIDER_RESPONSES = [
    "What?! A spider?!",
    "Eeeeeeek!!! Where?!?!",
    "Kill the spider!! Kill it!!",
    "Where's the spider?!",
    "There's a spider?!",
    "A spider?! HERE?!",
    "A spider?! We're gonna DIE!!!",
    "Kill that 8-legged demon!!",
    "DIIIIIIIIEEEEEEEE!!!!!!!!"
]

class MessageResponder:
    async def process(message: discord.Message):
        text = message.content.lower()

        for word in SPIDER_KEYWORDS:
            if word in text:
                await MessageResponder.send_spider_message(message)
                break
    
    async def send_spider_message(message: discord.Message):
        channel = message.channel
        response = rand_list(SPIDER_RESPONSES)

        await channel.send(response)

def rand_list(l: list):
    return l[random.randint(0, len(l)-1)]

if __name__ == "__main__":
    print("You did it again, dummy!")