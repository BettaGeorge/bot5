# BOT5 EXTENSION
# DEPENDS: persistence
# user.py
# extension for user management

import bot5utils
from bot5utils import *
from bot5utils import ext as b5

from random import randint
import time

from enum import Enum

import re
re_ersti = re.compile('^sicherlich$',re.I)

Account = Enum('Account','TUK ERSTI GUEST UNVERIFIED')

# type hinting classes needs type vars:
T = TypeVar('T')

class UserCog(commands.Cog,name="User",command_attrs=dict(hidden=True)):

    def __init__(self,bot):
        self.bot = bot

    @commands.group()
    @b5check("user",check="admin")
    async def user(self,ctx:commands.Context) -> None:
        if ctx.invoked_subcommand is None:
            await ctx.send("Bitte gib ein Kommando an")

    @user.command(name="info",brief="show what Bot5 knows about a user")
    @b5check("user",check="admin")
    async def userinfo(self,ctx: commands.Context, members: Greedy[discord.Member]) -> None:
        for m in members:
            await ctx.send(b5('user').get(m.id).show())

    @user.group(name="list",brief="show a list of all users known to Bot5")
    @b5check("user",check="admin")
    async def userlist(self,ctx: commands.Context) -> None:
        if ctx.invoked_subcommand is None:
            await ctx.send(str(b5('user').nameList()))


    @userlist.command(name="unknown",brief="Zeige die Benutzer, die auf dem Server sind, aber nicht in der Datenbank.")
    @b5check("user",check="admin")
    async def userlistunknown(self,ctx):
        known = [u.getID() for u in b5("user").list()]
        for m in b5('ext').guild().members:
            if m.id not in known:
                await ctx.send(str(m)+", roles: "+str(discord.utils.get(b5('ext').guild().members,id=m.id).roles))

    @userlist.command(name="slipped",brief="Zeige die Benutzer, die zwar verifiziert sind, aber nicht in der Datenbank.")
    @b5check("user",check="admin")
    async def userlistslipped(self,ctx):
        known = [u.getID() for u in b5("user").list()]
        for m in b5('ext').guild().members:
            if m.id not in known and len(discord.utils.get(b5('ext').guild().members,id=m.id).roles)>1:
                await ctx.send(m)

    @user.command(name="verify",brief="Benutzer freischalten.")
    @b5check("user",check="admin")
    async def userverify(self,ctx,members: Greedy[discord.Member]):
        for m in members:
            u = b5("user").get(m.id)
            if u is None:
                await ctx.send(m.display_name+" nicht gefunden.")
            else:
                await u.forceVerify()
                await ctx.send(u.inGuild().display_name+" ist jetzt verifiziert.")

    @user.command(name="guest",brief="Benutzer als Gast freischalten.")
    @b5check("user",check="admin")
    async def userguest(self,ctx,members: Greedy[discord.Member]):
        for m in members:
            u = b5("user").get(m.id)
            if u is None:
                await ctx.send(m.display_name+" nicht gefunden.")
            else:
                await u.verify(0,force=True,accountType=Account.GUEST)
                await ctx.send(u.inGuild().display_name+" ist jetzt verifiziert.")

    @user.command(name="know",brief="Benutzer zur Datenbank hinzufügen.")
    @b5check("user",check="admin")
    async def userknow(self,ctx,members:Greedy[discord.Member]):
        for m in members:
            b5("user").add(m.id)
            await ctx.send("Ich kenne jetzt "+m.display_name+".")

    @user.command(name="forget",brief="Benutzer aus der Datenbank entfernen.")
    @b5check("user",check="admin")
    async def userforget(self,ctx,members:Greedy[discord.Member]):
        for m in members:
            b5("user").remove(m.id)
            await ctx.send("Ich habe "+m.display_name+" vergessen.")

    @user.command(name="set",brief="Ein Attribut des Benutzers setzen")
    @b5check("user",check="admin")
    async def userset(self,ctx, mem: discord.Member, attribute: str, value):
        m = b5('user').get(mem.id)
        if m is None:
            await ctx.send("Diese Person kenne ich nicht.")
        else:
            m.__set(attribute,value)
        await ctx.send("Ich habe mir den Wert notiert.")

    @user.command(name="welcome",brief="Die Willkommensnachricht (erneut) senden.")
    @b5check("user",check="admin")
    async def userwelcome(self,ctx,members:Greedy[discord.Member]):
        for m in members:
            u = b5('user').get(m.id)
            if u is None:
                await ctx.send(m.display_name+" kenne ich nicht.")
            else:
                await b5('auth').welcomeMessage(u)
                await ctx.send("Gesendet.")

class UserBase:
    # a database for our users
    def __init__(self):
        self.users = {}
        self.fields = {} # map name of field to UserField() instance

        try:
            self.users = b5('persist').load('users.bot5')
        except FileNotFoundError as e:
            print(e)
            print("Keine gespeicherten Nutzer. Bin ich neu geboren?")
            # TODO: how to log this to Discord?

        try:
            self.fields = b5('persist').load('userfields.bot5')
        except FileNotFoundError as e:
            print(e)
            print("No user field savefile found.")


    def get(self,numid):
        try:
            u = self.users[numid]
        except KeyError:
            return None
        return u

    def add(self,numid):
        u = UserClass(numid)
        self.users[numid] = u
        return u

    def remove(self,numid):
        self.users.pop(numid,None)

    def nameList(self):
        #l = [self.newusers[u].inGuild().display_name if self.newusers[u].inGuild() is not None else None for u in self.newusers]
        l = [self.users[u].inGuild().display_name if self.users[u].inGuild() is not None else None for u in self.users]
        return l

    def list(self):
        return [self.users[u] for u in self.users]

    
    # custom check for user attributes
    async def b5check(self, ctx, check="admin", role=None):
        #return True
        print("userb5check "+str(check)+" called.")
        if role is not None:
            rl = role
            if isinstance(role,str):
                rl = [role]
            for r in rl:
                if b5('user').get(ctx.author.id).isRole(r):
                    return True
            await ctx.send("Du musst eine der folgenden Rollen haben, um diesen Befehl zu verwenden:\n"+str(rl))
            return False
        if check == "admin":
            if ext('user').get(ctx.author.id).isAdmin():
                return True
            else:
                await ctx.send("Du bist nicht mein Boss!")
                await ctx.message.add_reaction('\N{ANGRY FACE}')
                return False
        if check == "verified":
            if ext('user').get(ctx.author.id).isVerified():
                return True
            else:
                await ctx.send("Dieser Befehl ist nur für verifizierte Benutzer verfügbar.")
                return False
        return False

