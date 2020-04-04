# BOT5 EXTENSION
# DEPENDS: user, email
# authentication.py
# extension with the Authentication cog.
# contains commands for the registration on the 5th floor.

# TODO: don't allow more than three guesses


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

Account = Enum('Account','TUK ERSTI GUEST UNVERIFIED')

print("setting up translations")
_ = b5('ext')._('authentication')



class Authentication(commands.Cog, name="Registrierung"):
    def __init__(self,bot):
        self.bot = bot

    async def welcomeMessage(self,u):
        await u.sendPM(_("Hallo $username! Ich bin Leo, das Maskottchen der Fachschaft Mathematik. Ich sorge dafür, dass auf dem fünften Stock alles funktioniert.",username=u.inGuild().name))
        await u.sendPM(_("Um Spam zu vermeiden, dürfen nur Mitglieder der TUK den fünften Stock betreten. Bitte schreib mir eine Nachricht der Form `\\rhrk nutzer`, wobei du 'nutzer' durch deinen Nutzernamen beim RHRK ersetzt (vergiss nicht den Backslash ganz am Anfang, wie bei LaTeX). Ich schicke dir dann eine Nachricht an deine RHRK-Email, um deine Identität zu bestätigen."))
        await u.sendPM("Falls du Ersti bist (und noch keinen RHRK-Login per Post erhalten hast), schreibe stattdessen `\\ersti`.")
        await u.sendPM("Solltest du einmal vergessen, wie du mit mir redest, gib einfach hier oder irgendwo auf dem fünften Stock `\\hilfe `ein.")
        await u.sendPM("Mit der Nutzung der Befehle `\\rhrk` oder `\\ersti` stimmst du der automatisierten Verarbeitung deiner Daten auf unserem Server zu. Für weitere Informationen gib `\\dsgvo` ein, um unsere Datenschutzerklärung einzusehen.")

    async def verify(self, 
            user,
            code: int, 
            force: bool=False, 
            accountType=Account.TUK
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
        return await self.verify(user,0,True,Account.ERSTI)

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

    @commands.command(name="rhrk",brief="Deinen RHRK-Nutzernamen setzen.")
    async def rhrk(self,ctx,*args):

        # we need an argument:
        if len(args) == 0:
            await ctx.send("Bitte gib einen Nutzernamen an.")
            return

        # TODO: allow Erstis to set their RHRK account a posteriori
        if b5('user').get(ctx.author.id) is not None and b5('user').get(ctx.author.id).get('verified'):
            await ctx.send("Dein Account ist bereits verifiziert.")
            return

        async with ctx.channel.typing():
            # find the user in our database:
            print(f"DEBUG: rhrk message from {ctx.author.id}")
            try:
                u = b5('user').get(ctx.author.id)
            except KeyError:
                await ctx.send("Etwas ist schrecklich schief gelaufen. Bitte verlasse den Server und tritt neu bei.")
                raise Bot5Error("rhrk: user was None")
                return

            # assign necessary variables
            rhrk_mail = args[0]
            auth_int = self.generateAuthCode(u,timeout=AUTH_TIMEOUT) #randint(1,10000)
            
            # try sending an email with the generated code
            mailcontent = f"Du bekommst diese E-Mail, weil du dich auf dem Discord-Server im 5. Stock angemeldet hast. Dein Authentifizierungscode ist {auth_int}. Sende Leo folgende Nachricht:\n\n\\code {auth_int}\n\nDu hast eine Stunde lang Zeit, um den Code zu verwenden.\n\nDein Leo"
            try:
                b5('email').send(rhrk_mail+'@rhrk.uni-kl.de',"Discord: 5. Stock",mailcontent)
            except Exception as e:
                print(e)
                await ctx.send("Ich konnte dir keine E-Mail schicken. Bitte versuche es erneut oder kontaktiere einen Admin per Mail an fs.leo@mathematik.uni-kl.de.")
                return

        u.set('rhrk',rhrk_mail)
        await ctx.send(f"Ich habe dir eine E-Mail mit weiteren Anweisungen an {rhrk_mail}@rhrk.uni-kl.de geschickt.")


    @commands.command(name="code",brief="Deinen Anmeldecode eingeben.")
    async def code(self,ctx,*args):
        if len(args) == 0:
            await ctx.send("Bitte gib einen Code an.")
            return

        if b5('user').get(ctx.author.id) is not None and b5('user').get(ctx.author.id).get('verified'):
            await ctx.send("Dein Account ist bereits verifiziert.")
            return

        entered_code = args[0]
        try:
            u = b5('user').get(ctx.author.id)
        except KeyError:
            await ctx.send("Etwas ist schrecklich schief gelaufen. Bitte verlasse den Server und tritt neu bei.")
            raise Bot5Error("code: user was None")
            return

        if await self.verify(u,int(entered_code)):
            await ctx.send("Vielen Dank! Du solltest jetzt Zugriff auf den fünften Stock haben. Falls nicht, schreib eine E-Mail an fs.leo@mathematik.uni-kl.de.")
        else:
            await ctx.send("Es tut mir sehr Leid, aber dieser Code ist falsch oder abgelaufen. Du kannst einen neuen Code anfordern, indem du mir nochmal deinen RHRK-Nutzernamen übermittelst:```\\rhrk nutzer```")
            await ctx.send("Wenn du ganz sicher bist, dass dein Code stimmt, schreib eine E-Mail an fs.leo@mathematik.uni-kl.de.")

    @commands.command(name="ersti", brief="Rufe dieses Kommando auf, wenn du Ersti bist.")
    async def ersti(self,ctx, *wort):
        if b5('user').get(ctx.author.id) is not None and b5('user').get(ctx.author.id).get('verified'):
            await ctx.send("Dein Account ist bereits verifiziert.")
            return

        u = b5('user').get(ctx.author.id)
        if u is None:
            await ctx.send("Etwas ist in unserem Code schief gelaufen. Bitte verlasse den Server und tritt neu bei, oder schreib eine E-Mail an fs.leo@mathematik.uni-kl.de.")
            return

        if len(wort) == 0:
            await ctx.send("Willkommen in der Fachschaft Mathe! Um Spam zu vermeiden, müssen wir leider sicherstellen, dass du wirklich als Ersti eingeschrieben bist. Unser Geschäftsführer Herr Lossen hat dir eine E-Mail mit dem Betreff 'Informationen zum Studieneinstieg' geschickt. Darin sagt er:```Wir möchten Sie hiermit am Fachbereich Mathematik der TUK herzlich willkommen heißen!```Was ist das erste Wort nach diesem Absatz? Schicke mir eine Nachricht der Form ```\\ersti wort```wobei du 'wort' durch dieses Wort ersetzt, um dich zu registrieren.")
            await ctx.send("Du hast die E-Mail nicht erhalten oder bereits gelöscht? Kein Problem, schreib einfach```\\erstihilfe```um einen Administrator zu kontaktieren, der dich von Hand freischaltet. Bitte gedulde dich in diesem Fall bis zu ein paar Stunden, weil wir das Ganze in unserer Freizeit machen und vielleicht gerade nicht am Computer sind.")

        else:
            if await self.erstiVerify(u,wort[0]):
                await ctx.send("Vielen Dank! Du solltest jetzt Zugriff zu unserem Server haben. Willkommen!")
            else:
                await ctx.send("Das eingegebene Wort ist leider falsch, oder du hast bereits drei Fehlversuche. In diesem Fall kontaktiere bitte einen Administrator via```\\erstihilfe```oder unter der E-Mail-Adresse fs.leo@mathematik.uni-kl.de. Tut mir Leid, dass wir dir so viel Arbeit machen.")

    @commands.command(name="erstihilfe", brief="Kontaktiert einen Administrator.")
    async def erstihilfe(self,ctx):
        if b5('user').get(ctx.author.id) is not None and b5('user').get(ctx.author.id).get('verified'):
            await ctx.send("Dein Account ist bereits verifiziert.")
            return

            u = b5('user').get(ctx.author.id)
            subject = "LEOBOT: Ersti-Anfrage"
            mailcontent = "Jemand hat den Ersti-Befehl verwendet. Folgendes weiß ich:\n"+u.show()
            b5('email').send("fs.leo@mathematik.uni-kl.de",subject,mailcontent)
            await ctx.send("Ich habe die Administratoren kontaktiert, damit sie dich von Hand freischalten. Das kann leider auch mal einen Tag dauern. Einer der Admins wird dich hier auf Discord kontaktieren.")





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
    helpcommand = commands.DefaultHelpCommand(command_attrs=dict(name="help",brief="Hilfe anzeigen."),verify_checks=False)
    helpcommand1 = commands.DefaultHelpCommand(command_attrs=dict(name="hilfe",brief="Hilfe anzeigen."),verify_checks=False)
    #helpcommand2 = commands.DefaultHelpCommand(command_attrs=dict(name="leo",brief="Hilfe anzeigen."))
    helpcommand._add_to_bot(bot)
    helpcommand1._add_to_bot(bot)
    #helpcommand2._add_to_bot(bot)

    # allow unverified users to verify:
    b5('ext').whitelistCommand('Registrierung','rhrk')
    b5('ext').whitelistCommand('Registrierung','ersti')
    b5('ext').whitelistCommand('Registrierung','code')
    b5('ext').whitelistCommand('Registrierung','erstihilfe')

    b5('ext').whitelistCommand(None,'help')
    b5('ext').whitelistCommand(None,'hilfe')

    b5('ext').register('auth',a)

    b5('user').registerField('auth','verified',bool,False)
    b5('user').registerField('auth','authCode',int,0)
    b5('user').registerField('auth','authCodeValidUntil',float,0.0)
    b5('user').registerField('auth','accountType',Account,Account.UNVERIFIED)
    b5('user').registerField('auth','rhrk',str,'')




def teardown(bot):
    # remove whitelisted commands
    b5('ext').unwhitelistCommand('Registrierung','rhrk')
    b5('ext').unwhitelistCommand('Registrierung','ersti')
    b5('ext').unwhitelistCommand('Registrierung','code')
    b5('ext').unwhitelistCommand('Registrierung','erstihilfe')
    b5('ext').unwhitelistCommand(None,'help')
    b5('ext').unwhitelistCommand(None,'hilfe')

    b5('ext').unregister('auth')
    
    bot.remove_cog('Registrierung')
    helpcommand._remove_from_bot(bot)
    helpcommand1._remove_from_bot(bot)
    #helpcommand2._remove_from_bot(bot)
