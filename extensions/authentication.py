# BOT5 EXTENSION
# DEPENDS: user, email
# authentication.py
# extension with the Authentication cog.
# contains commands for the registration on the 5th floor.

# TODO: don't allow more than three guesses


#----------------------------------------------------------------------------
#"THE COFFEEWARE LICENSE":
#Adrian Rettich (adrian.rettich@gmail.com) wrote this file. As long as you retain this notice, you can do whatever you want with this stuff. If we should meet in person some day, and you think this stuff is worth it, you are welcome to buy me a coffee in return.  
#----------------------------------------------------------------------------




from discord.ext import commands

from bot5utils import *
import bot5utils
from bot5utils import ext as b5

import re
re_ersti = re.compile('^sicherlich$',re.I)

import time
from random import randint

from enum import Enum

AUTH_TIMEOUT = 60*60

# Account = Enum('Account','TUK ERSTI GUEST UNVERIFIED')
# apparently enums are utterly unpickleable. As soon as I use this, pickling always fails.
# Can't pickle <enum 'Account'>: it's not the same object as extensions.authentication.Account

_ = b5('ext')._('authentication')



class Authentication(commands.Cog, name="Registrierung"):
    def __init__(self,bot):
        self.bot = bot

    async def welcomeMessage(self,u):
        await u.sendPM(_("Hello $username! Welcome to our server.",username=u.inGuild().name))

    async def verify(self, 
            user,
            code: int, 
            force: bool=False, 
            accountType="TUK"
            ) -> bool:

        if force or (user.get('authCode') > 0 and user.get('authCode')==code and time.time()<user.get('authCodeValidUntil')):
            user.set('verified',True)
            newrole = discord.utils.get(b5('ext').guild().roles,name='Studi')
            await user.inGuild().add_roles(newrole)
            user.set('accountType',accountType)
            if user.get('rhrk') != '':
                await user.inGuild().edit(nick=user.get('rhrk')+"@rhrk")
        return user.get('verified')

    async def erstiVerify(self,
            user,
            wort: str
            ) -> bool:

        if re_ersti.match(wort) is None:
            return False
        newrole = discord.utils.get(b5('ext').guild().roles,name="Ersti")
        await user.inGuild().add_roles(newrole)
        return await self.verify(user,0,True,"ERSTI")

    def generateAuthCode(self, user, timeout: float=60*60):
        user.set('authCode',randint(1,10000))
        user.set('authCodeValidUntil',time.time()+timeout)
        return user.get('authCode')


    @commands.Cog.listener()
    async def on_member_join(self,member):
        # TODO: what if ID already in USERS?
        existing_user = b5('user').get(member.id)
        if existing_user is not None:
            await b5('log').debug("WARNING: "+str(member.display_name)+" just joined, but already exists as follows\n"+existing_user.show())
        u = b5('user').add(member.id)
        await self.welcomeMessage(u)
        

    @commands.Cog.listener()
    async def on_member_remove(self,member):
        u = b5('user').get(member.id)
        if u is None:
            await b5('log').debug("WARNING: "+str(member.display_name)+" left the guild, but was not in my memory")
            return
        b5('user').remove(member.id)

    @commands.command(name=_("rhrk"),brief=_("Set your RHRK username."))
    async def rhrk(self,ctx,*args):

        # we need an argument:
        if len(args) == 0:
            await ctx.send(_("Please provide a username."))
            return

        # TODO: allow Erstis to set their RHRK account a posteriori
        if b5('user').get(ctx.author.id) is not None and b5('user').get(ctx.author.id).get('verified'):
            await ctx.send(_("Your account is already verified."))
            return

        async with ctx.channel.typing():
            # find the user in our database:
            print(f"DEBUG: rhrk message from {ctx.author.id}")
            try:
                u = b5('user').get(ctx.author.id)
            except KeyError:
                await ctx.send("Database error. Please leave the server and rejoin via the invite link.")
                raise Bot5Error("rhrk: user was None")
                return

            # assign necessary variables
            rhrk_mail = args[0]
            auth_int = self.generateAuthCode(u,timeout=AUTH_TIMEOUT) #randint(1,10000)
            
            # try sending an email with the generated code
            mailcontent = _("You are getting this email because you requested a verification code from Bot5. Your code is $code.",code=auth_int)
            try:
                b5('email').send(rhrk_mail+'@rhrk.uni-kl.de',_("Bot5 Verification Email"),mailcontent)
            except Exception as e:
                print(e)
                await ctx.send(_("Could not send you an email."))
                return

        u.set('rhrk',rhrk_mail)
        await ctx.send(_("I have sent your verification code to $email.",email=rhrk_mail+'@rhrk.uni-kl.de'))


    @commands.command(name=_("code"),brief=_("Command to enter your authentication code."))
    async def code(self,ctx,*args):
        if len(args) == 0:
            await ctx.send(_("Missing mandatory argument: verification code."))
            return

        if b5('user').get(ctx.author.id) is not None and b5('user').get(ctx.author.id).get('verified'):
            await ctx.send(_("Your account is already verified."))
            return

        entered_code = args[0]
        try:
            u = b5('user').get(ctx.author.id)
        except KeyError:
            await ctx.send(_("Database error. Please leave the server and rejoin via the invite link."))
            raise Bot5Error("code: user was None")
            return

        if await self.verify(u,int(entered_code)):
            await ctx.send(_("Code correct. You are now verified."))
        else:
            await ctx.send(_("Code incorrect or expired. Please try again."))

    @commands.command(name=_("ersti"), brief=_("Command to verify as Ersti."))
    async def ersti(self,ctx, *wort):
        if b5('user').get(ctx.author.id) is not None and b5('user').get(ctx.author.id).get('verified'):
            await ctx.send(_("Your account is already verified."))
            return

        u = b5('user').get(ctx.author.id)
        if u is None:
            await ctx.send(_("Database error. Please leave the server and rejoin via the invite link."))
            return

        if len(wort) == 0:
            await ctx.send(_("Instructions for Ersti verification go here."))

        else:
            if await self.erstiVerify(u,wort[0]):
                await ctx.send(_("Code correct. You are now verified."))
            else:
                await ctx.send(_("Text for failed Ersti verification goes here."))

    @commands.command(name=_("erstihelp"), brief=_("Command to get help for first semesters."))
    async def erstihilfe(self,ctx):
        if b5('user').get(ctx.author.id) is not None and b5('user').get(ctx.author.id).get('verified'):
            await ctx.send(_("Your account is already verified."))
            return

            u = b5('user').get(ctx.author.id)
            subject = "LEOBOT: Ersti-Anfrage"
            mailcontent = "Jemand hat den Erstihilfe-Befehl verwendet. Folgendes weiß ich:\n"+u.show()
            b5('email').send("fs.leo@mathematik.uni-kl.de",subject,mailcontent)
            await ctx.send(_("An administrator will contact you regarding your verification."))





