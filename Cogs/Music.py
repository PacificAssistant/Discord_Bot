from discord.ext import commands
from discord import app_commands
from discord.app_commands import checks
import discord
from database.database import SessionLocal
from database.models import User,Roles,UserRoles

class Music(commands.Cog):
    def __init__(self):
        self.bot = bot

    @app_commands.command(name="play_music", description="Add info about members in db")
    async def play_music(self,interaction: discord.Interaction):
        pass