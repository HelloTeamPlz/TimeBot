from discord.ext import commands, tasks
from database import pochBot_db as pb_db
from datagraphing import pochbotGraphs as pb_graphs
from structurebot import StructureBot as sb
from PIL import Image
import os
import discord
import requests

#static keys
timer_channel_id = os.environ.get("channel_id")
api_key = os.environ.get("discbot")
timer_response_channel = int(os.environ.get("timer_response_channel"))
timer_dict_glob = {}

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

def get_old_timers(file_path):
  try: 
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(':')
            if len(parts) == 2:
              timer_dict_glob.update({int(parts[0]):parts[1]})
        file.close()
  except:
    pass

@bot.event
async def on_ready():
  print('the bot is ready')
  remove_expired_timers.start()
  response_channel = bot.get_channel(timer_response_channel)
  file_path = 'timers.txt'
  get_old_timers(file_path)
  sorted_timers = dict(sorted(timer_dict_glob.items(), reverse=True))
  timers_msg = '\n'.join([f'> {value} <t:{key}:f> in <t:{key}:R> ID: {key}' for key, value in sorted_timers.items()])
  await response_channel.purge(limit=5)
  await response_channel.send(timers_msg)
  

@bot.command()
async def timer(ctx, *args):
  
    response_channel = bot.get_channel(timer_response_channel)
    user = ctx.message.author
  
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
    try:
      results = sb.read_img("saved_image.png")
      parsed_datetime = sb.date_from_list(results)
      unix_ts = sb.to_unix_time(parsed_datetime)
      timer_dict_glob.update({unix_ts: timer_args})
      try: 
        #sort the timers and retrieve from the dictionary
        sorted_timers = dict(sorted(timer_dict_glob.items(), reverse=True))
        timers_msg = '\n'.join([f'> {value} <t:{key}:f> in <t:{key}:R> `{parsed_datetime} `ID: `{key}`' for key, value in sorted_timers.items()])
        txt_msg = '\n'.join([f'{key}:{value}'for key,value in sorted_timers.items()])
        sb.write_to_timers_txt(txt_msg)
        try:
          await response_channel.purge(limit=2)
          await response_channel.send(timers_msg)
        except:
          await response_channel.send(timers_msg)
      except:
        await ctx.send(results)
    except:
      await ctx.send(f'Cant read the date plz add manualy with !t command {user.mention}',delete_after=40)
      
@bot.command()
async def bulk_timer(ctx, *args):
  
    response_channel = bot.get_channel(timer_response_channel)
    
  
    # Check if an image is attached to the message
    if len(ctx.message.attachments) == 0:
        await ctx.send("Please attach an image to the command.",  delete_after=40)
        return

    # Get the first attached image
    attachment = ctx.message.attachments[0]
    url = attachment.url
    response = requests.get(url)
    if response.status_code == 200:
      with open('bulk.txt', 'wb') as file:
          file.write(response.content)
          file.close()
    
    with open('bulk.txt', 'r') as file:
      for line in file:
        parts = line.strip().split(':')
        if len(parts) == 2:
          timer_dict_glob.update({int(parts[0]):parts[1]})
    file.close()
        
    
    #sort the timers and retrieve from the dictionary
    try: 
      sorted_timers = dict(sorted(timer_dict_glob.items(), reverse=True))
      txt_msg = '\n'.join([f'{key}:{value}'for key,value in sorted_timers.items()])
      sb.write_to_timers_txt(txt_msg)
      try:
        await response_channel.purge(limit=2)
        await ctx.send('adding timers')
        #await response_channel.send(timers_msg)
      except:
        await ctx.send('adding timers', delete_after=40)
    except:
      await ctx.send('add it the hard way',delete_after=40)
      
@tasks.loop(seconds=5)
async def remove_expired_timers():
    response_channel = bot.get_channel(timer_response_channel)

    # Get the current UTC time
    current_unix_time = sb.unix_time_now()

    # Create a copy of keys to remove
    keys_to_remove = [key for key in timer_dict_glob if (key + 3600) < current_unix_time]

    # Remove the keys with timestamps that have passed
    for key in keys_to_remove:
        del timer_dict_glob[key]

    if keys_to_remove:
        # If keys were removed, send a message and purge the channel
        await response_channel.purge(limit=2)
        sorted_timers = dict(sorted(timer_dict_glob.items(), reverse=True))
        timers_msg = '\n'.join([f'> {value} <t:{key}:f> in <t:{key}:R> ID: {key}' for key, value in sorted_timers.items()])
        txt_msg = '\n'.join([f'{key}:{value}'for key,value in sorted_timers.items()])
        sb.write_to_timers_txt(txt_msg)

        if not timer_dict_glob:
            # If the dictionary is empty, send a default message
            default_msg = "There are no active timers."
            await response_channel.send(content=default_msg)
        else:
            # Sort the remaining timers by timestamp
            sorted_timers = dict(sorted(timer_dict_glob.items(), reverse=True))

            # Create a message with the remaining timers
            timers_msg = '\n'.join([f'> {value} <t:{key}:f> in <t:{key}:R> ID: {key}' for key, value in sorted_timers.items()])
            txt_msg = '\n'.join([f'{key}:{value}'for key,value in sorted_timers.items()])
            sb.write_to_timers_txt(txt_msg)
            await response_channel.send(timers_msg)

@bot.command()
async def rem(ctx, key):
    key = int(key)
    response_channel = bot.get_channel(timer_response_channel)
    if key in timer_dict_glob:
        # Delete the timer associated with the given key
        del timer_dict_glob[key]
        await ctx.send(f'Timer with key "{key}" has been removed.')
        sorted_timers = dict(sorted(timer_dict_glob.items(), reverse=True))
        timers_msg = '\n'.join([f'> {value} <t:{key}:f> in <t:{key}:R> ID: {key}' for key, value in sorted_timers.items()])
        txt_msg = '\n'.join([f'{key}:{value}'for key,value in sorted_timers.items()])
        sb.write_to_timers_txt(txt_msg)
        await response_channel.purge(limit=5)
        try: 
          await response_channel.send(timers_msg)
        except:
          await response_channel.send('There are no active timers.')
    else:
        await ctx.send(f'Timer with key "{key}" not found.')

@bot.command()
async def p(ctx, system_name):
  """
  sends emebed image with likly wh spawns close to the system if the system is in sys.txt file
  """
  with open('sys.txt') as file:
    contents = file.read()
    search_word = system_name.lower()
    if search_word in contents:
        file.close()
        system_name =  system_name.lower()
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
    response_channel = bot.get_channel(timer_response_channel)
    timers_data = sb.timer(time)
    timer_dict_glob.update({timers_data[1]: timers_data[0]})
    #sort the timers and retrieve from the dictionary
    sorted_timers = dict(sorted(timer_dict_glob.items(), reverse=True))
    timers_msg = '\n'.join([f'> {value} <t:{key}:f> in <t:{key}:R> ID: {key}' for key, value in sorted_timers.items()])
    txt_msg = '\n'.join([f'{key}:{value}'for key,value in sorted_timers.items()])
    sb.write_to_timers_txt(txt_msg)
    try:
      await response_channel.purge(limit=2)
      await response_channel.send(timers_msg)
    except:
      await response_channel.purge(limit=2)
      await response_channel.send(timers_msg)

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