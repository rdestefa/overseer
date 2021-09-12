# template.py

import json
import logging
import logging.config
import os
import sys

from discord.ext import commands

# Bot and logger configs
if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

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
