import os

import discord

DIRECTORY = os.path.realpath(os.path.dirname(__file__))
SOUNDS_DIR = DIRECTORY + "/data/sounds/"
SOUND_NAMES = []
SOUNDS = {}

class VoiceHandler:
    async def startup(client: discord.Client):
        VoiceHandler.client = client
    
    async def load_list():
        global SOUND_NAMES

        SOUND_NAMES = []
        
        for filename in os.listdir(SOUNDS_DIR):
            if filename.endswith(".mp3"):
                name = filename[:-4]
                sound = await discord.FFmpegOpusAudio.from_probe(f"data/sounds/{name}.mp3")

                SOUND_NAMES += [name]
                SOUNDS[name] = sound

    async def process(message: discord.Message):
        args = message.content.split()[1:]

        if not SOUND_NAMES:
            await VoiceHandler.load_list()

        if len(args) == 0:
            await VoiceHandler.send_help_message(message.channel)
        elif args[0].lower() in ["help", "?"]:
            await VoiceHandler.send_help_message(message.channel)
        elif args[0].lower() in ["join", "connect"]:
            await VoiceHandler.join_user_voice_channel(message)
            voice_client = discord.utils.get(VoiceHandler.client.voice_clients, guild=message.guild)
            await VoiceHandler.play_sfx("hello", voice_client)
        elif args[0].lower() in ["leave", "disconnect"]:
            await VoiceHandler.leave_voice_channel(message)
        elif args[0].lower() in ["play"]:
            await VoiceHandler.start_playing_sfx(message)
        elif args[0].lower() in ["stop", "shut", "stfu"]:
            voice_client = discord.utils.get(VoiceHandler.client.voice_clients, guild=message.guild)
            voice_client.stop()
        elif args[0].lower() in ["list", "sounds", "sfx"]:
            await VoiceHandler.create_sounds_list_message(message.channel)
    
    async def get_voice_channel(message: discord.Message):
        user = message.author
        voice_state = user.voice

        if voice_state == None:
            return None
        
        return voice_state.channel
    
    async def join_user_voice_channel(message: discord.Message):
        try:
            channel = await VoiceHandler.get_voice_channel(message)
            await channel.connect()
        except:
            pass
    
    async def leave_voice_channel(message: discord.Message):
        try:
            await message.guild.voice_client.disconnect()
        except:
            pass
    
    async def play_sfx(name: str, voice_client: discord.VoiceClient):
        if name in SOUND_NAMES:
            voice_client.play(SOUNDS[name])

            sound = await discord.FFmpegOpusAudio.from_probe(f"data/sounds/{name}.mp3")
            SOUNDS[name] = sound
    
    async def start_playing_sfx(message: discord.Message):
        args = message.content.split()[1:]

        try:
            guild = message.guild
            voice_client = discord.utils.get(VoiceHandler.client.voice_clients, guild=guild)

            if not voice_client:
                await VoiceHandler.join_user_voice_channel(message)
                voice_client = discord.utils.get(VoiceHandler.client.voice_clients, guild=guild)
            
            sound_name = args[1]
            await VoiceHandler.play_sfx(sound_name,	voice_client)
        except:
            pass
    
    async def create_sounds_list_message(channel: discord.abc.Messageable):
        await VoiceHandler.load_list()

        strings = [
            "Sound effects:"
        ]
        for name in SOUND_NAMES:
            strings += [f"- <{name}>"]

        await channel.send("```md\n" + "\n".join(strings) + "```")
    
    async def send_help_message(channel: discord.abc.Messageable):
        strings = [
            "= Voice Channel =",
            "",
            "* %vc join",
            "Joins the user in a voice channel.",
            "",
            "* %vc leave",
            "Leaves the voice channel.",
            "",
            "* %vc play [name]",
            "Plays a sound effect.",
            "name :: The name of the sound effect (can be found in the list).",
            "",
            "* %vc stop",
            "Stops talking.",
            "",
            "* %vc list",
            "Shows all available sound effects."
        ]

        await channel.send("```asciidoc\n" + "\n".join(strings) + "```")

if __name__ == "__main__":
    print("You did it again, dummy!")