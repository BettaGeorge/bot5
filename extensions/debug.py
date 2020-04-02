# debug.py
# extension containing dangerous debugging tools
# these have to be enabled before use via the \debug command.

import bot5utils
from bot5utils import *
from bot5utils import ext as b5


class Debug(commands.Cog,name="Debug",command_attrs=dict(hidden=True)):
    def __init__(self,bot):
        self.bot = bot
        self.debugEnabled = False

    @commands.command(name="debug")
    @b5check("user",check="admin")
    async def debug(self,ctx):
        if self.debugEnabled:
            self.debugEnabled = False
            await ctx.send("Debugging ausgeschaltet")
        else:
            self.debugEnabled = True
            await ctx.send("VORSICHT! Debugging eingeschaltet!")

    @commands.command(name="massverify")
    @b5check("user",check="admin")
    async def massverify(self,ctx):
        if not self.debugEnabled:
            await ctx.send("Du musst mich erst aufschrauben. Benutze den \\debug Befehl.")
            return

        for i in b5('user').list():
            b5('user').get(i).forceVerify()



def setup(bot):
    bot.add_cog(Debug(bot))

def teardown(bot):
    bot.remove_cog('Debug')
