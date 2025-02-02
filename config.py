import os
import discord


intents = discord.Intents.default()

intents.message_content = True
intents.voice_states = True
intents.members = True

FFMPEG_PATH = "ffmpeg"
RECORDINGS_DIR = "recordings"
RECOGNITION_DIR = "recognition"
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN" )  # USE YOUR TOKEN AND PLACE HERE

if not os.path.exists(RECORDINGS_DIR):
    os.makedirs(RECORDINGS_DIR)
if not os.path.exists(RECOGNITION_DIR):
    os.makedirs(RECOGNITION_DIR)