import discord
from discord.ext import commands
from discord.ext.voice_recv import VoiceRecvClient ,AudioSink
import subprocess
import os
from pydub import AudioSegment
from datetime import datetime,timedelta

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)
RECORDINGS_DIR = "recordings"
BOT_TOKEN="YOUR_TOKEN"

if not os.path.exists(RECORDINGS_DIR):
    os.makedirs(RECORDINGS_DIR)


@bot.event
async def on_ready():
    print(f"Бот {bot.user} готовий до роботи!")


@bot.command()
async def join(ctx):
    """ Подключение к голосовому каналу с поддержкой записи """
    if ctx.author.voice is None or ctx.author.voice.channel is None:
        await ctx.send("Вы должны быть в голосовом канале!")
        return

    channel = ctx.author.voice.channel
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

    # Подключаемся к голосовому каналу как VoiceRecvClient (с записью)
    vc = await channel.connect(cls=VoiceRecvClient)
    await ctx.send(f" Подключился к {channel.name} с поддержкой записи!")


class MP3Recorder(AudioSink):
    """ Клас для запису аудіо та збереження у MP3 """

    def __init__(self):
        self.files = {}

    def write(self, user_id, data):
        """ Запис PCM-даних у файл """
        pcm_path = f"{RECORDINGS_DIR}/user_{user_id}.pcm"

        with open(pcm_path, "ab") as f:
            f.write(data.pcm)  # Важливо зберігати саме data.pcm!

    def cleanup(self):
        """ Конвертація PCM у MP3 """
        for pcm_file in os.listdir(RECORDINGS_DIR):
            if pcm_file.endswith(".pcm"):
                user_id = pcm_file.split("_")[1].split(".")[0]
                pcm_path = os.path.join(RECORDINGS_DIR, pcm_file)
                mp3_path = os.path.join(RECORDINGS_DIR, f"user_{user_id}.mp3")

                # Конвертація PCM -> WAV -> MP3 (щоб уникнути помилок)
                wav_path = pcm_path.replace(".pcm", ".wav")

                # PCM у WAV
                audio = AudioSegment.from_raw(
                    pcm_path, sample_width=2, frame_rate=48000, channels=2
                )
                audio.export(wav_path, format="wav")

                # WAV у MP3 (192 kbps)
                audio = AudioSegment.from_wav(wav_path)
                audio.export(mp3_path, format="mp3", bitrate="192k")

                os.remove(pcm_path)
                os.remove(wav_path)

    def wants_opus(self):
        """ Запитуємо PCM замість Opus """
        return False


@bot.command()
async def record(ctx):
    """ Начало записи голосового чата """
    start_time= datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not ctx.voice_client:
        await ctx.send(" Бот не подключен к голосовому каналу!")
        return

    if not isinstance(ctx.voice_client, VoiceRecvClient):  # Проверяем поддержку записи
        await ctx.send(" Бот подключен без поддержки записи! Используйте `!join` перед записью.")
        return

    ctx.voice_client.listen(MP3Recorder())  # Начинаем запись
    await ctx.send(" Запись голосового чата началась!")


@bot.command()
async def stop(ctx):
    """ Остановка записи голосового чата """
    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not ctx.voice_client or not isinstance(ctx.voice_client, VoiceRecvClient):
        await ctx.send(" Бот не записывает звук в данный момент!")
        return

    ctx.voice_client.stop_listening()  # Останавливаем запись
    await ctx.send(" Запись голосового чата остановлена!")

    # Конвертируем PCM в WAV
    MP3Recorder().cleanup()

    await ctx.send(" Файлы сохранены в формате WAV!")


@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Бот відключився від голосового каналу.")
    else:
        await ctx.send("Бот не підключений до голосового каналу.")


bot.run(BOT_TOKEN)