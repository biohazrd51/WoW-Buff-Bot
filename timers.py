import discord
from discord.ext import commands
import sqlite3 as sqlite
from datetime import datetime, timedelta
import pytz
import sys, os
import asyncio

#Opens database used to hold time data
locpath = os.path.dirname(os.path.realpath(__file__))
dbpath = locpath + "/" + "timers.sqlite"
dbopen = sqlite.connect(dbpath)
dbref = dbopen.cursor()

#Sets up database table if doesn't exist
dbref.execute('''create table if not exists timers (timertype TEXT, timestamp NUMERIC, lastseen NUMBERIC)''')
dbopen.commit()

#Attempts to select data from table to validate base information, creates if necessary
try:
    dbref.execute('''select timertype from timers''')
    tabledata = dbref.fetchall()
    if len(tabledata) != 0:
        pass
    elif len(tabledata) == 0:
        dbref.execute('''insert into timers (timertype) values ('ony'), ('wcb')''')
        dbopen.commit()
except:
    print("Error creating table data")

#Setup client and sets prefix for commands
client = discord.Client()
bot = commands.Bot(command_prefix='$')

#Sets the emeds for the messages and image thumbnails, embed fields get added under each command, then cleared after
onyemb = discord.Embed()
onyemb.set_thumbnail(url="https://i.imgur.com/6xs88EH.jpg")
wcbemb = discord.Embed()
wcbemb.set_thumbnail(url="https://i.imgur.com/ZYpVx9P.jpg")
timeremb = discord.Embed()
timeremb.set_thumbnail(url="https://i.imgur.com/nWXgNsz.jpg")

#Variables to be used.  Channel ID required for specific channel use.  Bot key for bot to login
#testchannelid = #Test channel, if needed: uncomment, switch bot.get_channel(channelid) from channelid to testchannelid
channelid = #This restricts the bot to receiving commands, and speaking, only in this channel. Use discord permissions appropriately.
botkey = ''

@bot.command(name='info', brief="Info on the bot", description="Thrown together bot")
async def botinfo(ctx):
    if ctx.channel.id == channelid:
        channel = bot.get_channel(channelid)
        info = '\nI am a bot hacked together for the purpose of tracking Ony and WCB buffs. \nAll commands use $ to run.'
        await channel.send(info)

@bot.command(name='ony', brief="Sets Rallying Cry of the Dragonslayer", description="Sets the timer for turn in of Onyxia head")
async def ony(ctx):
    if ctx.channel.id == channelid:
        channel = bot.get_channel(channelid)
        bufftype = "ony"
        timerset = datetime.now() #I'm lazy and bot time is also WoW server time. Needs TZ rewrite
        timerplus = timerset + timedelta(hours=6)
        dbref.execute('''update timers set timestamp = ?, lastseen = ? where timertype = ?''', (timerplus, timerset.strftime("%Y-%m-%d %H:%M"), bufftype))
        dbopen.commit()
        onyturnin = 'Got it! The head was turned in at ' + timerset.strftime("%Y-%m-%d %H:%M") + ' and the next window should open at ' + timerplus.strftime("%Y-%m-%d %H:%M")
        onyemb.add_field(name="Dragonslayer Timer Set", value=onyturnin, inline=True)
        onyemb.set_footer(text="Added by " + ctx.message.author.nick, icon_url=ctx.message.author.avatar_url)
        await channel.send(embed=onyemb)
        onyemb.clear_fields() #Clears field from embed for next event
        onyemb.set_footer(text="", icon_url="") #Clears footer manually, as footer has no clear method

@bot.command(name='wcb', brief="Sets Warchief's Blessing", description="Sets the timer for turn in on Rend head")
async def wcb(ctx):
    if ctx.channel.id == channelid:
        channel = bot.get_channel(channelid)
        bufftype = "wcb"
        timerset = datetime.now() #I'm lazy and bot time is also WoW server time. This will need to b rewritten to handle timezones
        timerplus = timerset + timedelta(hours=3)
        dbref.execute('''update timers set timestamp = ?, lastseen = ? where timertype = ?''', (timerplus, timerset.strftime("%Y-%m-%d %H:%M"), bufftype))
        dbopen.commit()
        wcbturnin = 'Got it! The head was turned in at ' + timerset.strftime("%Y-%m-%d %H:%M") + ' and the next window should open at ' + timerplus.strftime("%Y-%m-%d %H:%M")
        wcbemb.add_field(name="Warchief's Timer Set", value=wcbturnin, inline=True)
        wcbemb.set_footer(text="Added by " + ctx.message.author.nick, icon_url=ctx.message.author.avatar_url)
        await channel.send(embed=wcbemb)
        wcbemb.clear_fields() #Clears field from embed for next event
        wcbemb.set_footer(text="", icon_url="") #Clears footer manually, as footer has no clear method

