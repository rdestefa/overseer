# overseer.cogs.fun

import asyncio
import json
import logging
import random

from helpers.config_helpers import load_bot_configs, load_colors
from helpers.json_helpers import increment_gintama_count, reset_gintama_count

import aiohttp
import discord
from discord.ext import commands
from discord.ext.commands import BucketType

# Bot, color, and logger configs.
config = load_bot_configs()
colors = load_colors()
logger = logging.getLogger()


class Fun(commands.Cog, name="fun"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="bitcoin",
        usage="bitcoin",
        brief="Get the current price of Bitcoin."
    )
    async def bitcoin(self, context):
        """
        Get the current price of Bitcoin from coindesk.com.
        """
        url = "https://api.coindesk.com/v1/bpi/currentprice/BTC.json"
        # Async HTTP request.
        async with aiohttp.ClientSession() as session:
            raw_response = await session.get(url)
            response = await raw_response.text()
            response = json.loads(response)
            embed = discord.Embed(
                title=":information_source: Crypto",
                description=f"Bitcoin price is: ${response['bpi']['USD']['rate']}",
                color=colors["green"]
            )
            await context.send(embed=embed)

    """
    Why 1 and 86400?
    -> Because the user should be able to use the command *once* every *86400* seconds.

    Why BucketType.user?
    -> Because the cooldown only affects the current user. Other kinds of cooldowns:
      - BucketType.default for a global basis.
      - BucketType.user for a per-user basis.
      - BucketType.server for a per-server basis.
      - BucketType.channel for a per-channel basis.
    """

    @commands.command(
        name="dailyfact",
        usage="dailyfact",
        brief="Get your daily dose of knowledge."
    )
    @commands.cooldown(1, 86400, BucketType.user)
    async def dailyfact(self, context):
        """
        Get a random fact from the Internet. Can only run once per day per user.
        """
        # This will prevent the Overseer from stopping everything when making a web request.
        # See https://discordpy.readthedocs.io/en/stable/faq.html#how-do-i-make-a-web-request.
        async with aiohttp.ClientSession() as session:
            async with session.get("https://uselessfacts.jsph.pl/random.json?language=en") as request:
                if request.status == 200:
                    data = await request.json()
                    embed = discord.Embed(
                        description=data["text"], color=colors["purple"])
                    await context.send(embed=embed)
                else:
                    logger.warning(
                        'Failed to fetch a daily fact from the useless facts API. Error code: %s', request.status)
                    embed = discord.Embed(
                        title="Error!",
                        description="There's an issue with the useless facts API. Please try again later",
                        color=colors["red"]
                    )
                    await context.send(embed=embed)
                    # We need to reset the cooldown since the user didn't get their daily fact.
                    self.dailyfact.reset_cooldown(context)

    @commands.command(
        name="embed",
        usage="embed <message>",
        brief="The Overseer embeds what you're thinking."
    )
    async def embed(self, context, *, args):
        """
        The Overseer will say what you're thinking, but within embeds.
        """
        embed = discord.Embed(
            description=args,
            color=colors["green"]
        )
        await context.send(embed=embed)

    @commands.group(
        name="gintamacount",
        usage="gintamacount",
        brief="Keep track of Dec's Gintama references."
    )
    async def gintama_count(self, context):
        """
        Every time Declan mentions Gintama, keep track of it.
        """
        if context.invoked_subcommand is None:
            count = increment_gintama_count()
            count_str = f"{count} {'time' if count == 1 else 'times'}"
            embed = discord.Embed(
                title="Gintama Reference Counter",
                description=f"Declan has mentioned Gintama {count_str} in consecutive conversations.",
                color=colors["green"]
            )
            await context.send(embed=embed)

    @gintama_count.command(
        name="reset",
        usage="reset",
        brief="Resets Dec's Gintama reference counter."
    )
    async def gintama_count_clear(self, context):
        """
        If Declan hasn't mentioned Gintama during a conversation, reset his reference counter.
        """
        reset_gintama_count()
        embed = discord.Embed(
            title="No Gintama References Today",
            description="Declan didn't mention Gintama today, so we'll reset his reference counter.",
            color=colors["yellow"]
        )
        await context.send(embed=embed)

    @commands.command(
        name="poll",
        usage="poll <title>",
        brief="Create a poll that members can vote on."
    )
    async def poll(self, context, *, title):
        """
        Create a poll that members can vote on.
        The three default reactions are yes, no, and maybe.
        """
        embed = discord.Embed(
            title="A new poll has been created!",
            description=f"{title}",
            color=colors["green"]
        )
        embed.set_footer(
            text=f"Poll created by: {context.message.author} • React to vote!"
        )
        embed_message = await context.send(embed=embed)
        await embed_message.add_reaction("👍")
        await embed_message.add_reaction("👎")
        await embed_message.add_reaction("🤷")

    @commands.command(
        name="rps",
        usage="rps",
        brief="Play rock, paper, scissors with the Overseer."
    )
    async def rock_paper_scissors(self, context):
        """
        Play rock, paper, scissors with the me. It's a fight to the death!
        I don't like time-wasters, so you'll have 10 seconds to respond.
        """
        choices = {
            0: "rock",
            1: "paper",
            2: "scissors"
        }
        reactions = {
            "🪨": 0,
            "🧻": 1,
            "✂": 2
        }
        embed = discord.Embed(title="Choose your weapon!",
                              color=colors["orange"])
        embed.set_author(name=context.author.display_name,
                         icon_url=context.author.avatar_url)
        choose_message = await context.send(embed=embed)
        for emoji in reactions:
            await choose_message.add_reaction(emoji)

        def check(reaction, user):
            return user == context.message.author and str(reaction) in reactions

        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=10, check=check)

            user_choice_emote = reaction.emoji
            user_choice_index = reactions[user_choice_emote]

            bot_choice_emote = random.choice(list(reactions.keys()))
            bot_choice_index = reactions[bot_choice_emote]

            result_embed = discord.Embed(color=colors["green"])
            result_embed.set_author(
                name=context.author.display_name, icon_url=context.author.avatar_url)
            await choose_message.clear_reactions()

            choices_message = f"You've chosen {user_choice_emote} and I've chosen {bot_choice_emote}."

            if user_choice_index == bot_choice_index:
                result_embed.description = f"**That's a draw!**\n{choices_message}"
                result_embed.colour = colors["orange"]
            elif user_choice_index == 0 and bot_choice_index == 2:
                result_embed.description = f"**You won!**\n{choices_message}"
                result_embed.colour = colors["green"]
            elif user_choice_index == 1 and bot_choice_index == 0:
                result_embed.description = f"**You won!**\n{choices_message}"
                result_embed.colour = colors["green"]
            elif user_choice_index == 2 and bot_choice_index == 1:
                result_embed.description = f"**You won!**\n{choices_message}"
                result_embed.colour = colors["green"]
            else:
                result_embed.description = f"**I won!**\n{choices_message}"
                result_embed.colour = colors["red"]
                await choose_message.add_reaction("🇱")
            await choose_message.edit(embed=result_embed)
        except asyncio.exceptions.TimeoutError:
            await choose_message.clear_reactions()
            timeout_embed = discord.Embed(
                title="Too late slowpoke! I don't wanna play anymore!", color=colors["red"])
            timeout_embed.set_author(
                name=context.author.display_name, icon_url=context.author.avatar_url)
            await choose_message.edit(embed=timeout_embed)

    @commands.command(
        name="say",
        aliases=["echo"],
        usage="say <message>",
        brief="The Overseer says what you're thinking."
    )
    async def say(self, context, *, args):
        """
        The Overseer will say what you're thinking so you don't have to.
        """
        await context.send(args)

    @commands.command(
        name="8ball",
        usage="8ball <question>",
        brief="Ask the Overseer anything."
    )
    async def eight_ball(self, context, *, question):
        """
        Ask the Overseer anything. You may not like its answer.
        """
        answers = ['It is certain.', 'It is decidedly so.', 'You may rely on it.', 'Without a doubt.',
                   'Yes - definitely.', 'As I see, yes.', 'Most likely.', 'Outlook good.', 'Yes.',
                   'Signs point to yes.', 'Reply hazy, try again.', 'Ask again later.', 'Better not tell you now.',
                   'Cannot predict now.', 'Concentrate and ask again later.', 'Don\'t count on it.', 'My reply is no.',
                   'My sources say no.', 'Outlook not so good.', 'Very doubtful.']
        embed = discord.Embed(
            title="**My Answer:**",
            description=f"{answers[random.randint(0, len(answers))]}",
            color=colors["green"]
        )
        embed.set_footer(
            text=f"{context.message.author.name} asked: {question}"
        )
        await context.send(embed=embed)


def setup(bot):
    bot.add_cog(Fun(bot))