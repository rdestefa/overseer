# owner.py

import json
import logging
import logging.config
import os
import sys
import yaml

import discord
from discord.ext import commands

from helpers import json_helpers

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


class owner(commands.Cog, name="owner"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="shutdown", usage="shutdown")
    async def shutdown(self, context):
        """
        Shut down the Overseer...for now.
        """
        if context.message.author.id in config["owners"]:
            embed = discord.Embed(
                description="Shutting down :wave:. We'll meet again.",
                color=0x42F56C
            )
            await context.send(embed=embed)
            await self.bot.close()
        else:
            embed = discord.Embed(
                title="Error!",
                description="You don't have permission to shut down the Overseer.",
                color=0xE02B2B
            )
            await context.send(embed=embed)

    @commands.command(name="say", aliases=["echo"], usage="say")
    async def say(self, context, *, args):
        """
        The Overseer will say what you're thinking so you don't have to.
        """
        if context.message.author.id in config["owners"]:
            await context.send(args)
        else:
            embed = discord.Embed(
                title="Error!",
                description="You don't have the permission to use this command.",
                color=0xE02B2B
            )
            await context.send(embed=embed)

    @commands.command(name="embed", usage="embed")
    async def embed(self, context, *, args):
        """
        The Overseer will say what you're thinking, but within embeds.
        """
        if context.message.author.id in config["owners"]:
            embed = discord.Embed(
                description=args,
                color=0x42F56C
            )
            await context.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Error!",
                description="You don't have the permission to use this command.",
                color=0xE02B2B
            )
            await context.send(embed=embed)

    @commands.group(name="blacklist", usage="blacklist")
    async def blacklist(self, context):
        """
        Blacklist a user or remove one from the blacklist.
        Blacklisted users won't be able to issue commands to the Overseer.
        """
        if context.invoked_subcommand is None:
            with open("blacklist.json") as file:
                blacklist = json.load(file)
            embed = discord.Embed(
                title=f"There are currently {len(blacklist['ids'])} blacklisted IDs",
                description=f"{', '.join(str(id) for id in blacklist['ids'])}",
                color=0x0000FF
            )
            await context.send(embed=embed)

    @blacklist.command(name="add", usage="add")
    async def blacklist_add(self, context, member: discord.Member = None):
        """
        Add a user to the Overseer's blacklist.
        """
        if context.message.author.id in config["owners"]:
            userID = member.id
            try:
                with open("blacklist.json") as file:
                    blacklist = json.load(file)
                if (userID in blacklist['ids']):
                    embed = discord.Embed(
                        title="Error!",
                        description=f"**{member.name}** is already in the blacklist.",
                        color=0xE02B2B
                    )
                    await context.send(embed=embed)
                    return
                json_helpers.add_user_to_blacklist(userID)
                embed = discord.Embed(
                    title="User Blacklisted",
                    description=f"**{member.name}** has been successfully added to the blacklist",
                    color=0x42F56C
                )
                with open("blacklist.json") as file:
                    blacklist = json.load(file)
                embed.set_footer(
                    text=f"There are now {len(blacklist['ids'])} users in the blacklist"
                )
                await context.send(embed=embed)
            except:
                embed = discord.Embed(
                    title="Error!",
                    description=f"An unknown error occurred when trying to add **{member.name}** to the blacklist.",
                    color=0xE02B2B
                )
                await context.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Error!",
                description="You don't have the permission to use this command.",
                color=0xE02B2B
            )
            await context.send(embed=embed)

    @blacklist.command(name="remove", usage="remove")
    async def blacklist_remove(self, context, member: discord.Member = None):
        """
        Remove a user from the Overseer's blacklist.
        """
        if context.message.author.id in config["owners"]:
            userID = member.id
            try:
                json_helpers.remove_user_from_blacklist(userID)
                embed = discord.Embed(
                    title="User removed from blacklist",
                    description=f"**{member.name}** has been successfully removed from the blacklist",
                    color=0x42F56C
                )
                with open("blacklist.json") as file:
                    blacklist = json.load(file)
                embed.set_footer(
                    text=f"There are now {len(blacklist['ids'])} users in the blacklist"
                )
                await context.send(embed=embed)
            except:
                embed = discord.Embed(
                    title="Error!",
                    description=f"**{member.name}** is not in the blacklist.",
                    color=0xE02B2B
                )
                await context.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Error!",
                description="You don't have the permission to use this command.",
                color=0xE02B2B
            )
            await context.send(embed=embed)


def setup(bot):
    bot.add_cog(owner(bot))
