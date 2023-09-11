from datetime import datetime, timedelta, timezone
import discord
from discord.ext import commands
import os
from nextcord.utils import format_dt
import dateutil.parser as dparser
from database import pochBot_db as pb_db
from datagraphing import pochbotGraphs as pb_graphs

#static keys
timer_channel_id = os.environ.get("channel_id")
api_key = os.environ.get("discbot")

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
async def S(ctx, time: str):
  '''
  for site ran by other people so it wont count against you
  '''
  new_site = StructureBot.new_Site(time)
  await ctx.send(f"> **{new_site}**")

@bot.command()
async def stats(ctx, *, user=None):
    if user is None:
        user = ctx.message.author
    else:
        pass
    
    df = pb_db.individual_sites_done(user)
    user = df['Name'][0]
    sites_ran = df['Payout'].value_counts()
    profit = 3.4 * sites_ran.sum()
    tax = profit * .025

    embed = discord.Embed(title=f"Sites Run by {user}", description=f'Sites Run: {sites_ran.sum()}')
    embed.add_field(name='Total Payout', value=f'{profit:.2f} Bil')
    embed.add_field(name='Tax', value=f'{tax:.3f} Bil')

    file = pb_graphs.individual_sites_graph(df)
    image = discord.File(file, filename='graph.png')
    embed.set_image(url=f'attachment://graph.png')
    await ctx.send(file=image, embed=embed)

@bot.command()
async def Tstats(ctx):
  df = pb_db.total_site_done()
  payout = 3.4
  df = df.drop('Date', axis = 1)
  df['IskMade'],df['Tax'] = df['TotalPayout'] * payout, df['TotalPayout'] * payout *.025
  df_sorted = df.sort_values(by='IskMade', ascending=False).to_string(index=False)

  embed = discord.Embed(title=f"Total Payouts", description= f"""```{df_sorted}```""")

  file = pb_graphs.total_sites_done_total(df)
  image = discord.File(file, filename='graph.png')
  embed.set_image(url=f'attachment://graph.png')
  await ctx.send(file=image, embed=embed)

@bot.command()
async def t(ctx, *, time):
  '''
  creates a timer for a structure in a specified channel
  '''
  channel_id = int(timer_channel_id)
  response_channel = bot.get_channel(channel_id)
  timers = StructureBot.timer(time)
  delete_after_time = timers[3] 
  await response_channel.send(f">>> {timers[0]}\n{timers[1]} in {timers[2]}", delete_after=delete_after_time)

@bot.command()
async def timer(ctx, *, time):
  ''''
  creates a timer for a structure in any channel where the command is called
  '''
  timers = StructureBot.timer(time)
  delete_after_time = timers[3] 
  await ctx.send(f">>> {timers[0]}\n{timers[1]} in {timers[2]}", delete_after=delete_after_time)

@bot.command()
async def h(ctx):
  commands = {
      's' : 'Add 35 minutes to the time in 24hr format and adds a site ran to your total',
      'timer': 'Creates a timer for a structure in any channel where the command is called',
      't': 'Creates a timer for a structure in a specified channel no matter where the timer is entered',
      'stats': 'Gives the # of sites ran by a user',
      'p': 'Returns a map of pochven and how close the wormhole will bring you only works for high and lowsec systems',
      'S': 'Add 35 minutes to the time in 24hr format if someone else runs the spawn and wont add it to your total',
      'Tstats': 'Shows all the sites ran by everyone and the relevent stats'
  }
  command_txt = ">>> "
  for key, value in commands.items():
      command_txt += f'**{key}**: {value}\n'
  await ctx.send(command_txt)    
      
def main():
    pb_db.create_site_table()
    bot.run(api_key)

if __name__ == "__main__":
    main()