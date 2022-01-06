import random
import re

import discord

TILE_CHARACTERS = "🅱️ 🟦 1️⃣ 2️⃣ 3️⃣ 4️⃣ 5️⃣ 6️⃣ 7️⃣ 8️⃣".split()

class Minesweeper:
	async def process(message: discord.Message):
		width = height = 10
		bomb_ratio = 0.15

		args = message.content.lower().split()[1:]

		for arg in args:
			if re.match("[0-9]+x[0-9]+", arg):
				new_width, new_height = [int(j) for j in arg.split("x")]
				
				if new_width >= 1 and new_width <= 40:
					width = new_width
				
				if new_height >= 1 and new_height <= 40:
					height = new_height
			
			if re.match("[0-9]+:[0-9]+", arg):
				num, denom = [int(j) for j in arg.split(":")]
				
				if num <= denom and num >= 0 and denom > 0:
					bomb_ratio = num / denom
			
			try:
				new_bomb_ratio = float(arg)
				if new_bomb_ratio >= 0 and new_bomb_ratio <= 1:
					bomb_ratio = new_bomb_ratio
			except:
				pass
			
			if arg in ["help", "?"]:
				await Minesweeper.send_help_message(message.channel)
				return

		bombs = int(width * height * bomb_ratio)
		grid = Minesweeper.generate(width, height, bombs)

		await Minesweeper.create_message(message.channel, grid)
	
	def generate(width: int, height: int, bombs: int) -> "list[list[int]]":
		removing = bombs * 2 > width * height

		# -1:	Bomb
		# 0-8:	Neighbor bomb count
		grid = [[-int(removing) for ix in range(width)] for iy in range(height)]

		c = width * height * removing
		while c != bombs:
			x, y = random.randint(0, width - 1), random.randint(0, height - 1)

			if removing:
				if grid[y][x] == -1:
					grid[y][x] = 0
					c -= 1
			else:
				if grid[y][x] != -1:
					grid[y][x] = -1
					c += 1
		
		for iy in range(height):
			for ix in range(width):
				if grid[iy][ix] == -1:
					continue

				for cy in range(iy-1, iy+2):
					if cy < 0 or cy > height-1:
						continue
					
					for cx in range(ix-1, ix+2):
						if cx < 0 or cx > width-1:
							continue
						
						grid[iy][ix] += int(grid[cy][cx] == -1)
		
		return grid
	
	async def create_message(channel: discord.abc.Messageable, grid: "list[list[int]]"):
		bombs = sum(sum(int(tile == -1) for tile in row) for row in grid)
		await channel.send(f"Generating field... ({len(grid[0])}x{len(grid)}, {bombs} bomb"
			+ "s"*int(bombs != 1) + ")\n" + ("⬜ "*(len(grid[0]) + 2))[:-1])

		for iy in range(len(grid)):
			await channel.send("⬜ " + " ".join(f"||{TILE_CHARACTERS[tile+1]}||" for tile in grid[iy]) + " ⬜")
		await channel.send(("⬜ ​"*(len(grid[0]) + 2))[:-1])
	
	async def send_help_message(channel: discord.abc.Messageable):
		strings = [
			"= Minesweeper =",
			"",
			"* %ms <[w]x[h]> <[a:b]>",
			"Creates a field of a certain size and with a certain bomb ratio.",
			"w :: The width of the field.",
			"h :: The height of the field.",
			"a:b :: The ratio of bombs to tiles (0 <= a <= b, 0 < b)."
		]

		await channel.send("```asciidoc\n" + "\n".join(strings) + "```")

if __name__ == "__main__":
	print("You did it again, dummy!")