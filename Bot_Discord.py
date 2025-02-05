from config.config import BOT_TOKEN
from discord.ext import commands
from config.config import intents
from myScripts.Record import MP3Recorder


class BOTDiscord(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.record = MP3Recorder()

    async def on_ready(self):
        print(f"Бот {self.user} готовий до роботи!")

    async def setup_hook(self):
        # await self.load_extension("Cogs.Voice")  # Підключаємо команду
        await self.load_extension("Cogs.Admin")
        try:
            synced = await self.tree.sync()
            print(f"Синхронізовано {len(synced)} команд")
        except Exception as e:
            print(f"Помилка при синхронізації команд: {e}")


bot = BOTDiscord()

bot.run(BOT_TOKEN)


