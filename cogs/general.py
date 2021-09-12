# general.py

import json
import logging
import logging.config
import os
import platform
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


class General(commands.Cog, name="general"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="info",
        aliases=["botinfo"],
        usage="info",
        brief="Get basic information about the Overseer."
    )
    async def info(self, context):
        """
        Get some useful (or not) basic information about the Overseer.
        """
        embed = discord.Embed(
            description="I belong to the almighty Creenis",
            color=0x42F56C
        )
        embed.set_author(
            name="Bot Information"
        )
        embed.add_field(
            name="Owner",
            value="Ryan Creenis#8374",
            inline=True
        )
        embed.add_field(
            name="Python Version",
            value=f"{platform.python_version()}",
            inline=True
        )
        embed.add_field(
            name="Command Prefix",
            value=f"{config['bot_prefix']}",
            inline=True
        )
        embed.set_footer(
            text=f"Requested by {context.message.author}"
        )
        await context.send(embed=embed)

    @commands.command(
        name="serverinfo",
        usage="serverinfo",
        brief="Get basic information about the server."
    )
    async def serverinfo(self, context):
        """
        Get some useful (or not) basic information about the server.
        """
        server = context.message.guild
        roles = [x.name for x in server.roles]
        role_length = len(roles)
        if role_length > 50:
            roles = roles[:50]
            roles.append(f">>>> Displaying[50/{len(roles)}] Roles")
        roles = ", ".join(roles)
        channels = len(server.channels)
        time = str(server.created_at)
        time = time.split(" ")
        time = time[0]

        embed = discord.Embed(
            title="**Server Name**",
            description=f"{server}",
            color=0x42F56C
        )
        embed.set_thumbnail(
            url=server.icon_url
        )
        embed.add_field(
            name="Owner",
            value=f"{server.owner}"
        )
        embed.add_field(
            name="Server ID",
            value=server.id
        )
        embed.add_field(
            name=f"Roles ({role_length})",
            value=roles,
            inline=False
        )
        embed.add_field(
            name="Member Count",
            value=server.member_count
        )
        embed.add_field(
            name="Text/Voice Channels",
            value=f"{channels}"
        )
        embed.set_footer(
            text=f"Created on {time}"
        )
        await context.send(embed=embed)

    @commands.command(
        name="ping",
        usage="ping",
        brief="Check if the Overseer is alive."
    )
    async def ping(self, context):
        """
        Check if the Overseer is alive.
        """
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Overseer's latency is {round(self.bot.latency * 1000)}ms.",
            color=0x42F56C
        )
        await context.send(embed=embed)

    @commands.command(
        name="invite",
        usage="invite",
        brief="Get the Overseer's invite link."
    )
    async def invite(self, context):
        """
        Get the Overseer's invite link to share with other servers.
        """
        embed = discord.Embed(
            description=f"Invite me by clicking [here](https://discordapp.com/oauth2/authorize?&client_id={config['application_id']}&scope=bot&permissions=470150263).",
            color=0xD75BF4
        )

        try:
            # Needs permissions to do this
            await context.author.send(embed=embed)
            await context.send(f"Psst! {context.author.mention}, I sent you a private message!")
        except discord.Forbidden:
            logger.warning(
                "Overseer doesn't have permission to DM %s", context.author)
            await context.send(embed=embed)


def setup(bot):
    bot.add_cog(General(bot))
