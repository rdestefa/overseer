# help.py

import json
import logging
import logging.config
import os
import sys
import yaml

import discord
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


class Help(commands.Cog, name="help"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", usage="help")
    async def help(self, context):
        """
        List all commands from every Cog that Overseer has loaded.
        """
        prefix = config["bot_prefix"]
        if not isinstance(prefix, str):
            prefix = prefix[0]
        embed = discord.Embed(
            title="Help",
            description="Witness the extent of my power.",
            color=0x42F56C
        )
        for i in self.bot.cogs:
            cog = self.bot.get_cog(i.lower())
            commands = cog.get_commands()
            command_list = [command.usage for command in commands]
            command_description = [command.help for command in commands]
            help_text = '\n'.join(
                f'{prefix}{n} - {h}' for n, h in zip(command_list,
                                                     command_description))
            embed.add_field(name=i.capitalize(),
                            value=f'```{help_text}```', inline=False)
        await context.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
