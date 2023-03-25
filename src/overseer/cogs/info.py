# overseer.cogs.info

import logging
import platform

from utils.configs import load_config, load_config_attr

import discord
from discord.ext import commands

# Color and logger configs.
colors = load_config("colors")
logger = logging.getLogger()


class Info(commands.Cog, name="info"):
    """
    Cog for displaying basic info about the Overseer and its servers.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name="info",
        aliases=["botinfo"],
        usage="info",
        brief="Get basic information about the Overseer."
    )
    async def info(self, context: commands.Context) -> None:
        """
        Get some useful (or not) basic information about the Overseer.
        """
        embed = discord.Embed(
            title="I am the Overseer",
            description="My configurations are listed below",
            color=colors["green"]
        )
        embed.add_field(name="Owner", value="Ryan Creenis#8374")
        embed.add_field(
            name="Python Version",
            value=f"{platform.python_version()}"
        )
        embed.add_field(
            name="Command Prefix",
            value=f"{self.bot.command_prefix}"
        )
        embed.set_footer(text=f"Requested by {context.message.author.name}")

        await context.send(embed=embed)

    @commands.hybrid_command(
        name="invite",
        usage="invite",
        brief="Get the Overseer's invite link."
    )
    async def invite(self, context: commands.Context) -> None:
        """
        Get the Overseer's invite link to share with other servers.
        """
        app_id = load_config_attr("overseer", "application_id")
        invite_link = ("https://discordapp.com/oauth2/authorize?&"
                       + f"client_id={app_id}&scope=bot&permissions=470150263")
        embed = discord.Embed(
            description=f"Invite me by clicking [here]({invite_link}).",
            color=colors["purple"]
        )

        try:
            # Requires permission to DM users.
            await context.author.send(embed=embed)
            await context.send(f"Psst! {context.author.mention}, I DM'd you!")
        except discord.Forbidden:
            logger.warning(
                "Overseer doesn't have permission to DM %s", context.author)
            await context.send(embed=embed)

    @commands.hybrid_command(
        name="ping",
        usage="ping",
        brief="Check if the Overseer is alive."
    )
    async def ping(self, context: commands.Context) -> None:
        """
        Check if the Overseer is alive.
        """
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"My latency is {round(self.bot.latency * 1000)} ms.",
            color=colors["green"]
        )
        await context.send(embed=embed)

    @commands.hybrid_command(
        name="serverinfo",
        usage="serverinfo",
        brief="Get basic information about the server."
    )
    async def serverinfo(self, context: commands.Context) -> None:
        """
        Get some useful (or not) basic information about the server.
        """
        if not (server := context.message.guild):
            await context.send(embed=discord.Embed(
                title="Not in a Server!",
                description="Your command didn't come from within a server.",
                color=colors["red"]
            ))
            return

        roles = [x.name for x in server.roles]
        role_count = len(roles)

        if role_count > 50:
            roles = roles[:50]
            roles.append(f">>>> Displaying[50/{role_count}] Roles")

        roles = ", ".join(roles)
        time = str(server.created_at).split(" ")[0]

        embed = discord.Embed(
            title="**Server Name**",
            description=f"{server}",
            color=colors["green"]
        )
        embed.set_thumbnail(url=server.icon)
        embed.add_field(name="Owner", value=f"{server.owner}")
        embed.add_field(name="Server ID", value=server.id)
        embed.add_field(
            name=f"Roles ({role_count})",
            value=roles,
            inline=False
        )
        embed.add_field(name="Member Count", value=server.member_count)
        embed.add_field(
            name="Text / Voice Channels",
            value=f"{len(server.channels)}"
        )
        embed.set_footer(text=f"Created on {time}")

        await context.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Info(bot))
