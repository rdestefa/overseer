# overseer.cogs.info

import logging
import platform

from helpers.config_helpers import load_config

import discord
from discord.ext import commands

# Color, and logger configs.
colors = load_config("colors")
logger = logging.getLogger()


class Info(commands.Cog, name="info"):
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
            color=colors["green"]
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
            value=f"{self.bot.command_prefix}",
            inline=True
        )
        embed.set_footer(
            text=f"Requested by {context.message.author}"
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
        # TODO: Fix to enable custom attribute fetching from bot configs.
        embed = discord.Embed(
            description=f"Invite me by clicking [here](https://discordapp.com/oauth2/authorize?&client_id={'885745752893186068'}&scope=bot&permissions=470150263).",
            color=colors["purple"]
        )

        try:
            # Needs permissions to do this.
            await context.author.send(embed=embed)
            await context.send(f"Psst! {context.author.mention}, I sent you a private message!")
        except discord.Forbidden:
            logger.warning(
                "Overseer doesn't have permission to DM %s", context.author)
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
            description=f"The Overseer's latency is {round(self.bot.latency * 1000)} ms.",
            color=colors["green"]
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
            color=colors["green"]
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


def setup(bot):
    bot.add_cog(Info(bot))
