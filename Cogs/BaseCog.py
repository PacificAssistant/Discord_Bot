from discord.ext import commands


class BaseCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.descriptions = bot.descriptions  # Отримуємо опис команд з бота
        self.message = bot.message
        self.error = bot.error

    def update_command_descriptions(self):
        for command in self.bot.tree.get_commands():
            if command.name in self.descriptions:
                command.description = self.descriptions[command.name]
