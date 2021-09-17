# overseer.cogs.template

import logging

from helpers.config_helpers import load_bot_configs

from discord.ext import commands

# Bot and logger configs
config = load_bot_configs()
logger = logging.getLogger()


# Here we name the cog and create a new class for the cog.
class Template(commands.Cog, name="template"):
    def __init__(self, bot):
        self.bot = bot

    # Here you can just add your own commands, you'll always need to provide "self" as first parameter.
    @commands.command(
        name="testcommand",
        usage="testcommand",
        brief="Test command that does nothing."
    )
    async def testcommand(self, context):
        """
        This is a testing command that does nothing.
        """
        # Do your stuff here

        # Don't forget to remove "pass"
        pass


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
def setup(bot):
    bot.add_cog(Template(bot))
