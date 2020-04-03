# BOT5 EXTENSION
# misc.py
# extension containing everything for which I had no better place

from bot5utils import *
import bot5utils
from bot5utils import ext as b5

import subprocess

import re
re_command = re.compile('^\\\\')


class Misc(commands.Cog, name="Verschiedenes"):
    def __init__(self,bot):
        self.bot = bot

#    @commands.Cog.listener()
#    async def on_message(self,message):
#        if message.author == self.bot.user:
#            return

#        # reply if Bot5 was mentioned
#        # or if we are in a private chat <=> not on a server <=> message.guild is None
#        if self.bot.user in message.mentions or message.guild is None:
#            # of course, if this is a command, we don't need to react:
#            if not re_command.match(message.content):
#                await message.channel.send("Hi! Ich sehe, du hast mich angesprochen. Ich bin noch nicht gut genug programmiert, um damit umzugehen, aber hier ist ein weiser Spruch für dich.")
#                wisout = subprocess.check_output("wisdom",shell=True)
#                await message.channel.send(wisout)

        # you usually need the following to hand the message over to the command framework if you override on_message().
        # but as far as I can tell, this is NOT needed anymore once you implement everything as cogs.
        # if you do include it, commands are processed twice.
        #await self.bot.process_commands(message)


    @commands.command(name="echo",brief="Lass Leo etwas sagen.", description='Beispiel: \\echo "Du bist wunderbar." lässt Leo dir positive Rückmeldung geben.')
    async def b5echo(self,ctx,*,arg="Hallo!"):
        await ctx.send(arg)

    @commands.Cog.listener()
    async def on_command_error(self,ctx,error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Diesen Befehl kenne ich nicht. `\\hilfe` listet alle gültigen Befehle auf.")
        elif isinstance(error,commands.CheckFailure):
            pass # we provide feedback to checks within the checks, so this is taken care of
        else:
            raise error



def setup(bot):
    bot.add_cog(Misc(bot))

def teardown(bot):
    bot.remove_cog('Verschiedenes')
