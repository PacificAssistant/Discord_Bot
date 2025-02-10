from discord.ext import commands


class BaseCog(commands.Cog):
    """Base cog class that provides common functionality for all cogs.

    A foundational cog class that implements shared features and attributes used across
    different cogs in the bot. It handles message configurations and command description
    management.

    Attributes:
        bot (commands.Bot): The bot instance this cog is attached to.
        descriptions (dict): Command descriptions inherited from the bot.
        message (dict): General messages inherited from the bot.
        error (dict): Error messages inherited from the bot.
    """
    def __init__(self, bot: commands.Bot):
        """Updates the descriptions of all registered slash commands.

            Iterates through all commands registered in the bot's command tree and
            updates their descriptions based on the descriptions dictionary. Only
            updates commands that have matching entries in the descriptions dictionary.

            Returns:
                None
            """
        self.bot = bot
        self.descriptions = bot.descriptions  # Отримуємо опис команд з бота
        self.message = bot.message
        self.error = bot.error

    def update_command_descriptions(self):
        for command in self.bot.tree.get_commands():
            if command.name in self.descriptions:
                command.description = self.descriptions[command.name]