@bot.command(name='timers', brief="Shows time until open turn in", description="Shows the time in HH:MM until turn in is open")
async def timers(ctx):
    if ctx.channel.id == channelid:
        onybuff = ""
        wcbbuff = ""
        channel = bot.get_channel(channelid)
        dbref.execute('''select timertype, timestamp, lastseen from timers''')
        timerdata = dbref.fetchall()
        if timerdata is not None: #Check if data exists before proceeding
            for timertype, timestamp, lastseen in timerdata:
                if timestamp is None: #If timestamp does not exist, there is no currently set timer
                    if timertype == "ony":
                        onybuff = "Dragonslayer: \nNo timer is available.  \nLast turn in was seen at " + lastseen + '\n'
                    elif timertype == "wcb":
                        wcbbuff = "Warchief's: \nNo timer is available. \nLast turn in was seen at " + lastseen + '\n'
                elif timestamp is not None:
                    timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
                    timenow = datetime.now()
                    timecalc = timestamp - timenow
                    timedursec = timecalc.total_seconds()
                    timetobuff = divmod(timedursec, 3600) #Gives datetime object in hours/seconds remainder, as float, [0] is hours, and [1] is second
                    timehours = str(int(timetobuff[0])) #Convert to INT, STR for output
                    timeminutes = str(int(timetobuff[1] /60)) #Divides to minutes, converts to INT, STR for output
                    timetotal = timehours + ':' + timeminutes
                    if timertype == "ony":
                        onybuff = "\nDragonslayer:" + "\nTime until turn in opens: " + timehours + " hour(s) " + timeminutes + " minute(s) " + "\nLast turn in was seen at " + lastseen + '\n'
                    elif timertype == "wcb":
                        wcbbuff = "\nWarchief's:" + "\nTime until turn in opens: " + timehours + " hour(s) " + timeminutes + " minute(s)" + "\nLast turn in was seen at " + lastseen + '\n'
            buffstate = onybuff + wcbbuff
        elif timerdata is None:
            buffstate = "No data available" #Handle if data from query is none
        timeremb.add_field(name="Timers: ", value=buffstate, inline=True)
        await channel.send(embed=timeremb)
        timeremb.clear_fields()

#Loops every 60 seconds to check for upcoming timers
async def real_notify():
    await bot.wait_until_ready()
    channel = bot.get_channel(channelid)
    while not bot.is_closed():
        notifytime = datetime.now() + timedelta(seconds=300) #Adds 5 minutes to current time
        dbref.execute('''select timertype, timestamp, lastseen from timers where ? > timestamp''', (notifytime,)) #Searches for any timer coming up in the next 5 minutes
        notifications = dbref.fetchall()
        if notifications is not None:
            setnull = None
            onytype = "ony"
            wcbtype = "wcb"
            for timertype, timestamp, lastseen in notifications:
                convert = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f") #Convert to datetime object to be appropriately formatted for message
                timestamp = convert.strftime("%Y-%m-%d %H:%M") #Format for message output, removing seconds, and converting to string
                if timertype == onytype:
                    onybuff = "The window for Dragonslayer opens soon! (Last known turn-in was " + lastseen + ')'
                    dbref.execute('''update timers set timestamp = ? where timertype = ?''', (setnull, onytype,)) #Clears existing timer
                    onyemb.add_field(name="Dragonslayer Window Opening: ", value=onybuff, inline=True)
                    await channel.send(embed=onyemb)
                    onyemb.clear_fields()
                elif timertype == wcbtype:
                    wcbbuff = "The window for Warchief's opens soon! (Last known turn-in was " + lastseen + ')'
                    dbref.execute('''update timers set timestamp = ? where timertype = ?''', (setnull, wcbtype,)) #Clears existing timer
                    wcbemb.add_field(name="Warchief's Window Opening: ", value=wcbbuff, inline=True)
                    await channel.send(embed=wcbemb)
                    wcbemb.clear_fields()
            dbopen.commit()
        await asyncio.sleep(60)

bot.loop.create_task(real_notify())
bot.run(botkey)
