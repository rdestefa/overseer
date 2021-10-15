# overseer.cogs.owner

import json
import logging

from utils.configs import load_config

import discord
from discord.ext import commands

from utils import moderation

# Color, and logger configs.
colors = load_config("colors")
logger = logging.getLogger()


class Owner(commands.Cog, name="owner"):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        name="blacklist",
        usage="blacklist",
        brief="Print the Overseer's blacklist."
    )
    async def blacklist(self, context):
        """
        Add or remove users from the Overseer's blacklist.
        Blacklisted users won't be able to issue commands to the Overseer.
        Using this command without arguments will print the current blacklist.
        """
        if context.invoked_subcommand is None:
            with open("lists/blacklist.json") as file:
                blacklist = json.load(file)

            n_ids = len(blacklist["ids"])
            embed = discord.Embed(
                title=(f"There {'is' if n_ids == 1 else 'are'} currently " +
                       f"{n_ids} blacklisted ID{'' if n_ids == 1 else 's'}"),
                description=f"{', '.join(str(id) for id in blacklist['ids'])}",
                color=colors["black"]
            )
            await context.send(embed=embed)

    @blacklist.command(
        name="add",
        usage="add <@user>",
        brief="Add a user to the blacklist."
    )
    @commands.is_owner()
    async def blacklist_add(self, context, member: discord.Member = None):
        """
        Add a user to the Overseer's blacklist.
        """
        try:
            with open("lists/blacklist.json") as file:
                blacklist = json.load(file)

            # There shouldn't be duplicates in the blacklist.
            if member.id in blacklist['ids']:
                logger.warning("%s is already blacklisted", member.name)
                embed = discord.Embed(
                    title="User Already Blacklisted!",
                    description=f"**{member.name}** is already blacklisted.",
                    color=colors["red"]
                )
                return

            moderation.blacklist_add(member.id)
        except Exception as e:
            logger.error(
                "Failed to blacklist %s (%s): %s",
                member.name,
                type(e).__name__,
                str(e)
            )
            embed = discord.Embed(
                title="Error!",
                description=("Something went wrong when trying to add " +
                             f"**{member.name}** to the blacklist."),
                color=colors["red"]
            )
        else:
            with open("lists/blacklist.json") as file:
                blacklist = json.load(file)

            n_ids = len(blacklist["ids"])
            embed = discord.Embed(
                title="User Blacklisted",
                description=(f"**{member.name}** has been successfully " +
                             "added to the blacklist."),
                color=colors["green"]
            )
            embed.set_footer(
                text=(f"There {'is' if n_ids == 1 else 'are'} currently " +
                      f"{n_ids} blacklisted user{'' if n_ids == 1 else 's'}")
            )
        finally:
            await context.send(embed=embed)

    @blacklist.command(
        name="remove",
        usage="remove <@user>",
        brief="Remove a user from the blacklist."
    )
    @commands.is_owner()
    async def blacklist_remove(self, context, member: discord.Member = None):
        """
        Remove a user from the Overseer's blacklist.
        """
        try:
            moderation.blacklist_remove(member.id)
        except ValueError as e:
            logger.error(
                "%s is not in the blacklist (%s): %s",
                member.name,
                type(e).__name__,
                str(e)
            )
            embed = discord.Embed(
                title="User Not Blacklisted!",
                description=f"**{member.name}** is not in the blacklist.",
                color=colors["red"]
            )
        except Exception as e:
            logger.error(
                "Failed to remove %s from blacklist (%s): %s",
                member.name,
                type(e).__name__,
                str(e)
            )
            embed = discord.Embed(
                title="Error!",
                description=("Something went wrong when trying to remove " +
                             f"**{member.name}** from the blacklist."),
                color=colors["red"]
            )
        else:
            with open("lists/blacklist.json") as file:
                blacklist = json.load(file)

            n_ids = len(blacklist["ids"])
            embed = discord.Embed(
                title="User Removed From Blacklist",
                description=(f"**{member.name}** has been successfully " +
                             "removed from the blacklist."),
                color=colors["green"]
            )
            embed.set_footer(
                text=(f"There {'is' if n_ids == 1 else 'are'} currently " +
                      f"{n_ids} blacklisted user{'' if n_ids == 1 else 's'}")
            )
        finally:
            await context.send(embed=embed)

    @commands.command(
        name="shutdown",
        usage="shutdown",
        brief="Shut down the Overseer...for now."
    )
    @commands.is_owner()
    async def shutdown(self, context):
        """
        Shut down the Overseer bot. Only the Overseer's owner can do this.
        """
        logger.info("Shutting down the Overseer")
        embed = discord.Embed(
            description="Shutting down :wave:. We'll meet again.",
            color=colors["green"]
        )
        await context.send(embed=embed)
        await self.bot.close()


def setup(bot):
    bot.add_cog(Owner(bot))
