# overseer.cogs.moderation

import logging

from helpers.config_helpers import load_bot_configs, load_colors

import discord
from discord.ext import commands

# Bot, color, and logger configs.
config = load_bot_configs()
colors = load_colors()
logger = logging.getLogger()


class Moderation(commands.Cog, name="moderation"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="ban",
        usage="ban <@user> <reason>",
        brief="Ban a user from the server."
    )
    @commands.has_permissions(ban_members=True)
    async def ban(self, context, member: discord.Member, *, reason="Not specified"):
        """
        Ban a user from the server. Must have ban permissions.
        """
        try:
            if member.guild_permissions.administrator:
                logger.warning(
                    "Cannot ban %s: Users with Admin permissions cannot be banned.", member)
                embed = discord.Embed(
                    title="Error!",
                    description="User has Admin permissions.",
                    color=colors["red"]
                )
            else:
                await member.ban(reason=reason)
                embed = discord.Embed(
                    title="User Banned!",
                    description=f"**{member}** was banned by **{context.message.author}**!",
                    color=colors["green"]
                )
                embed.add_field(
                    name="Reason",
                    value=reason
                )
                await member.send(f"You were banned by **{context.message.author}**!\nReason: {reason}")
        except Exception as e:
            logger.error(
                "Failed to ban %s (%s): %s", member, type(e).__name__, str(e))
            embed = discord.Embed(
                title="Error!",
                description="An error occurred while trying to ban the user. Make sure my role is above the role of the user you want to ban.",
                color=colors["red"]
            )
        finally:
            await context.send(embed=embed)

    @commands.command(
        name='kick',
        usage="kick <@user> <reason>",
        brief="Kick a user out of the server."
    )
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
                color=colors["red"]
            )
            await context.send(embed=embed)
        else:
            try:
                await member.kick(reason=reason)
                try:
                    await member.send(
                        f"You were kicked by **{context.message.author}**!\nReason: {reason}")
                except Exception as e:
                    logger.error(
                        "Failed to DM %s (%s): %s", member, type(e).__name__, str(e))
            except Exception as e:
                logger.error(
                    "Failed to kick %s (%s): %s", member, type(e).__name__, str(e))
                embed = discord.Embed(
                    title="Error!",
                    description="An error occurred while trying to kick the user. Make sure my role supersedes that of the user you want to kick.",
                    color=colors["red"]
                )
            else:
                embed = discord.Embed(
                    title="User Kicked!",
                    description=f"**{member}** was kicked by **{context.message.author}**!",
                    color=colors["green"]
                )
                embed.add_field(name="Reason", value=reason)
            finally:
                await context.send(embed=embed)

    @commands.command(
        name="nick",
        usage="nick <@user> <nickname>",
        brief="Change the nickname of a user."
    )
    @commands.has_permissions(manage_nicknames=True)
    async def nick(self, context, member: discord.Member, *, nickname=None):
        """
        Change the nickname of a user on a server. Must have permission to manage nicknames.
        """
        try:
            await member.edit(nick=nickname)
        except Exception as e:
            logger.error(
                "Failed to change nickname of %s (%s): %s", member, type(e).__name__, str(e))
            embed = discord.Embed(
                title="Error!",
                description=f"An error occurred while trying to change the nickname of **{member}**. Make sure my role supersedes the role of the user for whom you want to change the nickname.",
                color=colors["red"]
            )
        else:
            embed = discord.Embed(
                title="Changed Nickname!",
                description=f"**{member}'s** new nickname is **{nickname}**!",
                color=colors["green"]
            )
        finally:
            await context.send(embed=embed)

    @commands.command(
        name="purge",
        usage="purge <number>",
        brief="Delete a number of messages."
    )
    @commands.has_permissions(manage_messages=True, manage_channels=True)
    async def purge(self, context, amount: int = 10):
        """
        Delete a number of messages in the channel. Defaults to 10 messages.
        If -1 is specified, then every message in the channel will be deleted.
        """
        if amount < 1 and amount != -1:
            logger.error(
                "Only positive integers or -1 are accepted by purge.")
            embed = discord.Embed(
                title="Error!",
                description=f"`{amount}` must be a positive integer or -1.",
                color=colors["red"]
            )
            await context.send(embed=embed)
            return

        limit = amount if amount > 0 else None
        purged_messages = await context.message.channel.purge(limit=limit)
        embed = discord.Embed(
            title="Chat Cleared!",
            description=f"**{context.message.author}** cleared **{len(purged_messages)}** messages!",
            color=colors["green"]
        )
        await context.send(embed=embed)

    @commands.command(
        name="warn",
        usage="warn <@user> <reason>",
        brief="Warn a user."
    )
    @commands.has_permissions(manage_messages=True)
    async def warn(self, context, member: discord.Member, *, reason="Not specified"):
        """
        Direct messages a user with a stern warning.
        """
        embed = discord.Embed(
            title="User Warned!",
            description=f"**{member}** was warned by **{context.message.author}**!",
            color=colors["yellow"]
        )
        embed.add_field(
            name="Reason",
            value=reason
        )
        await context.send(embed=embed)
        try:
            await member.send(f"You were warned by **{context.message.author}**!\nReason: {reason}")
        except Exception as e:
            logger.error(
                "Failed to warn %s (%s): %s", member, type(e).__name__, str(e))


def setup(bot):
    bot.add_cog(Moderation(bot))