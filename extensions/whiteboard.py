# whiteboard.py
# this is an extension to Bot5 containing the Whiteboard cog. It should hold all commands that do something with the whiteboard.


from bot5utils import *
import bot5utils
from bot5utils import ext as b5

import datetime

import re
re_command = re.compile('^\\\\')
re_setwdt = re.compile('.*wort\\s*(des)?\\s*tage?s?.*"(\\S+)"',re.IGNORECASE)
re_almostsetwdt = re.compile('.*wort\\s*(des)?\\s*tage?s?.*(\\S+)',re.IGNORECASE) # same as setwdt, but the user forgot the quote marks
re_getwdt = re.compile('.*wort\\s*(des)?\\s*tage?s?\\s*\\?',re.IGNORECASE)

class Word:
    def __init__(self,wort):
        self.word = wort
        self.date = Whiteboard.today()
        self.message = None

class Whiteboard(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.channel = discord.utils.get(bot5utils.GUILD.text_channels,name="whiteboard")

        # list of words indexed by YYYYMMDD.
        self.words = {}
        try:
            self.words = b5('persist').load('wortdestages.bot5')
        except FileNotFoundError as e:
            print(e)
            print("Keine gespeicherten Wörter des Tages!")

    @staticmethod
    def today():
        return datetime.datetime.now().strftime('%Y%m%d')

    def getWord(self):
        if Whiteboard.today() in self.words:
            return self.words[Whiteboard.today()]
        else:
            return None

    def getWordAsFormattedOutput(self):
            if self.getWord() is None:
                return "Es gibt noch kein Wort des Tages."
            else:
                return "Das Wort des Tages ist \""+self.getWord().word+"\"."

    async def setWord(self,wort):
        if self.getWord() is None:
            w = Word(wort)
            self.words[Whiteboard.today()] = w
            m = await self.channel.send("Wort des Tages: "+w.word)
            w.message = m.id
            return "Ich habe \""+w.word+"\" als Wort des Tages ans Whiteboard geschrieben."
        else:
            return "Tut mir Leid, aber das Wort des Tages ist bereits \""+self.getWord().word+"\"."


    @commands.command(name="wort",brief="show or set word of the day")
    async def wort(self,ctx,*wort):
        if len(wort) == 0:
            await ctx.send(self.getWordAsFormattedOutput())
        else:
            await ctx.send(await self.setWord(wort[0]))

    @commands.command(name="wortAuswischen", brief="Heutiges Wort des Tages entfernen", hidden=True)
    @b5check("user",check="admin")
    async def wortAuswischen(self,ctx):
        if Whiteboard.today() not in self.words:
            await ctx.send("Es ist kein Wort des Tages gesetzt.")
            return
        try:
            m = await self.channel.fetch_message(self.words[Whiteboard.today()].message)
        except:
            pass
        else:
            await m.delete()
        self.words.pop(Whiteboard.today(),None)
            

            
    @commands.Cog.listener()
    async def on_message(self,message):
        if message.author == self.bot.user:
            return
        if message.channel == self.channel and re_command.match(message.content):
            await message.delete(delay=2)
        if re_command.match(message.content):
            return
        if re_getwdt.match(message.content):
            await message.channel.send(self.getWordAsFormattedOutput())
        else:
            if re_almostsetwdt.match(message.content):
                mat = re_setwdt.match(message.content)
                if mat:
                    m = await self.setWord(mat.group(2))
                    await message.channel.send(m)
                else:
                    await message.channel.send("Hinweis: Wenn du das Wort des Tages anschreiben möchtest, setze es in \"Anführungszeichen\", damit ich weiß, was ich ans Whiteboard schreiben soll.")
                # if someone tries to set the word on the whiteboard, we end up with two messages proclaiming the word of the day -- one from Bot5 and one from the user. Delete the superfluous one.
                if message.channel == self.channel:
                    await message.delete(delay=2)



def setup(bot):
    w = Whiteboard(bot)
    bot.add_cog(w)
    b5('ext').register('whiteboard',w)

def teardown(bot):
    b5('persist').save('wortdestages.bot5',b5('whiteboard').words)
    bot.remove_cog('Whiteboard')
    b5('ext').unregister('whiteboard')
