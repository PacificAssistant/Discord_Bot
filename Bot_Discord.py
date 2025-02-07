from config.config import BOT_TOKEN
from discord.ext import commands
from config.config import intents, MESSAGE
from myScripts.Record import MP3Recorder
from Cogs.BaseCog import BaseCog


class BOTDiscord(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.record = MP3Recorder()
        # for key, value in MESSAGE.items():
        #     setattr(self, key.lower(), value)
        self.descriptions = MESSAGE.get("descriptions", "")
        self.message = MESSAGE.get("message", "")
        self.error = MESSAGE.get("error", "")

    async def on_ready(self):
        print(f"Бот {self.user} готовий до роботи!")

    async def setup_hook(self):
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
