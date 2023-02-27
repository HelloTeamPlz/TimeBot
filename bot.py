from datetime import datetime, timedelta, timezone


def add_time(time):
  # convert input to datetime object
  time = datetime.strptime(time, '%H:%M')

  # add 1 hour and 30 minutes to the time
  new_time = time + timedelta(minutes=35)

  # return the new time in 24-hour format
  return new_time.strftime('%H:%M')


# Example usage

#Use Discord.py library to send new_time to Discord
import discord
from discord.ext import commands
import os
from nextcord.utils import format_dt
import dateutil.parser as dparser


bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())


@bot.event
async def on_ready():
  print('the bot is ready')


@bot.command()
async def s(ctx, time: str):
  await ctx.send(add_time(time))


@bot.command()
async def asd(ctx, time: str):
  user = ctx.message.author
  timer = add_time(time)
  await ctx.send(f"{timer} sent by {user}")
  return


@bot.command()
async def timer(ctx, *, time):
  timer2 = time
  sysName = time.split(",")
  timer = dparser.parse(time, fuzzy=True)
  short_date_time = format_dt(timer, "f")
  relative_date = format_dt(timer, "R")
  await ctx.send(f"> {sysName[0]} {short_date_time} in {relative_date}")


api_key = os.environ.get("dicbot")

bot.run(api_key)
