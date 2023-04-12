from datetime import datetime, timedelta, timezone
import discord
from discord.ext import commands
import os
from nextcord.utils import format_dt
import dateutil.parser as dparser
from database import pochBot_db as pb_db
import io
import matplotlib.pyplot as plt

class StructureBot:
    
    def __init__() -> None:
        pass
    
    def get_channel_id(channel_name):
      """
      gets the channel id from env file
      """
      channel_id = os.environ.get(f"{channel_name}")
      return int(channel_id)
    
    def to_unix_time(date_time):
      unix_time = int(datetime.timestamp(date_time))
      return unix_time

    def new_Site(time):
      """
      convert input to datetime object, add 35 minutes to the time, return the new time in 24-hour format 
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
async def p(ctx, system_name):
  """
  sends emebed image with likly wh spawns close to the system if the system is in sys.txt file
  """
  with open('sys.txt') as file:
    contents = file.read()
    search_word = system_name
    if search_word in contents:
        file.close()
        embed = discord.Embed(description=f"Here's the exit map for {system_name}")
        embed.set_image(url=f'https://pochven.goryn.wtf/img/{system_name}.png')
        await ctx.send(embed=embed)
    else:
        file.close()
        pass
  
@bot.command()
async def s(ctx, time: str):
  new_site = StructureBot.new_Site(time)
  user = ctx.message.author
  payout = 3.4
  pb_db.insert_new_site(str(user), time, payout)
  await ctx.send(f"> **{new_site}**")

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
  channel_id = StructureBot.get_channel_id('dora_channel_id')
  timers = StructureBot.timer(time)
  delete_after_time = timers[3] 
  if channel_id == None:
    await ctx.send(f">>> {timers[0]}\n{timers[1]} in {timers[2]}", delete_after=delete_after_time)
  else:
    response_channel = bot.get_channel(channel_id)
    await response_channel.send(f">>> {timers[0]}\n{timers[1]} in {timers[2]}", delete_after=delete_after_time)

@bot.command()
async def stats(ctx, user = None):
  if user == None:
    user = ctx.message.author
    user_name = str(user).split('#')
  else:
     pass
  user_name = user
  df = pb_db.individual_sites_done(user)
  user = df['Name'][0]
  sites_ran = df['Payout'].value_counts()
  profit = 3.4 * sites_ran.values[0]
  tax = profit * .025
  embed = discord.Embed(title=f"Sites Run by {user}", description= f'Sites Run: {sites_ran.values[0]}')
  embed.add_field(name= 'Total Payout', value=f'{profit} Bil')
  embed.add_field(name= 'Tax', value=f'{tax} Bil')
  plt.style.use('dark_background')
  fig, ax = plt.subplots()
  counts = df['Date'].value_counts().sort_index(ascending=True)
  dates = counts.index
  payouts = counts.values
  ax.set_xlabel('Date')
  ax.set_ylabel('Payouts')
  ax.scatter(dates, payouts, marker='.', s = 75, color = '#47a0ff')
  ax.plot(counts, color = '#47a0ff')
  ax.yaxis.grid()
  ax.spines['top'].set_visible(False)
  ax.spines['right'].set_visible(False)
  ax.spines['left'].set_visible(False)
  plt.savefig('graph.png', transparent=True)
  plt.close(fig)
  with open('graph.png', 'rb') as f:
      file = io.BytesIO(f.read())
  image = discord.File(file, filename='graph.png')
  embed.set_image(url=f'attachment://graph.png')
  await ctx.send(file=image, embed=embed)

@bot.command()
async def h(ctx):
  commands = {
      's' : 'add 35 minutes to the time in 24hr format',
      'timer': 'creates a timer for a structure in any channel where the command is called',
      't': 'creates a timer for a structure in a specified channel no matter where the timer is entered',
      'stats': 'Gives the # of sites ran by a user',
      'p': 'returns a map of pochven and how close the wormhole will bring you only works for high and lowsec systems'
  }
  command_txt = ">>> "
  for key, value in commands.items():
      command_txt += f'**{key}**: {value}\n'
  await ctx.send(command_txt)    
      
def main():
    pb_db.create_site_table()
    api_key = os.environ.get("discbot")
    bot.run(api_key)

if __name__ == "__main__":
    main()