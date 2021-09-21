# overseer.cogs.help

import logging

from helpers.config_helpers import load_bot_configs

import discord
from discord.ext import commands

# Bot and logger configs
config = load_bot_configs()
logger = logging.getLogger()


class Help(commands.Cog, name="help"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="help",
        usage="help <command>",
        brief="List one or all of the Overseer's commands."
    )
    async def help(self, context, *, command=None):
        """
        Display help text for a specific command.
        If no command is specified, the Overseer will list all commands from every Cog that it's loaded.
        """
        if command is not None:
            # Trim prefix from command.
            command = command[1:] if command.startswith(
                config['bot_prefix']) else command

            # Search for matching command.
            if (cmd := self.bot.get_command(command)) is not None:
                title = (f"{cmd.name.capitalize()} (Usage: `{config['bot_prefix']}{cmd.usage}`)" if not cmd.parents
                         else f"{cmd.qualified_name.title()} (Usage: `{config['bot_prefix']}{' '.join(map(str, cmd.parents))} {cmd.usage}`)")
                embed = discord.Embed(
                    title=title,
                    description=f"{cmd.help}",
                    color=0x42F56C
                )
                await context.send(embed=embed)
                return

            # Command not found.
            raise commands.CommandNotFound(f'Command "{command}" is not found')

        prefix = config["bot_prefix"]
        if not isinstance(prefix, str):
            prefix = prefix[0]
        embed = discord.Embed(
            title="Help",
            description="Witness the extent of my power.",
            color=0x42F56C
        )
        for cog_name in self.bot.cogs:
            cog = self.bot.get_cog(cog_name.lower())
            cmd_attrs = [(cmd.usage, cmd.brief, cmd.parents)
                         for cmd in cog.walk_commands()]

            help_text = "\n".join(
                f"{prefix}{usage} - {brief}" if not parents
                else f"{'  ' * len(parents)}+ {usage} - {brief}"
                for usage, brief, parents in cmd_attrs)
            embed.add_field(name=cog_name.capitalize(),
                            value=f'```{help_text}```', inline=False)
        await context.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
