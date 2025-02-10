from discord.ext import commands
from discord import app_commands
from discord.app_commands import checks
import discord
from database.database import SessionLocal
from database.models import User, Roles, UserRoles
from config.config import ydl_opts
import yt_dlp as youtube_dl
from Cogs.BaseCog import BaseCog
import asyncio

class Music(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)
        self.queue = asyncio.Queue()
        self.curently_playing= None
        self.is_paused = False
        self.history=[]

    @app_commands.command(name="play_music", description="")
    async def play_music(self, interaction: discord.Interaction, *, url: str):
        """
                Plays music from a given URL in a voice channel.

                This method retrieves the audio stream URL using youtube_dl and adds it to the playback queue.
                If the bot is not connected to a voice channel, it attempts to connect before playing the song.
                If no song is currently playing, it starts playback immediately.

                Args:
                    interaction (discord.Interaction): The interaction object representing the command invocation.
                    url (str): The URL of the music to be played.

                Returns:
                    None: Sends a confirmation message upon adding the song to the queue or an error message if the bot cannot connect.
                """
        await interaction.response.defer()  # Запобігає Unknown Interaction

        voice_client = await self.get_voice_client(interaction)
        if not voice_client:
            await interaction.followup.send("Бот не може підключитися", ephemeral=True)
            return

        try:
            with youtube_dl.YoutubeDL(ydl_opts) as yld:
                info = yld.extract_info(url, download=False)
                url2 = info["url"]
                title = info.get("title", "Unknown Title")

            self.history.append((url2, title))
            await self.queue.put((url2, title))

            if not self.curently_playing:
                await self.play_next_song(voice_client)

            await interaction.followup.send(f"✅ Додано в чергу: **{title}**")
        except Exception as e:
            print(f"Unexcepted error: {e} ")



    async def play_next_song(self,voice_client):
        """Plays the next song in the queue if one exists.

        Retrieves the next song from the queue and plays it using the voice client. If the queue is empty,
        resets the currently playing track. Sets up a callback to handle errors and automatically play the
        next song when the current one finishes.

        Args:
            voice_client (discord.VoiceClient): The voice client used to play audio.

        Returns:
            None
        """
        if self.queue.empty():
            self.curently_playing = None
            return
        self.curently_playing = await self.queue.get()
        url,title = self.curently_playing

        def after_play(error):
            if error:
                print(f"Помилка при відтворенні: {error}")
            asyncio.run_coroutine_threadsafe(self.play_next_song(voice_client), self.bot.loop)

        if not voice_client.is_playing():
            voice_client.play(discord.FFmpegPCMAudio(url), after=after_play)

    async def get_voice_client(self, interaction: discord.Interaction) -> discord.VoiceClient | None:
        """Gets or creates a voice client for the bot in the current guild.

        Checks if the bot is already in a voice channel and connects it if needed by
        calling the Voice cog's join command.

        Args:
            interaction (discord.Interaction): The interaction object from the command invocation.

        Returns:
            discord.VoiceClient | None: The voice client if successful, None if the voice cog
                is not found or connection fails.
        """
        voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)

        if not voice_client:
            voice_cog = self.bot.get_cog("Voice")
            if voice_cog:
                await voice_cog.join.callback(voice_cog, interaction)
                voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
            else:
                return None

        return voice_client

    @app_commands.command(name = "previos", description="")
    async def previos(self,interaction: discord.Interaction):
        """Plays the previously played song.

        Retrieves the second-to-last song from the playback history and adds it to the front
        of the queue. Initiates playback if no song is currently playing.

        Args:
            interaction (discord.Interaction): The interaction object from the command invocation.

        Returns:
            None: Sends a message indicating success or failure of the operation.
        """
        await interaction.response.defer()  # Додаємо defer, щоб уникнути помилки
        if len(self.history) < 2:
            await interaction.followup.send("❌ Немає попередньої пісні для відтворення!", ephemeral=True)
            return

        last_song = self.history[-2]  # Беремо передостанню пісню
        self.queue._queue.appendleft(last_song)  # Додаємо її на початок черги
        voice_client = await self.get_voice_client(interaction)

        if voice_client and not self.curently_playing:
            await self.play_next_song(voice_client)

        if not interaction.response.is_done():
            await interaction.response.send_message(f"⏪ Відтворюємо попередню пісню: **{last_song[1]}**")
        else:
            await interaction.followup.send(f"⏪ Відтворюємо попередню пісню: **{last_song[1]}**")

    @app_commands.command(name = "pause",description="")
    async def pause (self,interaction: discord.Interaction):
        """Pauses the currently playing song.

        Pauses audio playback if a song is currently playing through the voice client.

        Args:
            interaction (discord.Interaction): The interaction object from the command invocation.

        Returns:
            None: Sends a message confirming the pause action.
        """
        voice_client = await self.get_voice_client(interaction)
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            self.is_paused = True
            await interaction.response.send_message("⏸️ Музику поставлено на паузу")

    @app_commands.command(name="resume", description="")
    async def resume(self, interaction: discord.Interaction):
        """Resumes playback of a paused song.

        Resumes audio playback if a song is currently paused through the voice client.

        Args:
            interaction (discord.Interaction): The interaction object from the command invocation.

        Returns:
            None: Sends a message confirming the resume action.
        """
        voice_client = await self.get_voice_client(interaction)
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            self.is_paused = False
            await interaction.response.send_message("▶️ Відтворення відновлено")

    @app_commands.command(name = "skip",description="")
    async def skip (self,interaction : discord.Interaction):
        """Skips the currently playing song.

        Stops the current song and initiates playback of the next song in the queue.

        Args:
            interaction (discord.Interaction): The interaction object from the command invocation.

        Returns:
            None: Sends a message confirming the skip action and begins playing the next song.
        """
        voice_client = await self.get_voice_client(interaction)
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            await interaction.response.send_message("⏭️ Пісню пропущено")
            await self.play_next_song(voice_client)

    @app_commands.command(name="youtube_video", description="")
    async def youtube_video(self, interaction: discord.Interaction, *, url: str):
        """Handles a YouTube video URL command.

        Responds with a predefined message when a YouTube video URL is provided.

        Args:
            interaction (discord.Interaction): The interaction object from the command invocation.
            url (str): The YouTube video URL provided by the user.

        Returns:
            None: Sends the predefined response message.
        """
        await interaction.response.send_message(self.message["play_video"])


async def setup(bot):
    await bot.add_cog(Music(bot))
