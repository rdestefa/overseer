# help.py

import json
import logging
import logging.config
import os
import sys

import discord
from discord.ext import commands

# Bot and logger configs
if not os.path.isfile("config.json"):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open("config.json") as file:
        config = json.load(file)

logger = logging.getLogger()


class Help(commands.Cog, name="help"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="help",
        usage="help <command>",
        brief="List one or all of the Overseer's commands."
    )
    async def help(self, context, command=None):
        """
        Display help text for a specific command.
        If no command is specified, the Overseer will list all commands from every Cog that it's loaded.
        """
        if command is not None:
            # Trim prefix from command
            command = command[1:] if command.startswith(
                config['bot_prefix']) else command

            # Search for command within cogs
            for i in self.bot.cogs:
                cmds = self.bot.get_cog(i.lower()).get_commands()
                cmd_names = [cmd.name for cmd in cmds]
                if command in cmd_names:
                    cmd = cmds[cmd_names.index(command)]
                    embed = discord.Embed(
                        title=f"{cmd.name.capitalize()} (Usage: `{cmd.usage}`)",
                        description=f"{cmd.help}",
                        color=0x42F56C
                    )
                    await context.send(embed=embed)
                    return

            # Command not found
            raise commands.CommandNotFound(f'Command "{command}" is not found')

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
            cmds = cog.get_commands()
            cmd_list = [cmd.usage for cmd in cmds]
            cmd_description = [cmd.brief for cmd in cmds]

            help_text = '\n'.join(
                f'{prefix}{n} - {h}' for n, h in zip(cmd_list,
                                                     cmd_description))
            embed.add_field(name=i.capitalize(),
                            value=f'```{help_text}```', inline=False)
        await context.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
