# PochBot
PochBot is a bot for [EVE Online](https://www.eveonline.com/). It is primarly made for pochven but has a few commands that are usefull outside of pochven for creating unix timers in a discord format for structure timers.

## Table of contents
* [General info](#general-info)
* [Setup](#setup)

## General info
all bot commands are called with the **!** prefix.
    Commands:
      's' : Add 35 minutes to the time in 24hr format and adds a site ran to your total.
      'timer': Creates a timer for a structure in any channel where the command is called
      't': Creates a timer for a structure in a specified channel no matter where the timer is entered **Requires Channel ID**.
      'stats': Gives the # of sites ran by a user.
      'p': Returns a map of pochven and how close the wormhole will bring you only works for high and lowsec systems.
      'S': Add 35 minutes to the time in 24hr format if someone else runs the spawn and wont add it to the database.
      'h': shows this list of commands.
      'Tstats': shows all the sites ran by everyone and the relevent stats

	
## Setup
PochBot is simple and easy to set up simply clone the project and add your discord api key.

### 1. Discord
Add your token from your bot to the .env in `discbot=<key>` and add the bot to your server if you need help follow this [documentaion](https://discord.com/developers/docs/topics/oauth2#bots).

### 2. 
Add your channel id for for the !t command to the .env `channel_id=<id>`.

### 3. SetUp
1. clone this repository.
2.
```
docker compose up --build -d
```
