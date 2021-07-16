import random

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

class RegularMessage:
	async def process(message):
		text = message.content.lower()

		for word in SPIDER_KEYWORDS:
			if word in text:
				await RegularMessage.send_spider_message(message)
				break
	
	async def send_spider_message(message):
		channel = message.channel
		response = rand_list(SPIDER_RESPONSES)

		await channel.send(response)

def rand_list(l):
	return l[random.randint(0, len(l)-1)]

if __name__ == "__main__":
	print("You did it again, dummy!")