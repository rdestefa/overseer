# overseer.cogs.calendar

import datetime
import icalendar
import logging
import os
import re

from utils.configs import load_config

import discord
from discord.ext import commands, tasks

# Color and logger configs.
colors = load_config("colors")
logger = logging.getLogger()


# TODO: Add support for recurring events.
class Calendar(commands.Cog, name="calendar"):
    def __init__(self, bot):
        self.bot = bot
        self.cal_dir = "lists"
        self.cal_file = "calendar.ics"
        self.timeout = 5.0

    @commands.Cog.listener()
    async def on_ready(self):
        self.check_calendar.start()

    # Continuous loop to check for upcoming events.
    @tasks.loop(minutes=5.0)
    async def check_calendar(self):
        with open(os.path.join(self.cal_dir, self.cal_file), 'r') as calendar:
            # Loed iterator for all events.
            calendar = calendar.read()
            events = icalendar.Calendar.from_ical(calendar).walk('vevent')

            # Filter for properly formatted dates.
            events = filter(lambda e: isinstance(
                e["DTSTART"].dt, datetime.datetime), events)

            # Initialize embed object to list events in.
            """embed = discord.Embed(
                title="Upcoming Events",
                description="Here are the upcoming events that I've planned.",
                color=colors["green"]
            )"""

            for event in events:
                # Get basic info about event.
                summary = event.get("summary")
                start = event.get("dtstart").dt
                end = event.get("dtend").dt
                description = event.get("description", "")

                # Timestamps to compare against.
                now = datetime.datetime.now(datetime.timezone.utc)
                later = now + datetime.timedelta(minutes=self.timeout)

                # Get appropriate channels to send the notification to.
                try:
                    channels = re.findall(
                        r'(?<=CHANNELS: )\d+[^\\\n]*', description)[0].split(',')
                    channels = list(map(lambda c: int(c.strip()), channels))
                except IndexError:
                    # TODO: Fix to work with new config layout.
                    channels = [config["general_channel_id"]]

                # Get episodes to watch.
                episodes = re.findall(
                    r'(?<=EPISODE: )[^\\\n]*', description)
                if episodes:
                    episodes = list(map(lambda e: e.split("::"), episodes))
                    episodes = list(map(
                        lambda e: {"show": e[0], "episode": e[1]}, episodes))

                # Get movies to watch.
                movies = re.findall(r'(?<=MOVIE: )[^\\\n]*', description)

                # Event isn't happening any time soon, so don't notify people.
                if not now <= start <= later:
                    continue

                delta = int((start - now).total_seconds() // 60)
                description = f"{summary} from {start.strftime('%I:%M %p')} " \
                              f"to {end.strftime('%I:%M %p')} "
                if delta:
                    description += f"is starting in {delta} " \
                                   f"{'minute!' if delta == 1 else 'minutes!'}"
                else:
                    description += f"is starting now!"

                for channel in channels:
                    # If channel isn't found, don't try and send a message.
                    if not (channel := self.bot.get_channel(channel)):
                        continue

                    # Assemble string of stuff to watch.
                    episodes_list = "\n".join(
                        [f" - {e['show']} - Episode {e['episode']}"
                         for e in episodes]
                    )
                    movies_list = ('\n' if episodes_list else ''
                                   + "\n".join([f" - {m}" for m in movies]))
                    content_list = episodes_list + movies_list

                    # Create embed object to send.
                    embed = discord.Embed(
                        title="Upcoming Event",
                        description=description,
                        color=colors["green"]
                    )
                    embed.add_field(
                        name="Today's Watch List",
                        value=content_list,
                        inline=False
                    )

                    # Send message.
                    await channel.send(embed=embed)

                attendees = event.get('attendee')
                if isinstance(attendees, str):
                    attendees = [attendees]
                for attendee in attendees:
                    # If user isn't found, don't try and send a message.
                    if not (attendee := self.bot.get_user(int(attendee))):
                        continue

                    await attendee.send(description)

    @commands.command(
        name="events",
        usage="events",
        brief="Lists calendar events."
    )
    async def events(self, context):
        """
        List all events on this server's calendar.
        """
        pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Calendar(bot))