# global var to hold our help command
helpcommand = None
helpcommand1 = None
#helpcommand2 = None
# TODO: 

def setup(bot):
    a = Authentication(bot)
    bot.add_cog(a)
    try:
        bot.remove_command("help")
    except:
        pass
    global helpcommand
    global helpcommand1
    helpcommand = commands.DefaultHelpCommand(command_attrs=dict(name=_("help"),brief=_("Show help.")),verify_checks=False)
    helpcommand1 = commands.DefaultHelpCommand(command_attrs=dict(name=_("help command two"),brief=_("Show help.")),verify_checks=False)
    #helpcommand2 = commands.DefaultHelpCommand(command_attrs=dict(name="leo",brief="Hilfe anzeigen."))
    helpcommand._add_to_bot(bot)
    helpcommand1._add_to_bot(bot)
    #helpcommand2._add_to_bot(bot)

    # allow unverified users to verify:
    b5('ext').whitelistCommand('Registrierung',_('rhrk'))
    b5('ext').whitelistCommand('Registrierung',_('ersti'))
    b5('ext').whitelistCommand('Registrierung',_('code'))
    b5('ext').whitelistCommand('Registrierung',_('erstihelp'))

    b5('ext').whitelistCommand(None,_("help"))
    b5('ext').whitelistCommand(None,_("help command two"))

    b5('ext').register('auth',a)

    b5('user').registerField('auth','verified',bool,False)
    b5('user').registerField('auth','authCode',int,0)
    b5('user').registerField('auth','authCodeValidUntil',float,0.0)
    b5('user').registerField('auth','accountType',str,"UNVERIFIED")
    b5('user').registerField('auth','rhrk',str,'')




def teardown(bot):
    # remove whitelisted commands
    b5('ext').unwhitelistCommand('Registrierung',_('rhrk'))
    b5('ext').unwhitelistCommand('Registrierung',_('ersti'))
    b5('ext').unwhitelistCommand('Registrierung',_('code'))
    b5('ext').unwhitelistCommand('Registrierung',_('erstihelp'))
    b5('ext').unwhitelistCommand(None,_("help"))
    b5('ext').unwhitelistCommand(None,_("help command two"))

    b5('ext').unregister('auth')
    
    bot.remove_cog('Registrierung')
    helpcommand._remove_from_bot(bot)
    helpcommand1._remove_from_bot(bot)
    #helpcommand2._remove_from_bot(bot)
