# overseer.cogs.owner

import json
import logging

from helpers.config_helpers import load_bot_configs, load_colors

import discord
from discord.ext import commands

from helpers import json_helpers

# Bot, color, and logger configs.
config = load_bot_configs()
colors = load_colors()
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
            with open("blacklist.json") as file:
                blacklist = json.load(file)

            embed = discord.Embed(
                title=f"There are currently {len(blacklist['ids'])} blacklisted IDs",
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
            with open("blacklist.json") as file:
                blacklist = json.load(file)

            # There shouldn't be duplicates in the blacklist.
            if member.id in blacklist['ids']:
                logger.warning("%s is already blacklisted", member.name)
                embed = discord.Embed(
                    title="User Already Blacklisted!",
                    description=f"**{member.name}** is already in the blacklist.",
                    color=colors["red"]
                )
                await context.send(embed=embed)
                return

            json_helpers.add_user_to_blacklist(member.id)
        except Exception as e:
            logger.error(
                "Failed to blacklist %s (%s): %s",
                member.name,
                type(e).__name__,
                str(e)
            )
            embed = discord.Embed(
                title="Error!",
                description=f"Something went wrong when trying to add **{member.name}** to the blacklist: {str(e)}",
                color=colors["red"]
            )
        else:
            with open("blacklist.json") as file:
                blacklist = json.load(file)

            embed = discord.Embed(
                title="User Blacklisted",
                description=f"**{member.name}** has been successfully added to the blacklist",
                color=colors["green"]
            )
            embed.set_footer(
                text=f"There are now {len(blacklist['ids'])} users in the blacklist"
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
            json_helpers.remove_user_from_blacklist(member.id)
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
                description=f"Something went wrong when trying to remove **{member.name}** from the blacklist: {str(e)}",
                color=colors["red"]
            )
        else:
            with open("blacklist.json") as file:
                blacklist = json.load(file)

            embed = discord.Embed(
                title="User Removed From Blacklist",
                description=f"**{member.name}** has been successfully removed from the blacklist.",
                color=colors["green"]
            )
            embed.set_footer(
                text=f"There are now {len(blacklist['ids'])} users in the blacklist."
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
