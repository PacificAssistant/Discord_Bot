import os
import discord
from datetime import datetime
import json
from dotenv import load_dotenv
from database.init_db import db_init
import shutil

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
db_init()

CONFIG_PATH = os.path.join(BASE_DIR, "JsonDir", "strings.json")


def load_config():
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Файл не знайдено: {CONFIG_PATH}")
    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


MESSAGE = load_config()

original_cookie_path = "cookies.txt"
backup_cookie_path = "cookies.backup.txt"

# Створюємо резервну копію
shutil.copy2(original_cookie_path, backup_cookie_path)
if os.path.exists(original_cookie_path):
    print("Файл знайдено")
else:
    print(f"Файл не знайдено cockie {cookie_path} , {path}")

ydl_opts = {
    "format": "bestaudio",
    "no_warnings": True,
    "extract_flat": "in_playlist",
    "nocheckcertificate": True,
    "ignoreerrors": True,
    "no_cache": True,
    "http_headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-us,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
    },
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "192",
    }],
    "cookiefile": backup_cookie_path,
}


if not os.path.exists(RECORDINGS_DIR):
    os.makedirs(RECORDINGS_DIR)
if not os.path.exists(RECOGNITION_DIR):
    os.makedirs(RECOGNITION_DIR)
