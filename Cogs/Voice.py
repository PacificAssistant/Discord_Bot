import discord
import os
from discord import app_commands
from discord.ext.voice_recv import VoiceRecvClient
from config.config import FFMPEG_PATH, RECOGNITION_DIR
from gtts import gTTS
from myScripts.Record import MP3Recorder
from datetime import datetime
from Cogs.BaseCog import BaseCog
from config.config import SessionLocal
from database.models import Audio


class Voice(BaseCog):
    """A cog for handling voice-related commands in a Discord bot."""

    def __init__(self, bot):
        super().__init__(bot)
        self.recorder = None

    @app_commands.command(name="join", description="")
    async def join(self, interaction: discord.Interaction):
        """Starts recording audio in the current voice channel.

        Initiates audio recording if the bot is in a voice channel and not already recording.
        Uses the MP3Recorder class to handle the recording process.

        Args:
            interaction (discord.Interaction): The interaction object from the command invocation.

        Returns:
            None: Sends a message confirming the start of recording or error if conditions aren't met.
        """
        user = interaction.user
        # Перевіряємо, чи користувач у голосовому каналі
        if not user.voice or not user.voice.channel:
            await interaction.response.send_message(
                self.message["user_not_in_channel"], ephemeral=True
            )
            return

        channel = user.voice.channel
        voice_client = interaction.guild.voice_client

        # Якщо бот вже в голосовому каналі
        if voice_client:
            if voice_client.channel == channel:
                await interaction.response.send_message(self.message["bot_in_channel"], ephemeral=True)
                return
            await voice_client.disconnect()  # Вихід із поточного каналу

        try:
            await channel.connect(cls=VoiceRecvClient)
            if interaction.response.is_done():
                await interaction.followup.send(
                    self.message["join_to_channel"].format(channel=channel)
                )
            else:
                await interaction.response.send_message(
                    self.message["join_to_channel"].format(channel=channel)
                )
        except discord.errors.ClientException as e:
            await interaction.response.send_message(f"❌ Помилка підключення: {str(e)}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"⚠️ Несподівана помилка: {str(e)}", ephemeral=True)

    @app_commands.command(name="record", description="")
    async def record(self, interaction: discord.Interaction):
        """Starts recording audio in the current voice channel.

        Initiates audio recording if the bot is in a voice channel and not already recording.
        Uses the MP3Recorder class to handle the recording process.

        Args:
            interaction (discord.Interaction): The interaction object from the command invocation.

        Returns:
            None: Sends a message confirming the start of recording or error if conditions aren't met.
        """
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
        """Stops the current audio recording session.

        Halts any ongoing recording and cleans up the recorder instance.

        Args:
            interaction (discord.Interaction): The interaction object from the command invocation.

        Returns:
            None: Sends a message confirming the recording has stopped.
        """
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
        """Disconnects the bot from the current voice channel.

        Checks if the bot is in a voice channel and disconnects it if present.

        Args:
            interaction (discord.Interaction): The interaction object from the command invocation.

        Returns:
            None: Sends a message confirming the bot has left the channel.
        """
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
        """Analyzes the recorded audio file and converts it to text.

        Attempts to find and process a recorded audio file for the user from the current date,
        using speech recognition to convert it to text.

        Args:
            interaction (discord.Interaction): The interaction object from the command invocation.

        Returns:
            None: Sends a message with the transcribed text or error message if processing fails.

        Raises:
            FileNotFoundError: If the audio file doesn't exist.
        """
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
        """Converts text to speech and plays it in the voice channel.

        Uses Google Text-to-Speech (gTTS) to convert the provided text to audio and plays it
        in the current voice channel. If music is playing, it will be paused and resumed after
        the text-to-speech completes.

        Args:
            interaction (discord.Interaction): The interaction object from the command invocation.
            text (str): The text to convert to speech.

        Returns:
            None: Sends a message confirming the text being spoken.
        """
        vc = interaction.guild.voice_client
        if not vc:
            await interaction.response.send_message(self.message["bot_not_in_channel"])
            return

            # Якщо щось грає, зберігаємо потік і ставимо на паузу
        if vc.is_playing():
            self.current_audio = vc.source
            vc.pause()
            self.is_paused = True

        tts = gTTS(text=text, lang="uk")
        audio_file = "tts.mp3"
        tts.save(audio_file)

        def after_tts(_):  # _ - Заглушка
            os.remove(audio_file)  # Видаляємо файл після використання
            if self.current_audio and self.is_paused:
                vc.play(self.current_audio)  # Відновлюємо музику
                self.is_paused = False

        vc.play(discord.FFmpegPCMAudio(audio_file), after=after_tts)
        await interaction.response.send_message(f"🗣️ {text}")

    @app_commands.command(name="play", description="")
    async def play(self, interaction: discord.Interaction, member: discord.Member):
        """Plays a recorded audio file for a specific member.

        Retrieves and plays an audio recording associated with the specified member from the database.
        The audio file must exist for the current date.

        Args:
            interaction (discord.Interaction): The interaction object from the command invocation.
            member (discord.Member): The Discord member whose recording should be played.

        Returns:
            None: Sends a message confirming playback or error if file not found.

        Raises:
            FileNotFoundError: If the audio file doesn't exist.
        """
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
        await interaction.response.send_message(self.message["hello"])


async def setup(bot):
    """Adds the Voice cog to the bot."""
    await bot.add_cog(Voice(bot))
