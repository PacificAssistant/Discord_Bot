from config.config import BOT_TOKEN
from discord.ext import commands
from config.config import intents, MESSAGE
from myScripts.Record import MP3Recorder
from Cogs.BaseCog import BaseCog


class BOTDiscord(commands.Bot):
    """A custom Discord bot class extending commands.Bot.

    This class implements a Discord bot with voice, admin, and music capabilities.
    It handles command synchronization, cog loading, and maintains message configurations.

    Attributes:
        record (MP3Recorder): Instance of MP3Recorder for handling voice recordings.
        descriptions (dict): Command descriptions loaded from MESSAGE configuration.
        message (dict): General messages loaded from MESSAGE configuration.
        error (dict): Error messages loaded from MESSAGE configuration.
    """
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.record = MP3Recorder()
        # for key, value in MESSAGE.items():
        #     setattr(self, key.lower(), value)
        self.descriptions = MESSAGE.get("descriptions", "")
        self.message = MESSAGE.get("message", "")
        self.error = MESSAGE.get("error", "")

    async def on_ready(self):
        """Callback that fires when the bot has successfully connected to Discord.

           Prints a confirmation message when the bot is ready to handle commands.

           Returns:
               None
           """
        print(f"Бот {self.user} готовий до роботи!")

    async def setup_hook(self):
        """Initializes the bot by loading extensions and synchronizing commands.

            This method:
            1. Loads Voice, Admin, and Music cogs
            2. Updates command descriptions for all BaseCog subclasses
            3. Synchronizes application commands with Discord

            Returns:
                None

            Raises:
                Exception: If command synchronization fails.
            """
        await self.load_extension("Cogs.Voice")
        await self.load_extension("Cogs.Admin")
        await self.load_extension("Cogs.Music")

        # Оновлення описів команд для всіх Cogs
        for cog in self.cogs.values():
            if isinstance(cog, BaseCog):  # Перевіряємо, чи є клас підкласом BaseCog
                cog.update_command_descriptions()
        try:
            synced = await self.tree.sync()
            print(
                self.message.get(
                    "synchronization", "Синхронізовано {count} команд"
                ).format(count=len(synced))
            )

        except Exception as e:
            print(self.error["SynchronizationError"].format(e=e))


bot = BOTDiscord()

bot.run(BOT_TOKEN)
