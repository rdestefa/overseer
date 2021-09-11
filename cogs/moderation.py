# moderation.py

import json
import logging
import logging.config
import os
import sys
import yaml

import discord
from discord.ext import commands

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


class Moderation(commands.Cog, name="moderation"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='kick',
        usage="kick <@user> <reason>",
        pass_context=True)
    @commands.has_permissions(kick_members=True)
    async def kick(self, context, member: discord.Member, *, reason="Not specified"):
        """
        Kick a user out of the server. Must have kick permissions.
        """
        # Remove any quotes around the reason
        reason = reason.strip('"').strip("'")
        if member.guild_permissions.administrator:
            logger.warning(
                "Cannot kick %s: Users with Admin permissions cannot be kicked.", member)
            embed = discord.Embed(
                title="Error!",
                description=f"**{member.name}** has Admin permissions.",
                color=0xE02B2B
            )
            await context.send(embed=embed)
        else:
            try:
                await member.kick(reason=reason)
                embed = discord.Embed(
                    title="User Kicked!",
                    description=f"**{member}** was kicked by **{context.message.author}**!",
                    color=0x42F56C
                )
                embed.add_field(
                    name="Reason",
                    value=reason
                )
                await context.send(embed=embed)
                try:
                    await member.send(
                        f"You were kicked by **{context.message.author}**!\nReason: {reason}"
                    )
                except Exception as e:
                    logger.error('Failed to DM %s: %s', member, str(e))
            except Exception as e:
                logger.error('Failed to kick %s: %s', member, str(e))
                embed = discord.Embed(
                    title="Error!",
                    description="An error occurred while trying to kick the user. Make sure my role supersedes that of the user you want to kick.",
                    color=0xE02B2B
                )
                await context.message.channel.send(embed=embed)

    @commands.command(name="nick", usage="nick")
    @commands.has_permissions(manage_nicknames=True)
    async def nick(self, context, member: discord.Member, *, nickname=None):
        """
        Change the nickname of a user on a server. Must have permission to manage nicknames.
        """
        try:
            await member.edit(nick=nickname)
            embed = discord.Embed(
                title="Changed Nickname!",
                description=f"**{member}'s** new nickname is **{nickname}**!",
                color=0x42F56C
            )
            await context.send(embed=embed)
        except Exception as e:
            logger.error('Failed to change nickname of %s: %s', member, str(e))
            embed = discord.Embed(
                title="Error!",
                description=f"An error occurred while trying to change the nickname of **{member}**. Make sure my role is above the role of the user you want to change the nickname.",
                color=0xE02B2B
            )
            await context.message.channel.send(embed=embed)

    @commands.command(name="ban", usage="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, context, member: discord.Member, *, reason="Not specified"):
        """
        Bans a user from the server. Must have ban permissions.
        """
        try:
            if member.guild_permissions.administrator:
                embed = discord.Embed(
                    title="Error!",
                    description="User has Admin permissions.",
                    color=0xE02B2B
                )
                await context.send(embed=embed)
            else:
                await member.ban(reason=reason)
                embed = discord.Embed(
                    title="User Banned!",
                    description=f"**{member}** was banned by **{context.message.author}**!",
                    color=0x42F56C
                )
                embed.add_field(
                    name="Reason",
                    value=reason
                )
                await context.send(embed=embed)
                await member.send(f"You were banned by **{context.message.author}**!\nReason: {reason}")
        except Exception as e:
            logger.error('Failed to ban %s: %s', member, str(e))
            embed = discord.Embed(
                title="Error!",
                description="An error occurred while trying to ban the user. Make sure my role is above the role of the user you want to ban.",
                color=0xE02B2B
            )
            await context.send(embed=embed)

    @commands.command(name="warn", usage="warn")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, context, member: discord.Member, *, reason="Not specified"):
        """
        Direct messages a user with a warning.
        """
        embed = discord.Embed(
            title="User Warned!",
            description=f"**{member}** was warned by **{context.message.author}**!",
            color=0x42F56C
        )
        embed.add_field(
            name="Reason",
            value=reason
        )
        await context.send(embed=embed)
        try:
            await member.send(f"You were warned by **{context.message.author}**!\nReason: {reason}")
        except Exception as e:
            logger.error('Failed to warn %s: %s', member, str(e))

    @commands.command(name="purge", usage="purge")
    @commands.has_permissions(manage_messages=True, manage_channels=True)
    async def purge(self, context, amount):
        """
        Delete a number of messages.
        """
        try:
            amount = int(amount)
        except Exception as e:
            logger.error("Only integers are accepted by purge: %s", str(e))
            embed = discord.Embed(
                title="Error!",
                description=f"`{amount}` is not a valid integer.",
                color=0xE02B2B
            )
            await context.send(embed=embed)
            return
        if amount < 1:
            embed = discord.Embed(
                title="Error!",
                description=f"`{amount}` is not a valid number.",
                color=0xE02B2B
            )
            await context.send(embed=embed)
            return
        purged_messages = await context.message.channel.purge(limit=amount)
        embed = discord.Embed(
            title="Chat Cleared!",
            description=f"**{context.message.author}** cleared **{len(purged_messages)}** messages!",
            color=0x42F56C
        )
        await context.send(embed=embed)


def setup(bot):
    bot.add_cog(moderation(bot))
