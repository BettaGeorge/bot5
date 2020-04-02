# bot5utils.py
# should be loaded by every file pertaining to Bot5
# includes:
# * necessary imports for the bot
# * global variables
# * custom exception classes
# * custom checks for the discord.command framework

import discord
from discord.ext import commands
from discord.ext.commands import Greedy
import logging
import os
import configparser # easy way to parse the config files which you can use to customize the bot
import sys # to parse command line arguments
from getpass import getpass # exactly what it says on the tin: a prompt that does not display the typed characters


logging.basicConfig(level=logging.INFO)

confpath = os.getenv('HOME')+"/.bot5"
conffile = confpath+"/config"
conffilesecret = confpath+"/private.config"

if len(sys.argv) > 1: # first argument is the name of the current script
    confpath = sys.argv[1]

# first, see whether there is a config directory
if not os.path.isdir(confpath) or not os.path.isfile(conffile):
    print("No config file at "+conffile+". Either this is the first time you started your bot, or you misspelled your config path.")
    try:
        inp = input("Create a new configuration file in "+confpath+" [y/N]?")
    except:
        print("aborting.")
        raise SystemExit
    if inp != "y":
        print("aborting.")
        raise SystemExit
    else:
        os.path.isdir(confpath) or os.makedirs(confpath) # os.mkdir would make a dir, but os.makedirs also creates subfolders if necessary
        newconf = configparser.ConfigParser()
        secretconf = configparser.ConfigParser()
        print("Creating config files. If you do not want to set a value right now, simply hit enter and later edit "+conffile+" and "+conffilesecret+" by hand.")
        secretconf['discord'] = {}
        secretconf['discord']['bot token'] = input("Discord bot token: ")
        newconf['discord'] = {}
        newconf['discord']['guild'] = input("Name of your discord server: ")
        newconf['email'] = {}
        newconf['email']['from'] = input("E-Mail address from which the bot should send: ")
        newconf['email']['smtp user'] = input("User name for SMTP: ")
        secretconf['email'] = {}
        secretconf['email']['smtp pass'] = getpass("SMTP password: ")

        with open(conffile,'w') as FILE:
            newconf.write(FILE)
        with open(conffilesecret,'w') as FILE:
            secretconf.write(FILE)

# by this point, we should have a valid config path. Hence it is time to load the values thence.
b5config = configparser.ConfigParser(allow_no_value = True) # allow_no_value allows us to simply list e.g. extension names as options
b5secret = configparser.ConfigParser()

# these three variables will be used in the other modules as well, so give them easily recognizable names
b5config.read(conffile)
b5secret.read(conffilesecret)
b5path = confpath

TOKEN = b5secret.get('discord','bot token',fallback='')
GUILDNAME = b5config.get('discord','guild',fallback='')
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
        


