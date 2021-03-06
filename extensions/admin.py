# BOT5 EXTENSION
# DEPENDS: user
# admin.py
# this is an extension to Bot5 containing the Admin cog. It should hold all commands that regular users are not allowed to run, but admins are.


#----------------------------------------------------------------------------
#"THE COFFEEWARE LICENSE":
#Adrian Rettich (adrian.rettich@gmail.com) wrote this file. As long as you retain this notice, you can do whatever you want with this stuff. If we should meet in person some day, and you think this stuff is worth it, you are welcome to buy me a coffee in return.  
#----------------------------------------------------------------------------



from bot5utils import *
from bot5utils import ext as b5
import bot5utils



class Admin(commands.Cog,command_attrs=dict(hidden=True)):
    def __init__(self,bot):
        self.bot = bot



class System(commands.Cog,command_attrs=dict(hidden=True)):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.group(name="extension",brief="Plugin Management.")
    @b5check("user",check="admin")
    async def extension(self,ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Bitte gib ein Kommando an")
    
    @extension.command(name="load", brief="Ein neues Plugin laden.")
    @b5check("user",check="admin")
    async def b5load(self,ctx,ext):
        try:
            b5('ext').loadExtension(ext)
        except Exception as e:
            await b5('log').log("load "+ext+": exception\n"+str(e))
        else:
            await b5('log').log("load "+ext+": success")

    @extension.command(name="reload", brief="Ein bestehendes Plugin neu laden.")
    @b5check("user",check="admin")
    async def b5reload(self,ctx,ext):
        try:
            b5('ext').reloadExtension(ext)
        except Exception as e:
            await b5('log').log("reload "+ext+": exception\n"+str(e))
        else:
            await b5('log').log("reload "+ext+": success")

    @extension.command(name="forceunload")
    @b5check("user",check="admin")
    async def b5forceunload(self,ctx,ext):
        try:
            b5('ext').unloadExtension(ext,force=True)
        except Exception as e:
            await b5('log').log("unload "+ext+": exception\n"+str(e))
        else:
            await b5('log').log("unload "+ext+": success")


    @commands.command(name="shoo",brief="Leo schlafen schicken. Nur Adrian kann ihn dann neu starten.")
    @b5check("user",check="admin")
    async def shoo(self,ctx):
        await ctx.send("Ich mache mich auf den Weg.")
        await b5('ext').teardown()
        await ctx.send("Okay, bis später!")
        await self.bot.logout()

    @commands.command(name="send",brief="Leo in einem bestimmten Channel etwas sagen lassen.")
    @b5check("user",check="admin")
    async def b5send(self, ctx, channel: str, message: str):
        c = discord.utils.get(b5('ext').guild().text_channels,name=channel)
        if c is not None:
            await c.send(message)


    @commands.command(name="pm",brief="Eine Nachricht an einen Discord-User schicken")
    @b5check("user",check="admin")
    async def b5pm(self,ctx,user:str):
        username = user[0:-5]
        userdisc = user[-4:]
        u = discord.utils.get(b5('ext').guild().members,name=username,discriminator=userdisc)
        if u is None:
            await ctx.send("Dieser User ist nicht auf dem Server.")
            return
        await ctx.send("Deine nächste Nachricht wird an "+u.display_name+" gesendet.")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        try:
            msg = await self.bot.wait_for('message',check=check,timeout=120)
        except:
            await ctx.send("Ich habe den Sendevorgang abgebrochen.")
        else:
            await u.create_dm()
            await u.dm_channel.send(msg.content)
            await ctx.send("Gesendet.")


# global var for referencing an additional help command in setup and teardown
adminhelpcommand = None


def setup(bot):
    bot.add_cog(Admin(bot))
    bot.add_cog(System(bot))

    # add a second help command that shows hidden commands for admins
    global adminhelpcommand
    adminhelpcommand = commands.DefaultHelpCommand(show_hidden=True, verify_checks=False, command_attrs=dict(name="adminhelp",brief="Hilfe für Administratoren."))
    adminhelpcommand._add_to_bot(bot)

def teardown(bot):
    bot.remove_cog('Admin')
    bot.remove_cog('System')

    global adminhelpcommand
    adminhelpcommand._remove_from_bot(bot)
