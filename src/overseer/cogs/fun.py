# overseer.cogs.fun

import asyncio
import json
import logging
import random
import re

from utils.configs import load_config
from utils.parsers import parse_mentions

import aiohttp
import discord
from discord.ext import commands
from discord.ext.commands import BucketType

# Color and logger configs.
colors = load_config("colors")
logger = logging.getLogger()


class Fun(commands.Cog, name="fun"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.eight_ball_responses = (
            (
                ("It is certain.", "green"),
                ("It is decidedly so.", "green"),
                ("You may rely on it.", "green"),
                ("Without a doubt.", "green"),
                ("Yes - definitely.", "green"),
                ("As I see it, yes.", "green"),
                ("Most likely.", "green"),
                ("Outlook good.", "green"),
                ("Yes.", "green"),
                ("Signs point to yes.", "green")
            ),
            (
                ("Reply hazy, try again.", "yellow"),
                ("Better not tell you now.", "yellow"),
                ("Cannot predict now.", "yellow"),
                ("Ask again later.", "yellow"),
                ("Concentrate and ask again.", "yellow")
            ),
            (
                ("Don't count on it.", "red"),
                ("My sources say no.", "red"),
                ("Very doubtful.", "red"),
                ("My reply is no.", "red"),
                ("Outlook not so good.", "red")
            )
        )

    @commands.hybrid_command(
        name="bitcoin",
        usage="bitcoin",
        brief="Get the current price of Bitcoin."
    )
    async def bitcoin(self, context: commands.Context) -> None:
        """
        Get the current price of Bitcoin from `coindesk.com`.
        """
        url = "https://api.coindesk.com/v1/bpi/currentprice/BTC.json"
        # Asynchronously fetch data from the coindesk API.
        async with aiohttp.ClientSession() as session:
            raw_response = await session.get(url)
            response = await raw_response.text()
            response = json.loads(response)

            await context.send(embed=discord.Embed(
                title="Current Bitcoin Price :coin:",
                description=f"${response['bpi']['USD']['rate']}",
                color=colors["green"]
            ))

    """
    Why 1 and 86400?
      - Users should be able to use the command *once* every *86400* seconds.

    Why BucketType.user?
      - The cooldown only affects the current user. Other kinds of cooldowns:
        - BucketType.default for a global cooldown.
        - BucketType.user for a per-user cooldown.
        - BucketType.server for a per-server cooldown.
        - BucketType.channel for a per-channel cooldown.
    """
    @commands.hybrid_command(
        name="dailyfact",
        usage="dailyfact",
        brief="Get your daily dose of knowledge."
    )
    @commands.cooldown(1, 86400, BucketType.user)
    async def dailyfact(self, context: commands.Context) -> None:
        """
        Get a random fact from the Internet once per day per user.
        """
        # Asynchronously fetch data from the useless facts API.
        url = "https://uselessfacts.jsph.pl/random.json?language=en"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, ssl=False) as response:
                if response.status == 200:
                    data = await response.json()
                    await context.send(embed=discord.Embed(
                        description=data["text"],
                        color=colors["purple"]
                    ))
                else:
                    logger.warning(
                        "Failed to fetch a daily fact. Error code: %s",
                        response.status
                    )
                    await context.send(embed=discord.Embed(
                        title="Error!",
                        description=("I can't get any facts from the Internet "
                                     + "right now. Please try again later."),
                        color=colors["red"]
                    ))

                    # Reset user's cooldown since they missed their daily fact.
                    self.dailyfact.reset_cooldown(context)

    @commands.hybrid_command(
        name="poll",
        usage="poll <title>",
        brief="Create a poll that members can vote on."
    )
    async def poll(self, context: commands.Context, *, title) -> None:
        """
        Create a poll that members can vote on.
        The three default reactions are yes, no, and maybe.

        Parameters
        -----------
        title: str
            What people are going to vote on.
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

    @commands.hybrid_command(
        name="rps",
        usage="rps",
        brief="Play rock, paper, scissors with the Overseer."
    )
    async def rock_paper_scissors(self, context: commands.Context) -> None:
        """
        Play rock, paper, scissors with the me. It's a fight to the death!
        I don't like time-wasters, so you'll have 10 seconds to respond.
        """
        reactions = {
            "🪨": 0,
            "🧻": 1,
            "✂": 2
        }

        # Create embed that will be used to play rock, paper, scissors.
        embed = discord.Embed(
            title="Choose your weapon!",
            color=colors["orange"]
        )
        embed.set_author(
            name=context.author.display_name,
            icon_url=context.author.avatar
        )
        options_msg = await context.send(embed=embed)

        # Add each choice as a reaction to the message.
        for emoji in reactions:
            await options_msg.add_reaction(emoji)

        try:
            reaction, _ = await self.bot.wait_for(
                "reaction_add",
                timeout=10,
                check=lambda reaction, user: (user == context.message.author
                                              and str(reaction) in reactions)
            )

            user_choice_emote = reaction.emoji
            user_choice_id = reactions[user_choice_emote]

            bot_choice_emote = random.choice(tuple(reactions.keys()))
            bot_choice_id = reactions[bot_choice_emote]

            result_embed = discord.Embed(color=colors["green"])
            result_embed.set_author(
                name=context.author.display_name,
                icon_url=context.author.avatar
            )

            await options_msg.clear_reactions()

            choices_msg = (f"You chose {user_choice_emote} and "
                           + f"I chose {bot_choice_emote}.")

            # Format embed based on result.
            if user_choice_id == bot_choice_id:
                result_embed.description = f"**It's a draw!**\n{choices_msg}"
                result_embed.color = colors["yellow"]
            elif ((user_choice_id == 0 and bot_choice_id == 2)
                  or (user_choice_id == 1 and bot_choice_id == 0)
                  or (user_choice_id == 2 and bot_choice_id == 1)):
                result_embed.description = f"**You won!**\n{choices_msg}"
                result_embed.color = colors["green"]
            else:
                result_embed.description = f"**I won!**\n{choices_msg}"
                result_embed.color = colors["red"]
                await options_msg.add_reaction("🇱")

            await options_msg.edit(embed=result_embed)
        except asyncio.exceptions.TimeoutError:
            await options_msg.clear_reactions()

            timeout_embed = discord.Embed(
                title="Too late slowpoke! I don't wanna play anymore!",
                color=colors["red"]
            )
            timeout_embed.set_author(
                name=context.author.display_name,
                icon_url=context.author.avatar
            )

            await options_msg.edit(embed=timeout_embed)

    @commands.hybrid_command(
        name="spam",
        usage="spam <@user> <number>",
        brief="Spam a user with DMs."
    )
    @commands.is_owner()
    async def spam(
        self,
        context: commands.Context,
        member: discord.Member,
        amount: int
    ) -> None:
        """
        I will spam a specified user's DMs `<number>` times. They will never
        recover.

        Parameters
        -----------
        member: discord.Member
            The person you want to spam.
        amount: int
            The number of messages to send. Must be a positive integer.
        """
        if amount < 1:
            logger.error(
                "Only positive integers are accepted by spam.")
            embed = discord.Embed(
                title="Error!",
                description=f"`{amount}` must be a positive integer.",
                color=colors["red"]
            )
            await context.send(embed=embed)
            return

        emojis = (":monkey:", ":monkey_face:",
                  ":hippopotamus:", ":lion:", ":pig:")
        for _ in range(amount):
            message = " ".join([random.choice(emojis) for _ in range(10)])
            await member.send(message)

    @commands.hybrid_command(
        name="8ball",
        usage="8ball <question>",
        brief="Ask the Overseer anything."
    )
    async def eight_ball(self, context: commands.Context, *, question) -> None:
        """
        Ask me anything. You may not like what I have to say.

        Parameters
        -----------
        question: str
            The question you want to ask.
        """
        response = random.choice(random.choice(self.eight_ball_responses))
        embed = discord.Embed(
            title="**Here's What I Think**",
            description=response[0],
            color=colors[response[1]]
        )

        question = parse_mentions(question, self.bot, context.guild)
        embed.set_footer(
            text=f"{context.message.author.name} asked: {question}"
        )

        await context.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))
