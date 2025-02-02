import discord
import os
from discord import FFmpegPCMAudio,app_commands
from discord.ext import commands
from discord.ext.voice_recv import VoiceRecvClient
from config import FFMPEG_PATH,RECORDINGS_DIR,RECOGNITION_DIR
from Speech_analyse import recognize_speech_from_wav
from gtts import gTTS
from Record import MP3Recorder
from datetime import datetime


class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.recorder = None

    @app_commands.command(name="join", description="Підключає бота до голосового каналу")
    async def join(self, interaction: discord.Interaction):
        """ 📢 Підключення до голосового каналу з підтримкою запису """
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("❌ Ви повинні бути в голосовому каналі!", ephemeral=True)
            return

        channel = interaction.user.voice.channel
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()

        await channel.connect(cls=VoiceRecvClient)
        await interaction.response.send_message(f"✅ Підключився до {channel.mention}")

    @app_commands.command(name="record", description="Початок запису голосового чату")
    async def record(self, interaction: discord.Interaction):
        """ 🎙️ Початок запису голосового чату """
        vc = interaction.guild.voice_client

        if not vc:
            await interaction.response.send_message("❌ Бот не підключений до голосового каналу!", ephemeral=True)
            return

        if not isinstance(vc, VoiceRecvClient):
            await interaction.response.send_message(
                "⚠️ Бот підключений без підтримки запису! Використовуйте `/join` перед записом.", ephemeral=True)
            return

        if self.recorder:
            await interaction.response.send_message("🔴 Запис вже триває!", ephemeral=True)
            return

        self.recorder = MP3Recorder()  # Створюємо екземпляр запису
        vc.listen(self.recorder)  # Починаємо запис
        await interaction.response.send_message("✅ Почав запис голосового чату!")

    @app_commands.command(name="stop", description="Зупиняє запис голосового чату")
    async def stop(self, interaction: discord.Interaction):
        """ ⏹️ Зупинка запису """
        vc = interaction.guild.voice_client

        if not self.recorder:
            await interaction.response.send_message("❌ Запис не ведеться!", ephemeral=True)
            return

        vc.stop_listening()  # Зупиняємо запис
        self.recorder = None  # Очищаємо змінну
        await interaction.response.send_message("✅ Запис зупинено!")

    @app_commands.command(name="leave", description="Відключає бота від голосового каналу")
    async def leave(self, interaction: discord.Interaction):
        """ 🚪 Відключення бота від голосового каналу """
        vc = interaction.guild.voice_client

        if not vc:
            await interaction.response.send_message("❌ Я не в голосовому каналі!", ephemeral=True)
            return

        await vc.disconnect()
        await interaction.response.send_message("👋 Вийшов з голосового каналу!")

    @app_commands.command(name="analyse", description="Розпізнає голос з записаного файлу")
    async def analyse(self, interaction: discord.Interaction):
        """ 🎙️ Розпізнавання голосу з записаного файлу """
        user_id = interaction.user.name
        date = datetime.now().strftime("%Y-%m-%d")
        file_path = os.path.join(RECOGNITION_DIR, f"user_{user_id}_{date}.wav")

        try:
            if not os.path.exists(file_path):  # Перевірка існування файлу
                raise FileNotFoundError(f"Файл `{file_path}` не знайдено!")

            text = recognize_speech_from_wav(file_path)
            await interaction.response.send_message(f"📝 Розпізнаний текст:\n{text}")

        except FileNotFoundError as e:
            await interaction.response.send_message(f"❌ Помилка: {e}", ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(f"⚠️ Сталася несподівана помилка: {e}", ephemeral=True)

    @app_commands.command(name="member", description="Показує список учасників сервера")
    async def member(self, interaction: discord.Interaction):
        """ 📜 Список учасників сервера """
        guild = interaction.guild
        members = [member.name for member in guild.members]
        member_list = "\n".join(members)
        await interaction.response.send_message(f"👥 Учасники сервера:\n{member_list}")

    @app_commands.command(name="say",description="Озвучує текст")
    async def say(self, interaction: discord.Interaction, *, text: str):
        """ 🗣️ Бот озвучує введений текст """
        vc = interaction.guild.voice_client
        if not vc:
            await interaction.response.send_message("❌ Я не в голосовому каналі! Використай `!join`, щоб я приєднався.")
            return

        tts = gTTS(text=text, lang="uk")
        audio_file = "tts.mp3"
        tts.save(audio_file)


        if not vc.is_playing():
            vc.play(discord.FFmpegPCMAudio(audio_file, executable=FFMPEG_PATH), after=lambda e: os.remove(audio_file))
            await interaction.response.send_message(f"🗣️ Озвучую: `{text}`")
        else:
            await interaction.response.send_message("⏳ Зачекай, я вже говорю!")

    @app_commands.command(name="play",description="Свято наближаєтся ")
    async def play(self, interaction: discord.Interaction):
        """ 🎵 Бот відтворює останній записаний аудіофайл """
        if not interaction.guild.voice_client:
            await interaction.response.send_message("123")
            return

        audio_path = os.path.join(RECORDINGS_DIR, "user_sunik._2025-01-31.mp3")

        if not os.path.exists(audio_path):
            await interaction.response.send_message(f"❌ Файл `{audio_path}` не знайдено!", ephemeral=True)
            return

        vc = interaction.guild.voice_client
        if not vc.is_playing():
            vc.play(discord.FFmpegPCMAudio(audio_path, executable=FFMPEG_PATH))
            await interaction.response.send_message(f"🎵 Відтворюю `{audio_path}`")
        else:
            await interaction.response.send_message("⏳ Зачекай, я вже відтворюю звук!", ephemeral=True)

    @app_commands.command(name="hello", description="Привітатися з ботом")
    async def hello(self, interaction: discord.Interaction):
        await interaction.response.send_message("Привіт!")




async def setup(bot):
    await bot.add_cog(Voice(bot))