import os

import random
import codecs

DIRECTORY = "/".join(os.path.abspath(__file__).split("\\")[:-1])
FILE_SAMPLE = DIRECTORY + "/data/sample_texts/sg_sample_personal.txt"

REPLACED_CHARS = [
	("\\r", ""),
	("\\n", ""),
]

follow_up = None

def rand_list(l):
	i = random.randint(0, len(l)-1)
	return l[i]

class SentenceGenerator:
	async def process(message):
		args = message.content.split()[1:]

		channel = message.channel

		if len(args) == 0:
			args = ["5"]
		
		min_size = 5
		
		if args[0].lower() in ["help", "?"]:
			await SentenceGenerator.send_help_message(channel)
			return
		if args[0].lower() in ["forget", "reset", "delete"]:
			global follow_up
			del follow_up
			follow_up = None
			return
		
		try:
			min_size = int(args[0])
		except:
			pass

		await SentenceGenerator.send_random_sentence(message, min_size)
	
	async def send_random_sentence(message, min_size):
		global follow_up

		if follow_up == None:
			sample = ""
			with codecs.open(FILE_SAMPLE, encoding="utf-8") as f:
				for line in f:
					sample += repr(line) + " "
			
			for char in REPLACED_CHARS:
				sample = sample.replace(char[0], char[1])
			while "  " in sample:
				sample = sample.replace("  ", " ")

			words = sample.strip().split()
			follow_up = dict()
			for i in range(len(words)):
				if words[i] not in follow_up.keys():
					follow_up.update({words[i]: []})
				if i < len(words) - 1:
					follow_up[words[i]] += [words[i+1]]
		
		result = ""
		current = rand_list(["I", "You", "He", "She", "They", "A", "The"])
		i = 0

		while 1:
			result += current + " "
			i += 1


			if i >= min_size and not current[-1].isalnum():
				break

			if len(result) > 1900:
				result += "..."
				break

			if current not in follow_up.keys():
				break
			
			if not follow_up[current]:
				break
			else:
				current = rand_list(follow_up[current])
		
		await message.channel.send(result)

	async def send_help_message(channel):
		strings = [
			"# Sentence Generator",
			"",
			"* %sg                       <Generates a random sentence.>",
			"* %sg [min-size]            <Generates a random sentence of at least [min-size] words.>",
		]

		await channel.send("```md\n" + "\n".join(strings) + "```")

if __name__ == "__main__":
	print("You did it again, dummy!")