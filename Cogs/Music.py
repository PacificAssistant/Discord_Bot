from discord.ext import commands
from discord import app_commands
from discord.app_commands import checks
import discord
from database.database import SessionLocal
from database.models import User, Roles, UserRoles
from config.config import ydl_opts
import yt_dlp as youtube_dl
from Cogs.BaseCog import BaseCog


class Music(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)

    @app_commands.command(name="play_music", description="")
    async def play_music(self, interaction: discord.Interaction, *, url: str):
        voice_client = discord.utils.get(
            self.bot.voice_clients, guild=interaction.guild
        )

        if not voice_client:
            voice_cog = self.bot.get_cog("Voice")  # Отримуємо Voice Cog
            if voice_cog:
                await voice_cog.join.callback(voice_cog, interaction)
                voice_client = discord.utils.get(
                    self.bot.voice_clients, guild=interaction.guild
                )
            else:
                await interaction.response.send_message(
                    self.message["bot_cant_join"], ephemeral=True
                )
                return

        with youtube_dl.YoutubeDL(ydl_opts) as yld:
            info = yld.extract_info(url, download=False)
            url2 = info["url"]

        voice_client.play(
            discord.FFmpegPCMAudio(url2), after=lambda e: print("Complete")
        )
        if not interaction.response.is_done():
            await interaction.response.send_message(
                self.message["play_url"].format(url=url)
            )

    @app_commands.command(name="youtube_video", description="")
    async def youtube_video(self, interaction: discord.Interaction, *, url: str):
        await interaction.response.send_message(self.message["play_video"])


async def setup(bot):
    await bot.add_cog(Music(bot))
