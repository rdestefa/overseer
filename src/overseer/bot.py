# overseer.bot

# This is the main execution file for the Overseer Discord bot.

import json
import os
import platform

from cogs import load_cogs
from helpers.config_helpers import load_all_configs
from helpers.error_helpers import handle_error

import discord
from discord.ext.commands import Bot


# ------------------------- BOT CONFIGS AND INTENTS ------------------------- #


config, logger = load_all_configs()
activity = discord.Activity(name="You", type=discord.ActivityType.watching)

# Currently all intents are enabled, but custom intents can be set with
# discord.Intents(**config["intents"]).
intents = discord.Intents.all()

# Initialize bot instance
bot = Bot(
    command_prefix=config["bot_prefix"],    # Set command prefix.
    intents=intents,                        # Set intents.
    activity=activity,                      # Set the Overseer's status.
    help_command=None                       # Remove default help command.
)


# ---------------------------- STARTUP EXECUTION ---------------------------- #

if __name__ == "__main__":
    load_cogs(bot)


# Executes on initial load of the Overseer.
@bot.event
async def on_ready():
    logger.info("Logged in as %s", bot.user.name)
    logger.info("Discord.py API version: %s", discord.__version__)
    logger.info("Python version: %s", platform.python_version())
    logger.info(
        "Running on: %s %s (%s)",
        platform.system(),
        platform.release(),
        os.name
    )

"""Set up the game status task of the bot
@tasks.loop(minutes=1.0)
async def status_task():
    statuses = ["with you!", "with someone!",
                f"{config['bot_prefix']}help", "with humans!"]
    await bot.change_presence(activity=discord.Game(random.choice(statuses)))
"""


# ----------------------------- EVENT HANDLERS ------------------------------ #


# Executes every time someone sends a message, with or without the prefix.
@bot.event
async def on_message(message):
    # Ignores if a command is being executed by the Overseer or another bot.
    if message.author == bot.user or message.author.bot:
        return
    # Ignores if a command is being executed by a blacklisted user.
    with open("blacklist.json") as file:
        blacklist = json.load(file)
    if message.author.id in blacklist["ids"]:
        return
    await bot.process_commands(message)


# Executes every time a command has been *successfully* executed.
@bot.event
async def on_command_completion(ctx):
    fullCommandName = ctx.command.qualified_name
    executedCommand = str(fullCommandName.split(" ")[0])
    logger.debug(
        "Executed %s in %s (ID: %s) by %s (ID: %s)",
        executedCommand,
        ctx.guild.name,
        ctx.message.guild.id,
        ctx.message.author,
        ctx.message.author.id
    )


# Executes every time a valid command raises an error.
@bot.event
async def on_command_error(context, error):
    failedCommand = context.invoked_with
    logger.error("Failed to execute %s: %s", failedCommand, str(error))

    # Get custom message based on the error and send to the user.
    embed = handle_error(bot, error, failedCommand, config["bot_prefix"])
    await context.send(embed=embed)


# Run the Overseer with its token.
bot.run(config["token"])
