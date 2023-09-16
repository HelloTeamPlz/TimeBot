from discord.ext import commands, tasks
from nextcord.utils import format_dt
from database import pochBot_db as pb_db
from datagraphing import pochbotGraphs as pb_graphs
from structurebot import StructureBot as sb
from PIL import Image
import os
import discord
import requests
from datetime import datetime, timezone

#static keys
timer_channel_id = os.environ.get("channel_id")
api_key = os.environ.get("discbot")
timer_response_channel = int(os.environ.get("timer_response_channel"))
timer_dict_glob = {}

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
  print('the bot is ready')
  response_channel = bot.get_channel(timer_response_channel)
  msg = await response_channel.send('>>> Gib Timers')
  bot.message_id = msg.id
  remove_expired_timers.start()

@bot.command()
async def timer(ctx, *args):
  
    response_channel = bot.get_channel(timer_response_channel)
  
    # Check if an image is attached to the message
    if len(ctx.message.attachments) == 0:
        await ctx.send("Please attach an image to the command.",  delete_after=40)
        return

    # Get the first attached image
    image_url = ctx.message.attachments[0].url
    timer_args = ' '.join(args)

    # Download and save the image
    image = Image.open(requests.get(image_url, stream=True).raw)
    image.save("saved_image.png")
    results = sb.read_img("saved_image.png")
    parsed_datetime = sb.date_from_list(results)
    timer_dict_glob.update({parsed_datetime: timer_args})
    
    #sort the timers and retrieve from the dictionary
    sorted_timers = dict(sorted(timer_dict_glob.items()))
    timers_msg = '\n'.join([f'> {value} {format_dt(key, "f")} in {format_dt(key, "R")}' for key, value in sorted_timers.items()])
    
    #check for the msg id stored earlier to edit the msg in {timer_response_channel}
    if hasattr(bot, 'message_id'):
      try:
        channel = ctx.channel
        message = await channel.fetch_message(bot.message_id)
        
        await message.edit(content = timers_msg)
      except discord.NotFound:
        msg = await response_channel.send.send(timers_msg)
        bot.message_id = msg.id
    else:
      msg = await response_channel.send.send(timers_msg)
      bot.message_id = msg.id
        
    #await ctx.send(results)
    #await ctx.send(timers_msg)
    #await response_channel.send(f">>> {timer_args}\n{timers[0]} in {timers[1]}", delete_after=timers[2])

@tasks.loop(seconds=60*15)
async def remove_expired_timers():
    response_channel = bot.get_channel(timer_response_channel)

    # Get the current UTC time
    current_unix_time = sb.to_unix_time(datetime.now(timezone.utc))

    # Create a copy of keys to remove
    keys_to_remove = [key for key in timer_dict_glob if sb.to_unix_time(key) < current_unix_time]

    # Remove the keys with timestamps that have passed
    for key in keys_to_remove:
        del timer_dict_glob[key]

    if not timer_dict_glob:
        # If the dictionary is empty, send a default message
        default_msg = "There are no active timers."
        channel = response_channel
        message = await channel.fetch_message(bot.message_id)
        await message.edit(content=default_msg)
    else:
        # Sort the remaining timers by timestamp
        sorted_timers = dict(sorted(timer_dict_glob.items()))

        # Create a message with the remaining timers
        timers_msg = '\n'.join([f'> {value} {format_dt(key, "f")} in {format_dt(key, "R")}' for key, value in sorted_timers.items()])

        if hasattr(bot, 'message_id'):
            try:
                channel = response_channel
                message = await channel.fetch_message(bot.message_id)

                # Edit the existing message with the updated timers
                await message.edit(content=timers_msg)
            except discord.NotFound:
                # If the message doesn't exist, send a new one and store its ID
                msg = await response_channel.send(timers_msg)
                bot.message_id = msg.id
        else:
            # If there's no stored message ID, send a new message and store its ID
            msg = await response_channel.send(timers_msg)
            bot.message_id = msg.id

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
  new_site = sb.new_Site(time)
  user = ctx.message.author
  payout = 3.4
  pb_db.insert_new_site(str(user), time, payout)
  await ctx.send(f"> **{new_site}**")

@bot.command()
async def S(ctx, time: str):
  '''
  for site ran by other people so it wont count against you
  '''
  new_site = sb.new_Site(time)
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
    timers_data = sb.timer(time)

    timer_dict_glob.update({timers_data[1]: timers_data[0]})
    #sort the timers and retrieve from the dictionary
    sorted_timers = dict(sorted(timer_dict_glob.items()))
    timers_msg = '\n'.join([f'> {value} {format_dt(key, "f")} in {format_dt(key, "R")}' for key, value in sorted_timers.items()])
    
    #check for the msg id stored earlier to edit the msg in {timer_response_channel}
    if hasattr(bot, 'message_id'):
      try:
        channel = ctx.channel
        message = await channel.fetch_message(bot.message_id)
        
        await message.edit(content = timers_msg)
      except discord.NotFound:
        msg = await response_channel.send.send(timers_msg)
        bot.message_id = msg.id
    else:
      msg = await response_channel.send.send(timers_msg)
      bot.message_id = msg.id

# @bot.command()
# async def timer(ctx, *, time):
#   ''''
#   creates a timer for a structure in any channel where the command is called
#   '''
#   timers = StructureBot.timer(time)
#   delete_after_time = timers[3] 
#   await ctx.send(f">>> {timers[0]}\n{timers[1]} in {timers[2]}", delete_after=delete_after_time)

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