class UserField:
    def __init__(self, extension: str, t: T, default: Type[T]):
        self.extension = extension
        self.type = t
        self.default = default

class UserClass:
# note: keep this class pickleable!
    def __init__(self,numid):
        self.values = {}
        self.values["id"] = numid


    # INTERNAL METHODS
    # do NOT call these outside of getters and setters.

    def __get(self,what):
        try:
            val = self.values[what]
        except:
            return None
        else:
            return val

    def __set(self,what,val):
        self.values[what] = val

    # GETTERS

    def inGuild(self):
        m = discord.utils.get(b5('ext').guild().members,id=self.getID())
        return m

    def getID(self):
        return self.values["id"]

    def isVerified(self):
        v = self.__get("verified")
        if v is None:
            return False
        return v

    def getAuthCode(self):
        c = self.__get("authCode")
        if c is None:
            return 0
        return c

    def authValidUntil(self):
        a = self.__get("authValidUntil")
        if a is None:
            return 0
        return a

    def getErstiVerifyAttempts(self):
        e = self.__get("erstiVerifyAttempts")
        if e is None:
            return 0
        return e

    def getRHRK(self):
        r = self.__get("rhrk")
        if r is None:
            return ''
        return r
    
    def isAdmin(self):
        return self.isRole("Admin")

    def isRole(self, role: str):
        if discord.utils.get(b5('ext').guild().roles,name=role) in self.inGuild().roles:
            return True
        else:
            return False

    def getAccountType(self):
        a = self.__get('account')
        if a is None:
            return Account.UNVERIFIED
        return a

    # SETTERS

    def setRHRK(self,rhrk):
        self.__set("rhrk",rhrk)

    def setAccountType(self,t):
        self.__set("account",t)

    def setAuthCode(self,code):
        self.__set("authCode",code)

    def setAuthValidUntil(self,til):
        self.__set("authValidUntil",til)


    # OTHER METHODS (NO SIDE EFFECTS)
    # (not counting discord output)

    # set redacted to True if the user is unverified and should not be able to use this to gain insight into the server.
    def show(self, redacted=False):
        u = self.inGuild()
        outp = []
        def line(name,value):
            outp.append(name+": "+str(value))
        line("User",u.display_name)
        line("Discord Account",u.name+'#'+u.discriminator)
        line("Discord ID",self.getID())
        line("Account type",self.getAccountType())
        line("verified", ("yes" if self.isVerified() else "no"))
        line("RHRK user",self.getRHRK())
        line("Roles",", ".join([r.name for r in u.roles[1:]]))
        redacted or line("Authentication Code",self.getAuthCode())
        line("Authentication Code valid until",time.strftime('%d. %m. %Y, %H:%M:%S (%Z)',time.localtime(self.authValidUntil())))
        return "\n".join(outp)
        #ver = "yes" if self.isVerified() else "no"
        #return "User "+str(u.display_name)+"\nDiscord ID:"+str(self.getID())+"\nverified: "+ver+"\nrhrk user: "+self.getRHRK()


    # OTHER METHODS (YES SIDE EFFECTS)

    async def verify(self, code: int, force=False, accountType=Account.TUK):
        if force or (self.getAuthCode() > 0 and code == self.getAuthCode() and time.time() < self.authValidUntil()):
            self.__set("verified", True)
            newrole = discord.utils.get(b5('ext').guild().roles,name="Studi")
            await self.inGuild().add_roles(newrole)
            self.setAccountType(accountType)
        return self.isVerified()

    async def forceVerify(self):
        return await self.verify(0,True)

    async def erstiVerify(self, wort: str):
        self.__set("erstiVerifyAttempts", self.getErstiVerifyAttempts()+1)
        match = re_ersti.match(wort)
        if match is None:
            return False
        self.__set("semester",1)
        newrole = discord.utils.get(b5('ext').guild().roles,name="Ersti")
        await self.inGuild().add_roles(newrole)
        await self.verify(0,force=True,accountType=Account.ERSTI)
        return True



    def email(self,subject,message):
        b5('email').send(self.getRHRK()+"@rhrk.uni-kl.de",subject,message)


    async def sendPM(self,msg):
        u = self.inGuild()
        await u.create_dm()
        await u.dm_channel.send(msg)

    async def notifyAboutPM(self,ctx):
        if ctx.guild is not None:
            await ctx.send("Ich habe dir eine private Nachricht geschickt.")


    def generateAuthCode(self, timeout=60*60):
        self.setAuthCode(randint(1,10000))
        self.setAuthValidUntil(time.time()+timeout)
        return self.getAuthCode()





def setup(bot):
    bot.add_cog(UserCog(bot))
    u = UserBase()
    b5('ext').register('user',u)


def teardown(bot):
    b5('persist').save('users.bot5',b5('user').users)
    b5('ext').unregister('user')
    bot.remove_cog('User')
