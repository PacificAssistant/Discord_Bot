import discord
import os
from discord import app_commands
from discord.ext.voice_recv import VoiceRecvClient
from config.config import FFMPEG_PATH, RECOGNITION_DIR
from gtts import gTTS
from myScripts.Record import MP3Recorder
from datetime import datetime
from Cogs.BaseCog import BaseCog
from database.database import SessionLocal
from database.models import Audio


class Voice(BaseCog):
    """A cog for handling voice-related commands in a Discord bot."""

    def __init__(self, bot):
        super().__init__(bot)
        self.recorder = None

    @app_commands.command(name="join", description="")
    async def join(self, interaction: discord.Interaction):
        """Makes the bot join the user's voice channel."""
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message(
                self.message["user_not_in_channel"], ephemeral=True
            )
            return

        channel = interaction.user.voice.channel
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()

        await channel.connect(cls=VoiceRecvClient)
        await interaction.response.send_message(
            self.message["join_to_channel"].format(channel=channel)
        )

    @app_commands.command(name="record", description="")
    async def record(self, interaction: discord.Interaction):
        """Starts recording the voice channel."""
        vc = interaction.guild.voice_client

        if not vc:
            await interaction.response.send_message(
                self.message["bot_not_in_channel"], ephemeral=True
            )
            return

        if not isinstance(vc, VoiceRecvClient):
            await interaction.response.send_message(
                self.message["bot_not_record"], ephemeral=True
            )
            return

        if self.recorder:
            await interaction.response.send_message(
                self.message["bot_recording"], ephemeral=True
            )
            return

        self.recorder = MP3Recorder()  # Створюємо екземпляр запису
        vc.listen(self.recorder)  # Починаємо запис
        await interaction.response.send_message(self.message["start_record"])

    @app_commands.command(name="stop", description="")
    async def stop(self, interaction: discord.Interaction):
        """Stops recording the voice channel."""
        vc = interaction.guild.voice_client

        if not self.recorder:
            await interaction.response.send_message(
                self.message["bot_not_record"], ephemeral=True
            )
            return

        vc.stop_listening()  # Зупиняємо запис
        self.recorder = None  # Очищаємо змінну
        await interaction.response.send_message(self.message["stop_record"])

    @app_commands.command(name="leave", description="")
    async def leave(self, interaction: discord.Interaction):
        """Makes the bot leave the voice channel."""
        vc = interaction.guild.voice_client

        if not vc:
            await interaction.response.send_message(
                self.message["bot_not_in_channel"], ephemeral=True
            )
            return

        await vc.disconnect()
        await interaction.response.send_message(self.message["bot_leave"])

    @app_commands.command(name="analyse", description="")
    async def analyse(self, interaction: discord.Interaction):
        """Processes the recorded audio and returns the transcribed text."""
        user_id = interaction.user.name
        date = datetime.now().strftime("%Y-%m-%d")
        file_path = os.path.join(RECOGNITION_DIR, f"user_{user_id}_{date}.wav")

        try:
            if not os.path.exists(file_path):  # Перевірка існування файлу
                raise FileNotFoundError(
                    self.error["FileNotFoundError"].format(file_path=file_path)
                )

            text = MP3Recorder.recognize_speech_from_wav(file_path)

            await interaction.response.send_message(
                self.message["analyse_text"].format(text=text)
            )

        except FileNotFoundError as e:
            await interaction.response.send_message(f" Помилка: {e}", ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(
                self.error["UnexpectedError"].format(e=e), ephemeral=True
            )

    @app_commands.command(name="say", description="")
    async def say(self, interaction: discord.Interaction, *, text: str):
        """Uses text-to-speech to make the bot say a given text."""
        vc = interaction.guild.voice_client
        if not vc:
            await interaction.response.send_message(self.message["bot_not_in_channel"])
            return

        tts = gTTS(text=text, lang="uk")
        audio_file = "tts.mp3"
        tts.save(audio_file)

        if not vc.is_playing():
            vc.play(
                discord.FFmpegPCMAudio(audio_file, executable=FFMPEG_PATH),
                after=lambda e: os.remove(audio_file),
            )
            await interaction.response.send_message(
                self.message["bot_say"].format(text=text)
            )
        else:
            await interaction.response.send_message(self.message["bot_saying"])

    @app_commands.command(name="play", description="")
    async def play(self, interaction: discord.Interaction, member: discord.Member):
        """Plays a previously recorded audio file of a member."""
        if not interaction.guild.voice_client:
            await interaction.response.send_message(self.message["bot_not_in_channel"])
            return
        try:
            session = SessionLocal()
            date = datetime.now().strftime("%Y-%m-%d")
            file_id = MP3Recorder.generate_file_id(member.name, date)
            file_path = (
                session.query(Audio).filter_by(file_id=file_id).first().file_path
            )
            if not os.path.exists(file_path):
                raise FileNotFoundError(
                    self.error["FileNotFoundError"].format(file_path=file_path)
                )
            vc = interaction.guild.voice_client
            if not vc.is_playing():
                vc.play(discord.FFmpegPCMAudio(file_path, executable=FFMPEG_PATH))
                await interaction.response.send_message(
                    self.message["bot_play"].format(file_path=file_path)
                )
            else:
                await interaction.response.send_message(
                    self.message["bot_saying"], ephemeral=True
                )

        except FileNotFoundError as e:
            await interaction.response.send_message(f" Помилка: {e}", ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(
                self.error["UnexpectedError"].format(e=e), ephemeral=True
            )
        finally:
            session.close()

    @app_commands.command(name="hello", description="")
    async def hello(self, interaction: discord.Interaction):
        """Sends a hello message."""
        await interaction.response.send_message(self.message["hello"])


async def setup(bot):
    """Adds the Voice cog to the bot."""
    await bot.add_cog(Voice(bot))
