# Discord WoW Buff Bot

This bot was developed for guild tracking of the Dragonslayer and Warchief's Blessing buffs.  It uses [discordpy](https://discordpy.readthedocs.io/en/latest/) and [sqlite3](https://docs.python.org/3/library/sqlite3.html).


### Current features/commands

* Setting Onyxia head turn in ($ony)
* Setting Rend head turn in ($wcb)
* Automatic alert roughly 3-5 minutes before next turn in is available
* View timers showing last known turn in and time until next available turn in ($timers)


### How to use

* Follow [instructions](https://discordpy.readthedocs.io/en/latest/discord.html) for setting up a discord bot
* Download timers.py and open in a text editor
* In Discord, right click on the channel you wish the bot to alert in, and select 'Copy ID', paste this into 'channelid' variable
* From the bot setup above, copy the token and paste into the 'botkey' variable
* Anyone with write permissions to the channel will be able to use the bot commands.  Select appropriate Discord permissions if this channel is public. (Recommend only guild members can write to channel, but public can read the channel).
* Use $help to see additional information


### Examples

![Example1](https://i.imgur.com/WRlj0Dt.png)
![Example2](https://i.imgur.com/iESeQP2.png)
![Example3](https://i.imgur.com/OmfmkH7.png)


### Bugs and issues

* The time used is the time of the machine the bot runs on.  Needs to be updated to appropriately handle timezones.
* ~~Occassionally when registering a head turn in, the bot will not respond, but the time/reminder is set.~~ (Fixed)
