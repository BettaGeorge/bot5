# dsgvo.py
# extension for datenschutz.


from discord.ext import commands

from bot5utils import *
import bot5utils
from bot5utils import ext as b5



class DSGVO(commands.Cog, name="DSGVO"):
    def __init__(self,bot):
        self.bot = bot

    @commands.group(name="dsgvo",brief="Informationen zum Datenschutz und/oder Account löschen.")
    async def dsgvo(self,ctx):
        if ctx.invoked_subcommand is None:
            await b5("user").get(ctx.author.id).sendPM("""
**Datenschutz auf dem virtuellen fünften Stock**

Das wichtigste zuerst: Mit deiner Registrierung bei Discord hast du den Datenschutzrichtlinien von Discord (https://discordapp.com/privacy) zugestimmt. Was Discord mit deinen Daten anstellt, können wir nicht beeinflussen. Alle Angaben im folgenden Text beziehen sich nur auf _unsere_ Nutzung deiner Daten.

Leo (der Bot, der dir diese Nachricht geschickt hat) sammelt und verarbeitet personenbezogene Daten auf einem in Deutschland befindlichen Server, um den fünften Stock zu verwalten. Der Server wird betrieben von:

Adrian Rettich
Katharinenstraße 11
67655 Kaiserslautern
fs.leo@mathematik.uni-kl.de

Diese Daten beinhalten beispielsweise deine E-Mail-Adresse und deine Discord-ID.

Du kannst jederzeit sämtliche über dich gespeicherten Daten einsehen, indem du den Befehl `\\dsgvo einsicht` eingibst.

Du kannst jederzeit die Löschung aller deiner gespeicherten Daten beantragen, indem du den Befehl `\\dsgvo löschung` eingibst. Nach einer Bestätigungsabfrage werden dann alle über dich gespeicherten Daten sofort unwiederbringlich von meinem Server gelöscht. Beachte, dass du damit auch nicht mehr im fünften Stock Nachrichten schreiben oder lesen kannst.

Solltest du irgendwelche Fragen zum Datenschutz haben, kannst du an die E-Mail-Adresse _fs.leo@mathematik.uni-kl.de_ schreiben.
""")
            await ctx.send("Ich habe dir eine private Nachricht geschickt.")

    @dsgvo.command(name="einsicht", brief="Alle über dich gespeicherten Informationen in einer PM an dich schicken.")
    async def dsgvoeinsicht(self,ctx):
        u = b5("user").get(ctx.author.id)
        await u.sendPM(u.show(redacted=not u.isVerified()))
        await u.notifyAboutPM(ctx)

    @dsgvo.command(name="löschung", brief="Löscht alle deine Daten vom Server.")
    async def dsgvodelete(self,ctx):
        await ctx.send("Dieser Befehl löscht alle Daten, die wir von dir gespeichert haben (aber nicht die Daten, die Discord Inc. von dir gespeichert hat, vgl. `\\dsgvo`). Du wirst dadurch von unserem Server entfernt, weil wir zur Identitätsfeststellung deinen Account mit deinem RHRK-Login verknüpfen müssen. Du wirst nicht mehr in der Lage sein, Nachrichten auf dem fünften Stock zu sehen oder zu verschicken.\n\nUm fortzufahren, schreibe innerhalb der nächsten 60 Sekunden eine Nachricht, die nur das Wort```ja```enthält. Deine Daten werden dann mit sofortiger Wirkung gelöscht. (Wenn du stattdessen irgendeine andere Nachricht schreibst, gehe ich davon aus, dass du dich gegen die Löschung entschieden hast.)")
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        msg = None
        try:
            msg = await self.bot.wait_for('message',check=check,timeout=60)
        except:
            await ctx.send("Ich habe den Löschvorgang abgebrochen.")
        else:
            if msg.content in ["ja","Ja"]:
                await ctx.send("Mach es gut!")
                u = b5("user").get(ctx.author.id).inGuild()
                await b5("log").log("removed a user")
                await bot5utils.GUILD.kick(u,reason="Du hast die Löschung deiner Daten beantragt. Mach es gut!")
                b5("user").remove(ctx.author.id)
                await b5("log").log(b5("ext").reloadExtension("user"))
            else:
                await ctx.send("Ich habe den Löschvorgang abgebrochen.")
                


def setup(bot):
    bot.add_cog(DSGVO(bot))
    b5('ext').whitelistCommand('DSGVO','dsgvo')
    b5('ext').whitelistCommand('DSGVO','dsgvo einsicht')
    b5('ext').whitelistCommand('DSGVO','dsgvo löschung')


def teardown(bot):
    b5('ext').unwhitelistCommand('DSGVO','dsgvo')
    b5('ext').unwhitelistCommand('DSGVO','dsgvo einsicht')
    b5('ext').unwhitelistCommand('DSGVO','dsgvo löschung')
    bot.remove_cog('DSGVO')
