# BOT5 EXTENSION
# DEPENDS: user
# komraum.py
# extension to manage the KOM room e.g. during board games night or breakfast.


#----------------------------------------------------------------------------
#"THE COFFEEWARE LICENSE":
#Adrian Rettich (adrian.rettich@gmail.com) wrote this file. As long as you retain this notice, you can do whatever you want with this stuff. If we should meet in person some day, and you think this stuff is worth it, you are welcome to buy me a coffee in return.  
#----------------------------------------------------------------------------


import bot5utils
from bot5utils import *
from bot5utils import ext as b5


class KOMRaum(commands.Cog,name="KOM-Raum"):
    def __init__(self,bot):
        self.bot = bot

    @commands.group(name="komraum",brief="Verwaltung des KOM-Raums.")
    async def kom(self,ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Ich weiß nicht, was du tun möchtest. Versuch's mit `\\hilfe komraum`.")

    # if channel is "", change all channels.
    # on failure, raises a Bot5Error.
    async def changeChannelPerms(self, category, channel=None, role=None, **kwargs):
        if isinstance(category,discord.CategoryChannel):
            cat = category
        else:
            cat = discord.utils.get(bot5utils.b5('ext').guild().categories,name=category)
            if cat is None:
                raise Bot5Error("Kategorie "+str(category)+" finde ich nicht.")

        if role is None:
            rl = bot5utils.b5('ext').guild().roles[0]
        elif isinstance(role,discord.Role):
            rl = role
        else:
            rl = discord.utils.get(b5('ext').guild().roles,name="role")
            if rl is None:
                raise Bot5Error("Die Rolle "+str(role)+" kenne ich nicht.")

        toChange = cat

        if channel is not None:
            if isinstance(channel,discord.VoiceChannel):
                toChange = channel
            else:
                toChange = discord.utils.get(cat.voice_channels,name=channel)
                if toChange is None:
                    raise Bot5Error("Den Channel "+str(channel)+" finde ich nicht.")

        # toChange is now either a CategoryChannel or a VoiceChannel.
        try:
            await toChange.set_permissions(rl,**kwargs)
            if isinstance(toChange,discord.CategoryChannel):
                for c in toChange.voice_channels:
                    await self.changeChannelPerms(toChange,c,role,**kwargs)
        except Exception as e:
            raise Bot5Error("Editing category failed!\n"+str(e))
        else:
            return True

    @kom.command(name="ordnung",brief="Push to Talk einschalten.")
    @b5check('user',role=["Spieleabend","Vorsitz","FSR"])
    async def kompush(self,ctx,*,arg=None):
        try:
            await self.changeChannelPerms("KOM-Raum",arg,b5('ext').guild().roles[0],use_voice_activation=False)
        except Bot5Error as e:
            await ctx.send("Konnte Berechtigungen nicht ändern!\n"+str(e))
        else:
            wh = "überall" if arg is None else arg
            await ctx.send("Push to Talk ist jetzt "+wh+" Pflicht.")

    @kom.command(name="chaos",brief="Voice Activation erlauben.")
    @b5check('user',role=["Spieleabend","Vorsitz","FSR"])
    async def komnopush(self,ctx,*,arg=None):
        try: 
            await self.changeChannelPerms("KOM-Raum",arg,b5('ext').guild().roles[0],use_voice_activation=True)
        except Bot5Error as e:
            await ctx.send("Konnte Berechtigungen nicht ändern!\n"+str(e))
        else:
            wh = "überall" if arg is None else arg
            await ctx.send("Voice Activation ist jetzt "+wh+" erlaubt.")

    @commands.command(name="kaffee",brief="Eine Tasse Kaffee machen.")
    async def coffee(self,ctx):
        ch = ctx.message.author.voice.voice_channel
        if ch is not None:
            if ch = discord.utils.get(bot5utils.GUILD().voice_channels,name="an der Kaffeemaschine"):
                await ctx.send("\N{HOT BEVERAGE}")
                return
        await ctx.send("Du musst an die Kaffeemaschine gehen.")


def setup(bot):
    bot.add_cog(KOMRaum(bot))

def teardown(bot):
    bot.remove_cog('KOM-Raum')
