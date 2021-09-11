# template.py

import json
import logging
import logging.config
import os
import sys
import yaml

from discord.ext import commands

# Bot configs
if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

# Logger configs
if not os.path.isfile("logging_config.yaml"):
    print('No logging_config.yaml file found. Using default logger.')
else:
    with open("logging_config.yaml") as file:
        logging.config.dictConfig(yaml.load(file, Loader=yaml.FullLoader))
        logger = logging.getLogger(__name__)


# Here we name the cog and create a new class for the cog.
class Template(commands.Cog, name="template"):
    def __init__(self, bot):
        self.bot = bot

    # Here you can just add your own commands, you'll always need to provide "self" as first parameter.
    @commands.command(name="testcommand", usage="testcommand")
    async def testcommand(self, context):
        """
        This is a testing command that does nothing.
        """
        # Do your stuff here

        # Don't forget to remove "pass", that's just because there's no content in the method.
        pass


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
def setup(bot):
    bot.add_cog(Template(bot))
