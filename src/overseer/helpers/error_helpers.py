# overseer.helpers.error_helpers

import Levenshtein as lev

import discord
from discord.ext import commands
from discord.ext.commands import Bot


# ---------------------------- CUSTOM EXCEPTIONS ---------------------------- #


class MemberBlacklisted(commands.CheckFailure):
    """
    Custom exception to be thrown when a blacklisted user tries to issue
    a command to the Overseer.
    """

    def __init__(
        self,
        member: discord.Member,
        message: str = "The Overseer ignores blacklisted users"
    ):
        self.member = member
        self.message = message

        super().__init__(self.message)

    def __str__(self):
        return f"{self.member.name} is blacklisted. {self.message}"


# ----------------------------- ERROR HANDLERS ------------------------------ #


def handle_command_not_found(
    bot: Bot,
    error: commands.CommandNotFound,
    prefix: str
) -> discord.Embed:
    # Don't use failed command in case the error was raised from !help.
    invalidCommand = str(error).split('"')[1]

    # Calculate Levenshtein distance from valid commands for recommendation.
    cmds = [cmd for cmd in bot.walk_commands() if not cmd.hidden]
    lev_dists = [lev.distance(invalidCommand, str(cmd))
                 / max(len(invalidCommand), len(str(cmd))) for cmd in cmds]
    lev_min = min(lev_dists)

    # Build error message.
    description = f"I don't recognize the `{prefix}{invalidCommand}` command.\n"
    if lev_min <= 0.5:
        description += f"Did you mean `{prefix}{cmds[lev_dists.index(lev_min)]}`?"
    else:
        description += f"Try calling `{prefix}help` for a list of valid commands."

    # Send message.
    embed = discord.Embed(
        title="Command Not Found!",
        description=description
    )

    return embed


def handle_command_on_cooldown(error: commands.CommandOnCooldown) -> discord.Embed:
    minutes, seconds = divmod(error.retry_after, 60)
    hours, minutes = divmod(minutes, 60)
    hours = hours % 24

    embed = discord.Embed(
        title="Hey! Slow down!",
        description=f"You can use this command again in {f'{round(hours)} hours' if round(hours) > 0 else ''} {f'{round(minutes)} minutes' if round(minutes) > 0 else ''} {f'{round(seconds)} seconds' if round(seconds) > 0 else ''}."
    )

    return embed


def handle_member_not_found(error: commands.MemberNotFound) -> discord.Embed:
    invalid_member = str(error).split('"')[1]
    embed = discord.Embed(
        title="Member Not Found!",
        description=f"I looked everywhere, but I couldn't find **{invalid_member}** in the server."
    )

    return embed


def handle_member_blacklisted(error: MemberBlacklisted) -> discord.Embed:
    embed = discord.Embed(
        title="You're Blacklisted!",
        description=(f"You're on my blacklist, **{error.member.name}**.\n" +
                     "Try behaving yourself and maybe then we can talk.")
    )

    return embed


def handle_not_owner(failed_command: str, prefix: str) -> discord.Embed:
    embed = discord.Embed(
        title="Not an Owner!",
        description=f"Only my owners owners can execute `{prefix}{failed_command}`."
    )

    return embed


def handle_missing_permissions(error: commands.MissingPermissions) -> discord.Embed:
    embed = discord.Embed(
        title="Permissions Error!",
        description="You are missing the permission(s) `" + "`, `".join(
            error.missing_perms) + "` to execute this command!"
    )

    return embed


def handle_missing_required_argument(
    error: commands.MissingRequiredArgument,
    prefix: str
) -> discord.Embed:
    embed = discord.Embed(
        title="Missing Argument!",
        description=f"You forgot the following argument: `{error.param}`.\nTry calling `{prefix}help` if you're having trouble."
    )

    return embed


def handle_too_many_arguments(failed_command: str, prefix: str) -> discord.Embed:
    embed = discord.Embed(
        title="Too Many Arguments!",
        description=f"You input too many arguments for `{prefix}{failed_command}`.\nTry calling `{prefix}help` if you're having trouble."
    )

    return embed


def handle_bad_argument(error: commands.BadArgument, prefix: str) -> discord.Embed:
    message = str(error).replace('"', '`')
    embed = discord.Embed(
        title="Bad Argument(s)!",
        description=f"{message}\nTry calling `{prefix}help` if you're having trouble."
    )

    return embed


def handle_generic_error() -> discord.Embed:
    embed = discord.Embed(
        title="Error!",
        description="Hmm, I don't know what happened here."
    )

    return embed


def handle_error(
    bot: Bot,
    error: commands.errors,
    failed_command: str,
    prefix: str,
    color: int
) -> discord.Embed:
    if isinstance(error, commands.CommandNotFound):
        embed = handle_command_not_found(bot, error, prefix)
    elif isinstance(error, commands.CommandOnCooldown):
        embed = handle_command_on_cooldown(error)
    elif isinstance(error, commands.MemberNotFound):
        embed = handle_member_not_found(error)
    elif isinstance(error, MemberBlacklisted):
        embed = handle_member_blacklisted(error)
    elif isinstance(error, commands.NotOwner):
        embed = handle_not_owner(failed_command, prefix)
    elif isinstance(error, commands.MissingPermissions):
        embed = handle_missing_permissions(error)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = handle_missing_required_argument(error, prefix)
    elif isinstance(error, commands.TooManyArguments):
        embed = handle_too_many_arguments(failed_command, prefix)
    elif isinstance(error, commands.BadArgument):
        embed = handle_bad_argument(error, prefix)
    else:
        embed = handle_generic_error()

    embed.color = color
    return embed
