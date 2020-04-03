# logging.py
# SPECIAL EXTENSION
# this extension sets up basic logging to the Discord server. It should be loaded first by the ExtensionManager.


from bot5utils import *
#import bot5utils as b5
from bot5utils import ext as b5
import bot5utils

class Essential(commands.Cog,command_attrs=dict(hidden=True)):
    def __init__(self,bot):
        self.bot = bot
        self.syschannel = discord.utils.get(discord.utils.get(self.bot.guilds,name=bot5utils.GUILDNAME).text_channels,name="leo")


    async def debug(self,msg):
        await self.syschannel.send("[DEBUG] "+msg)

    async def log(self,msg):
        await self.syschannel.send(msg)





def setup(bot):
    bot.add_cog(Essential(bot))
    b5('ext').register('log',bot.get_cog('Essential'))
    #b5.sys = bot.get_cog('Essential')

def teardown(bot):
    #b5.sys = None
    b5('ext').unregister('log')
    bot.remove_cog('Essential')
