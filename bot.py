from datetime import datetime, timedelta, timezone
import discord
from discord.ext import commands
import os
from nextcord.utils import format_dt
import dateutil.parser as dparser
from database import *

class StructureBot:
    
    def __init__() -> None:
        pass
    
    def to_unix_time(date_time):
        unix_time = int(datetime.timestamp(date_time))
        return unix_time

    def new_Site(time):
      """
      convert input to datetime object, add 35 minutes to the time, return the new time in 24-hour format
      now unix timestamp for db as primary key 
      """
      time = datetime.strptime(time, '%H:%M')
      new_time = time + timedelta(minutes=35)
      return new_time.strftime('%H:%M')

    def timer(time):
      """
      given a string that looks like text, text and time stamp split on the "," parse the list to find the timestamp convert the timestamp into short and relitive date format
      for discod and return a tuple with all the desired values
      take curr unix time - future unix time + 3600 (60 minm)
      """
      sysName = time.split(",")
      structure_timer = dparser.parse(time, fuzzy=True)
      short_date_time = format_dt(structure_timer, "f")
      relative_date = format_dt(structure_timer, "R")
      unix_structure_timer = StructureBot.to_unix_time(structure_timer)
      current_unix_time = StructureBot.to_unix_time(datetime.now(timezone.utc))
      seconds_till_timer = unix_structure_timer - current_unix_time + 3600
      return (sysName[0], short_date_time, relative_date, seconds_till_timer)
      

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
  print('the bot is ready')


@bot.command()
async def s(ctx, time: str):
  new_site = StructureBot.new_Site(time)
  user = ctx.message.author
  payout = 3.6
  insert_new_site(str(user), time, payout)
  await ctx.send(f"> **{new_site}**")

@bot.command()
async def Site(ctx, time: str):
  user = ctx.message.author
  new_site = StructureBot.new_Site(time)
  await ctx.send(f"{new_site} sent by {user}")

@bot.command()
async def timer(ctx, *, time):
  ''''
  creates a timer for a structure in any channel where the command is called
  '''
  timers = StructureBot.timer(time)
  delete_after_time = timers[3] 
  await ctx.send(f">>> {timers[0]}\n{timers[1]} in {timers[2]}", delete_after=delete_after_time)

@bot.command()
async def t(ctx, *, time):
  '''
  creates a timer for a structure in a specified channel
  '''
  channel_id = os.environ.get("dora_channel_id")
  response_channel = bot.get_channel(channel_id)
  timers = StructureBot.timer(time)
  delete_after_time = timers[3] 
  await response_channel.send(f">>> {timers[0]}\n{timers[1]} in {timers[2]}", delete_after=delete_after_time)
    
def main():
    create_site_table()
    api_key = os.environ.get("discbot")
    bot.run(api_key)

if __name__ == "__main__":
    main()