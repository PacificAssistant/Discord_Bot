import os
import discord
from datetime import datetime
import json
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

intents = discord.Intents.default()

intents.message_content = True
intents.voice_states = True
intents.members = True


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FFMPEG_PATH = "ffmpeg"
RECORDINGS_DIR = os.path.join(BASE_DIR, "recordings")
RECOGNITION_DIR = os.path.join(BASE_DIR, "recognition")
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # USE YOUR TOKEN AND PLACE HERE
if not BOT_TOKEN:
    raise ValueError("❌ DISCORD_BOT_TOKEN не знайдено! Перевір змінні середовища.")
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL не знайдено! Перевір змінні середовища.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
Base.metadata.create_all(bind=engine)

CONFIG_PATH = os.path.join(BASE_DIR, "JsonDir", "strings.json")


def load_config():
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Файл не знайдено: {CONFIG_PATH}")
    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


MESSAGE = load_config()

ydl_opts = {
    "format": "bestaudio/best",
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        },
    ],
    "noplaylist": True,
}


if not os.path.exists(RECORDINGS_DIR):
    os.makedirs(RECORDINGS_DIR)
if not os.path.exists(RECOGNITION_DIR):
    os.makedirs(RECOGNITION_DIR)
