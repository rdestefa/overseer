# overseer.bot

# This is the main execution file for the Overseer Discord bot.

import asyncio
import glom
import json
import os
import platform

from cogs import load_cogs
from utils import custom_exceptions
from utils.configs import load_bot_configs, load_config
from utils.error_handlers import handle_error

import discord
from discord.ext.commands import Bot


# ------------------------- BOT CONFIGS AND INTENTS ------------------------- #


config, logger = load_bot_configs()
colors = load_config("colors")
activity = discord.Activity(name="You", type=discord.ActivityType.watching)

# Currently all intents are enabled, but custom intents can be set with
# discord.Intents(**config["intents"]).
intents = discord.Intents.all()

# Initialize bot instance.
bot = Bot(
    owner_ids=set(config["owners"]),      # Owners of the Overseer.
    command_prefix=config["bot_prefix"],  # Set command prefix.
    intents=intents,                      # Set intents.
    activity=activity,                    # Set the Overseer's status.
    help_command=None,                    # Remove default help command.
    strip_after_prefix=True               # !   <command> becomes !<command>.
)


# ------------------------------ GLOBAL CHECKS ------------------------------ #


# Ignore commands issued by a blacklisted user.
@bot.check
async def not_blacklisted(context):
    with open("lists/blacklist.json", "r") as file:
        blacklist = json.load(file)

    user_id = glom.glom(context, "message.author.id", default=None)
    if user_id is not None and user_id in blacklist["ids"]:
        raise custom_exceptions.MemberBlacklisted(context.message.author)

    return True


# ----------------------------- EVENT HANDLERS ------------------------------ #


# Executes on initial load of the Overseer.
@bot.event
async def on_ready():
    await bot.wait_until_ready()

    logger.info("Logged in as %s", bot.user.name)
    logger.info("Discord.py API version: %s", discord.__version__)
    logger.info("Python version: %s", platform.python_version())
    logger.info(
        "Running on: %s %s (%s)",
        platform.system(),
        platform.release(),
        os.name
    )


# Executes every time someone sends a message, with or without the prefix.
@bot.event
async def on_message(message):
    # Ignore commands being executed by the Overseer or another bot.
    if message.author == bot.user or message.author.bot:
        return

    # Process any commmands if they were issued.
    await bot.process_commands(message)


# Executes every time a command has been *successfully* executed.
@bot.event
async def on_command_completion(context):
    logger.debug(
        "%s (ID: %s) executed %s in %s (ID: %s)",
        context.message.author,
        context.message.author.id,
        context.command.qualified_name,
        glom.glom(context, "guild.name", default="no server"),
        glom.glom(context, "message.guild.id", default="None")
    )


# Executes every time a valid command raises an error.
@bot.event
async def on_command_error(context, error):
    # `command.qualified_name` won't populate on a nonexistent command.
    failed_command = glom.glom(
        context, glom.Coalesce("command.qualified_name", "invoked_with"))
    logger.error(
        "%s (ID: %s) failed to execute %s (%s): %s",
        context.message.author,
        context.message.author.id,
        failed_command,
        type(error).__name__,
        str(error)
    )

    # Get custom message based on the error and send to the user.
    embed = handle_error(bot, error, failed_command,
                         config["bot_prefix"], colors["red"])
    await context.send(embed=embed)


# ---------------------------- STARTUP EXECUTION ---------------------------- #

async def main():
    await load_cogs(bot)
    async with bot:
        await bot.start(config["token"])


if __name__ == "__main__":
    # TODO: Add support for slash commands after official release.
    asyncio.run(main())
