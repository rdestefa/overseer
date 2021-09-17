# overseer.cogs.fun

import asyncio
import json
import logging
import random

from helpers.config_helpers import load_bot_configs

import aiohttp
import discord
from discord.ext import commands
from discord.ext.commands import BucketType

# Bot and logger configs
config = load_bot_configs()
logger = logging.getLogger()


class Fun(commands.Cog, name="fun"):
    def __init__(self, bot):
        self.bot = bot

    """
    Why 1 and 86400?
    -> Because the user should be able to use the command *once* every *86400* seconds

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
        # This will prevent the Overseer from stopping everything when making a web request - see: https://discordpy.readthedocs.io/en/stable/faq.html#how-do-i-make-a-web-request
        async with aiohttp.ClientSession() as session:
            async with session.get("https://uselessfacts.jsph.pl/random.json?language=en") as request:
                if request.status == 200:
                    data = await request.json()
                    embed = discord.Embed(
                        description=data["text"], color=0xD75BF4)
                    await context.send(embed=embed)
                else:
                    logger.warning(
                        'Failed to fetch a daily fact from the useless facts API. Error code: %s', request.status)
                    embed = discord.Embed(
                        title="Error!",
                        description="There's an issue with the useless facts API. Please try again later",
                        color=0xE02B2B
                    )
                    await context.send(embed=embed)
                    # We need to reset the cooldown since the user didn't get their daily fact.
                    self.dailyfact.reset_cooldown(context)

    @commands.command(
        name="rps",
        usage="rps",
        brief="Play rock, paper, scissors with me."
    )
    async def rock_paper_scissors(self, context):
        """
        Play rock, paper, scissors with me. It's a fight to the death!
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
        embed = discord.Embed(title="Choose your weapon!", color=0xF59E42)
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

            result_embed = discord.Embed(color=0x42F56C)
            result_embed.set_author(
                name=context.author.display_name, icon_url=context.author.avatar_url)
            await choose_message.clear_reactions()

            choices_message = f"You've chosen {user_choice_emote} and I've chosen {bot_choice_emote}."

            if user_choice_index == bot_choice_index:
                result_embed.description = f"**That's a draw!**\n{choices_message}"
                result_embed.colour = 0xF59E42
            elif user_choice_index == 0 and bot_choice_index == 2:
                result_embed.description = f"**You won!**\n{choices_message}"
                result_embed.colour = 0x42F56C
            elif user_choice_index == 1 and bot_choice_index == 0:
                result_embed.description = f"**You won!**\n{choices_message}"
                result_embed.colour = 0x42F56C
            elif user_choice_index == 2 and bot_choice_index == 1:
                result_embed.description = f"**You won!**\n{choices_message}"
                result_embed.colour = 0x42F56C
            else:
                result_embed.description = f"**I won!**\n{choices_message}"
                result_embed.colour = 0xE02B2B
                await choose_message.add_reaction("🇱")
            await choose_message.edit(embed=result_embed)
        except asyncio.exceptions.TimeoutError:
            await choose_message.clear_reactions()
            timeout_embed = discord.Embed(
                title="Too late slowpoke! I don't wanna play anymore!", color=0xE02B2B)
            timeout_embed.set_author(
                name=context.author.display_name, icon_url=context.author.avatar_url)
            await choose_message.edit(embed=timeout_embed)

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
            color=0x42F56C
        )
        embed.set_footer(
            text=f"Poll created by: {context.message.author} • React to vote!"
        )
        embed_message = await context.send(embed=embed)
        await embed_message.add_reaction("👍")
        await embed_message.add_reaction("👎")
        await embed_message.add_reaction("🤷")

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
            color=0x42F56C
        )
        embed.set_footer(
            text=f"{context.message.author.name} asked: {question}"
        )
        await context.send(embed=embed)

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
        # Async HTTP request
        async with aiohttp.ClientSession() as session:
            raw_response = await session.get(url)
            response = await raw_response.text()
            response = json.loads(response)
            embed = discord.Embed(
                title=":information_source: Crypto",
                description=f"Bitcoin price is: ${response['bpi']['USD']['rate']}",
                color=0x42F56C
            )
            await context.send(embed=embed)


def setup(bot):
    bot.add_cog(Fun(bot))
