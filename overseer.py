# overseer.py

# This is the main execution file for the Overseer Discord bot

import json
import logging
import logging.config
import os
import platform
import sys
import yaml

import Levenshtein as lev

import discord
from discord.ext import commands
from discord.ext.commands import Bot


# -------------------------- CONFIGS AND INTENTS ---------------------------- #

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
        logger = logging.getLogger()

"""
Set up bot intents (events restrictions)

Default Intents:
intents.messages = True
intents.reactions = True
intents.guilds = True
intents.emojis = True
intents.bans = True
intents.guild_typing = False
intents.typing = False
intents.dm_messages = False
intents.dm_reactions = False
intents.dm_typing = False
intents.guild_messages = True
intents.guild_reactions = True
intents.integrations = True
intents.invites = True
intents.voice_states = False
intents.webhooks = False

Privileged Intents (Needs to be enabled on dev page):
intents.presences = False
intents.members = False
"""
intents = discord.Intents.default()
intents.members = True
intents.presences = True

# Initialize bot instance
bot = Bot(command_prefix=config["bot_prefix"], intents=intents)


# --------------------------- STARTUP EXECUTION ----------------------------- #


# Executes on initial load of the Overseer
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
    await bot.change_presence(activity=discord.Game("itself"))


"""Set up the game status task of the bot
@tasks.loop(minutes=1.0)
async def status_task():
    statuses = ["with you!", "with someone!",
                f"{config['bot_prefix']}help", "with humans!"]
    await bot.change_presence(activity=discord.Game(random.choice(statuses)))
"""


# Removes the default help command of discord.py to enable custom help command
bot.remove_command("help")

if __name__ == "__main__":
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            extension = file[:-3]
            try:
                bot.load_extension(f"cogs.{extension}")
                logger.debug("Loaded extension %s", extension)
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                logger.error(
                    "Failed to load extention %s: %s",
                    extension,
                    exception
                )


# ---------------------------- EVENT HANDLERS ------------------------------- #


# Executes every time someone sends a message, with or without the prefix
@bot.event
async def on_message(message):
    # Ignores if a command is being executed by a bot or by the Overseer itself
    if message.author == bot.user or message.author.bot:
        return
    # Ignores if a command is being executed by a blacklisted user
    with open("blacklist.json") as file:
        blacklist = json.load(file)
    if message.author.id in blacklist["ids"]:
        return
    await bot.process_commands(message)


# Executes every time a command has been *successfully* executed
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


# Executes every time a valid command raises an error
@bot.event
async def on_command_error(context, error):
    failedCommand = context.invoked_with
    logger.error("Failed to execute %s: %s", failedCommand, str(error))

    if isinstance(error, commands.CommandNotFound):
        # Don't use failedCommand in case the error was raised from !help
        invalidCommand = str(error).split()[1].strip('"')

        # Calculate Levenshtein distance from valid commands for recommendation
        cmds = list(bot.commands)
        lev_dists = [lev.distance(invalidCommand, str(cmd))
                     / max(len(invalidCommand), len(str(cmd))) for cmd in cmds]
        lev_min = min(lev_dists)

        # Build error message
        description = f"I don't recognize the `{config['bot_prefix']}{invalidCommand}` command.\n"
        if lev_min <= 0.5:
            description += f"Did you mean `{config['bot_prefix']}{cmds[lev_dists.index(lev_min)]}`?"
        else:
            description += f"Try calling `{config['bot_prefix']}help` for a list of valid commands."

        # Send message
        embed = discord.Embed(
            title="Command Not Found!",
            description=description,
            color=0xE02B2B
        )
        await context.send(embed=embed)
    elif isinstance(error, commands.MemberNotFound):
        invalid_member = str(error).split()[1].strip('"')
        embed = discord.Embed(
            title="Member Not Found!",
            description=f"I looked everywhere, but I couldn't find `{invalid_member}` in the server.",
            color=0xE02B2B
        )
        await context.send(embed=embed)
    elif isinstance(error, commands.CommandOnCooldown):
        minutes, seconds = divmod(error.retry_after, 60)
        hours, minutes = divmod(minutes, 60)
        hours = hours % 24
        embed = discord.Embed(
            title="Hey! Slow down!",
            description=f"You can use this command again in {f'{round(hours)} hours' if round(hours) > 0 else ''} {f'{round(minutes)} minutes' if round(minutes) > 0 else ''} {f'{round(seconds)} seconds' if round(seconds) > 0 else ''}.",
            color=0xE02B2B
        )
        await context.send(embed=embed)
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="Permissions Error!",
            description="You are missing the permission(s) `" + "`, `".join(
                error.missing_perms) + "` to execute this command!",
            color=0xE02B2B
        )
        await context.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="Missing Argument!",
            description=f"You forgot the following argument: `{error.param}`.\nTry calling `{config['bot_prefix']}help` if you're having trouble.",
            color=0xE02B2B
        )
        await context.send(embed=embed)
    elif isinstance(error, commands.TooManyArguments):
        embed = discord.Embed(
            title="Too Many Arguments!",
            description=f"You input too many arguments for `{config['bot_prefix']}{failedCommand}`.\nTry calling `{config['bot_prefix']}help` if you're having trouble.",
            color=0xE02B2B
        )
        await context.send(embed=embed)
    elif isinstance(error, commands.BadArgument):
        message = str(error).replace('"', '`')
        embed = discord.Embed(
            title="Bad Argument(s)!",
            description=f"{message}\nTry calling `{config['bot_prefix']}help` if you're having trouble.",
            color=0xE02B2B
        )
        await context.send(embed=embed)
    else:
        embed = discord.Embed(
            title="Error!",
            description="Hmm, I don't know what happened here.",
            color=0xE02B2B
        )
        await context.send(embed=embed)


# Run the Overseer with its token
bot.run(config["token"])
