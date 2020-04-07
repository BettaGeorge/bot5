#!/usr/bin/python3
# bot5.py
# the main executable to start Bot5.
# call python3 bot5.py to bring it online.
# accepts one optional argument: the path to the config folder. If none is provided, a sensible default is used.
# There should be nothing in here except the bare minimum. Everything else should be loaded through extensions.
# These extensions in turn should be loaded by the ExtensionManager.


#----------------------------------------------------------------------------
#"THE COFFEEWARE LICENSE":
#Adrian Rettich (adrian.rettich@gmail.com) wrote this file. As long as you retain this notice, you can do whatever you want with this stuff. If we should meet in person some day, and you think this stuff is worth it, you are welcome to buy me a coffee in return.  
#----------------------------------------------------------------------------



from bot5utils import *
import bot5utils
from bot5utils import ext as b5

import traceback

prefix = b5config.get('bot','command prefix',fallback='\\')
client = commands.Bot(command_prefix=commands.when_mentioned_or(prefix))


# WARNING: this is NOT GUARANTEED TO BE ONLY CALLED ONCE!
# my fix for now: see whether extension manager is loaded. If yes, we must have been here before.
# edit a few days later: fix seems to be working.
@client.event
async def on_ready():

    print("BOT5: on_ready called")

    # if we have already loaded the extension manager, do nothing.
    if bot5Loaded():
        print("BOT5: already loaded, doing nothing")
        return

    # see whether we are in the 5.Stock server. If not, give up.
    #bot5utils.GUILD = discord.utils.get(client.guilds,name=bot5utils.GUILDNAME)
    guild = discord.utils.get(client.guilds,name=bot5utils.GUILDNAME)
    if guild is None:
        raise Bot5Error("guild not found")
        await client.logout()


    try:
        client.load_extension("extensions.extensionmanager")
    except Exception as e:
        print(e)
        print("FATAL: unable to load extensionmanager. Shutting down.")
        await client.logout()
    else:
        print("loaded extensionmanager")

    try:
        await b5('ext').setup()
    except Exception as e:
        tr = traceback.format_exc()
        print(e)
        print(tr)
        print("Bot5 started, but something went wrong during setup.")
    else:
        print("Bot5 is online. All further messages shall be delivered via Discord.")




print("Starting bot.")
client.run(bot5utils.TOKEN)

