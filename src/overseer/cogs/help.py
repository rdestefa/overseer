# overseer.cogs.help

import logging

from utils.configs import load_config

import discord
from discord.ext import commands

# Color and logger configs.
colors = load_config("colors")
logger = logging.getLogger()


class Help(commands.Cog, name="help"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name="help",
        usage="help <command>",
        brief="List one or all of the Overseer's commands."
    )
    async def help(self, context: commands.Context, *, command=None) -> None:
        """
        Display help text for a specific command.
        If no command is specified, I will list all my commands.

        Parameters
        -----------
        command: str
            The command you need help with. If empty, all commands are shown.
        """
        if command is not None:
            # Trim prefix from command.
            command = command[1:] if command.startswith(
                self.bot.command_prefix) else command

            # Search for matching command.
            if (cmd := self.bot.get_command(command)) is not None and not cmd.hidden:
                title = (f"{cmd.name.replace('_', ' ').title()} (Usage: `{self.bot.command_prefix}{cmd.usage}`)" if not cmd.parents
                         else f"{cmd.qualified_name.replace('_', ' ').title()} (Usage: `{self.bot.command_prefix}{' '.join(map(str, cmd.parents))} {cmd.usage}`)")
                embed = discord.Embed(
                    title=title,
                    description=f"{cmd.help}",
                    color=colors["green"]
                )

                await context.send(embed=embed)
                return

            # If no valid command was found, throw an exception.
            raise commands.CommandNotFound(f'Command "{command}" is not found')

        prefix = self.bot.command_prefix

        # In case the bot has a list of prefixes.
        if not isinstance(prefix, str):
            prefix = prefix[0]

        embed = discord.Embed(
            title="Help",
            description="Witness the extent of my power.",
            color=colors["green"]
        )

        # Add commands for each Cog to the embed separately.
        for cog_name in self.bot.cogs:
            cog = self.bot.get_cog(cog_name.lower())
            cmd_attrs = [(cmd.usage, cmd.brief, cmd.parents)
                         for cmd in cog.walk_commands() if not cmd.hidden]

            # Create bulleted list with proper indentation for each Cog.
            help_text = "\n".join(
                f"{prefix}{usage} - {brief}" if not parents
                else f"{'  ' * len(parents)}+ {usage} - {brief}"
                for usage, brief, parents in cmd_attrs)
            embed.add_field(name=cog_name.capitalize(),
                            value=f'```{help_text}```', inline=False)
        await context.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))
