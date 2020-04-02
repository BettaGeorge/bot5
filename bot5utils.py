# bot5utils.py
# should be loaded by every file pertaining to Bot5
# includes:
# * necessary imports for the bot
# * global variables
# * custom exception classes
# * custom checks for the discord.command framework
# note: global variables HAVE TO BE referenced as bot5utils.VAR in order to work in files that import this one. I suggest importing bot5utils as b5 to shorten notation.

import discord
from discord.ext import commands
from discord.ext.commands import Greedy
import logging
import os
from dotenv import load_dotenv
logging.basicConfig(level=logging.INFO)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
MY_ADDRESS = os.getenv('BOT_EMAIL')
PASSWORD = os.getenv('BOT_EMAIL_PASSWORD')
GUILDNAME = TOKEN = os.getenv('DISCORD_GUILD')
GUILD = None

# this shall reference the unique instance of the class ExtensionVariables from the extensionmanager extension.
extensionVariables = None

class Bot5Error(Exception):
    """Custom exception class for Bot5"""
    def __init__(self,message):
        self.message=message


def ext(identifier: str):
    if extensionVariables is None:
        raise Bot5Error("ext called before extensionVariables was instantiated")

    return extensionVariables.get(identifier)


# this checks whether the bot loading has already happened. You can use this to make sure certain code during setup is never called more than once.
def bot5Loaded():
    if extensionVariables is None:
        return False
    else:
        return True



# okay, so here's how to dynamically implement custom command checks:
# in a class registered with the ExtensionManager, add a routine called b5check that takes at least the arguments (self,ctx) and as many additional arguments as you need for your check.
# you can then decorate commands in ANY extension with
# @b5check("ext")
# where "ext" is the name under which the class containing the check is registered.
# If you want to pass additional arguments, decorate with @b5check("ext",arg1,...) instead.
# If your class is not registered at the time the command is called, the check automatically fails. This means that users are not able to execute arbitrary commands just because you cannot verify their permissions right now.
def b5check(extension: str, *args, **kwargs):
    async def _b5check(ctx):
        print("B5CHECK called")
        ref = ext(extension)
        if ref is None:
            print("B5CHECK: unknown ref '"+extension)
            return False
        try:
            return await ref.b5check(ctx,*args,**kwargs)
        except Exception as e:
            print("B5CHECK: exception")
            print(str(e))
            return False
    return commands.check(_b5check)
        


