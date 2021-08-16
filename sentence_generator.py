import os
import random

from io import TextIOWrapper
import requests, html
import codecs

MAX_ARTICLES = 50

DIRECTORY = "/".join(os.path.abspath(__file__).split("\\")[:-1])
FILE_SAMPLE = DIRECTORY + "/data/database/sg_sample_text.txt"

REPLACED_CHARS = [
	("\\r", ""),
	("\\n", ""),
]

START_SUBSTRING = "<div class=\"mw-parser-output\">"
END_SUBSTRING = "<noscript>"

SPECIAL_WIKI_PAGES = [
	"Category:",
	"Draft:",
	"File:",
	"Help:",
	"Image:",
	"MediaWiki:",
	"Module:",
	"Portal:",
	"Project",
	"Special:",
	"Talk:",
	"Template:",
	"TimedText:",
	"User:",
	"Wikipedia:",
	"WP:"
]

follow_up = None
start_words = []

def rand_list(l):
	return l[random.randint(0, len(l)-1)]

def filter_between(text: str, start_string: str, end_string: str, **kwargs) -> str:
	sep = kwargs["sep"] if "sep" in kwargs.keys() else ""
	limits = kwargs["limits"] if "limits" in kwargs.keys() else False
	extremes = kwargs["extremes"] if "extremes" in kwargs.keys() else False

	old_text = text
	new_text = []

	first_start = old_text.find(start_string)
	first_end = old_text.find(end_string)

	if first_end < first_start and extremes:
		new_text += old_text[:first_end]
	
	if first_start == -1 and first_end == -1:
		return old_text

	index = 0
	while index < len(old_text) and index > -1:
		index = old_text.find(start_string, index)
		if index == -1:
			break
		start = index + (not limits) * len(start_string)
		index += len(start_string)

		index = old_text.find(end_string, index)
		end = index + limits * len(end_string)
		if index == -1:
			if extremes:
				end = len(old_text)
			else:
				break
		else:
			index += len(end_string)

		new_text += [old_text[start:end]]

	return sep.join(new_text)

class SentenceGenerator:
	def startup(client):
		SentenceGenerator.client = client
	
	async def process(message):
		args = message.content.split()[1:]

		channel = message.channel

		if len(args) == 0:
			args = ["5"]
		
		min_size = 5
		
		if args[0].lower() in ["help", "?"]:
			await SentenceGenerator.send_help_message(channel)
			return
		elif args[0].lower() in ["forget", "reset", "delete"]:
			global follow_up, start_words
			del follow_up, start_words
			follow_up = start_words = None
			return
		elif "wiki/" in args[0]:
			await SentenceGenerator.generate_text_from_wiki(message)
			return
		
		try:
			min_size = int(args[0])
		except:
			pass

		await SentenceGenerator.send_random_sentence(message, min_size)
	
	async def learn_to_speak():
		global follow_up, start_words

		del follow_up, start_words
		follow_up = start_words = None

		sample = ""
		try:
			with codecs.open(FILE_SAMPLE, encoding="utf-8") as f:
				for line in f:
					sample += repr(line) + " "
		except:
			return False

		words = sample.strip().split()
		follow_up = dict()
		start_words = []
		for i in range(len(words)):
			if words[i] not in follow_up.keys():
				follow_up.update({words[i]: []})
			if i < len(words) - 1:
				follow_up[words[i]] += [words[i+1]]
				if words[i][-1] == ".":
					start_words += [words[i+1]]
		
		return True
	
	async def wiki_scrape(topic: str, file: TextIOWrapper, depth: int = 0, width: int = 0):
		r = requests.get(f"https://en.wikipedia.org/wiki/{topic}")
		if r.status_code != 200:
			return
		raw_text = html.unescape(r.text)

		# Filter main page
		start = raw_text.find("/table>", raw_text.find(START_SUBSTRING))
		end = raw_text.find(END_SUBSTRING)
		if start == -1 or end == -1:
			return
		raw_text = raw_text[start:end]

		# Remove non-readable text
		text = filter_between(raw_text, "<p>", "</p>", sep="\n", limits=True)
		text = filter_between(text, "/style>", "<style", extremes=True)
		text = filter_between(text, ">", "<")
		text = filter_between(text, "]", "[", extremes=True)

		# Remove double whitespaces
		text = text.replace("\n", " ")
		while "  " in text:
			text = text.replace("  ", " ")
		text = text.strip()

		file.write(text)

		links = filter_between(raw_text, "<a href=\"/wiki/", "\"", sep="\n").split("\n")

		valid_links = []
		for link in links:
			if link in valid_links or link == "":
				continue

			valid = True
			for namespace in SPECIAL_WIKI_PAGES:
				if link.startswith(namespace) or link.startswith(namespace[:-1] + "_talk:"):
					valid = False
					break
			
			if valid:
				valid_links += [link]
		
		if depth > 0:
			children = min(width, len(valid_links))
			for _ in range(children):
				child = rand_list(valid_links)
				valid_links.remove(child)
				
				print(f"Reading: https://en.wikipedia.org/wiki/{child} (from \"{topic}\")")
				
				await SentenceGenerator.wiki_scrape(child, file, depth-1, width)
	
	async def generate_text_from_wiki(message):
		args = message.content.split()[1:]
		url_path = args[0].split("/")
		
		depth = 2
		width = 4

		try:
			if len(args) > 1:
				depth = int(args[1])

				if len(args) > 2:
					width = int(args[2])
				else:
					width = MAX_ARTICLES - 1
		except:
			pass
		
		while (1 - width ** (depth + 1)) // (1 - width) > MAX_ARTICLES:
			width -= 1
		
		await message.add_reaction("⌛")

		if len(url_path) < 2 or url_path[-2] != "wiki":
			return
		
		topic = url_path[-1]
		
		try:
			with open(FILE_SAMPLE, "w", encoding="utf-8") as file:
				print(f"Reading: https://en.wikipedia.org/wiki/{topic}")
				await SentenceGenerator.wiki_scrape(topic, file, depth, width)
			
			await SentenceGenerator.learn_to_speak()
		except:
			await message.add_reaction("⚠️")
		else:
			await message.add_reaction("✅")
		
		await message.remove_reaction("⌛", SentenceGenerator.client.user)

	async def send_help_message(channel):
		strings = [
			"= Sentence Generator =",
			"",
			"* %sg",
			"Generates a random sentence.",
			"",
			"* %sg [min-size]",
			"Generates a random sentence of a minimum size.",
			"min-size :: The minimum word count.",
			"",
			"* %sg [wiki-link] <[depth]> <[width]>",
			"Learns how to speak using WikiPedia.",
			"wiki-link :: The link to the WikiPedia article.",
			"depth :: The maximum recursion depth (0 = no recursion).",
			"width :: The amount of recursions done from a page.",
			"",
			"* %sg reset",
			"Clears up RAM (head empty, no thought)."
		]

		await channel.send("```asciidoc\n" + "\n".join(strings) + "```")
	
	async def send_random_sentence(message, min_size):
		global follow_up, start_words

		if follow_up == None or start_words == None:
			if not await SentenceGenerator.learn_to_speak():
				return
		
		result = ""
		current = rand_list(start_words)
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

if __name__ == "__main__":
	print("You did it again, dummy!")