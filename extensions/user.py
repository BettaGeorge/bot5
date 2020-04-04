# BOT5 EXTENSION
# DEPENDS: persistence
# user.py
# extension for user management

import bot5utils
from bot5utils import *
from bot5utils import ext as b5

import time

import os

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

        if os.path.isfile(b5path+'/user.debug'):
            print("USER: DEBUG FILE FOUND")
            self.loadRawData()
        else:

            try:
                self.users = b5('persist').load('users.bot5')
            except FileNotFoundError as e:
                print(e)
                print("Keine gespeicherten Nutzer. Bin ich neu geboren?")
                # TODO: how to log this to Discord?

        self.registerField('user','id',int,0)


    def get(self,numid):
        try:
            u = self.users[numid]
        except KeyError:
            return None
        return u

    def add(self,numid):
        u = UserClass(int(numid))
        self.users[int(numid)] = u
        return u

    def remove(self,numid):
        self.users.pop(numid,None)

    def nameList(self):
        #l = [self.newusers[u].inGuild().display_name if self.newusers[u].inGuild() is not None else None for u in self.newusers]
        l = [self.users[u].inGuild().display_name if self.users[u].inGuild() is not None else None for u in self.users]
        return l

    def list(self):
        return [self.users[u] for u in self.users]

    def registerField(self, extension: str, name: str, t: T, default: Type[T]) -> None:
        if name in self.fields:
            if self.fields[name].extension == extension:
                # the extension has been loaded before, not to worry
                return
            else:
                raise Bot5Error("field "+name+" already registered by extension "+self.fields[name].extension)

        self.fields[name] = UserField(extension,t,default)

    def getField(self, user: int, name: str):
        if name not in self.fields:
            raise Bot5Error('field '+name+' is not registered')
        if not user in self.users:
            raise Bot5Error('user id '+str(user)+' not found')
        if name in self.users[user].values:
            return self.users[user].values[name]
        else:
            return self.fields[name].default

    def setField(self, user: int, name: str, value):
        if name not in self.fields:
            raise Bot5Error('field '+name+' is not registered')
        if not isinstance(value,self.fields[name].type):
            raise Bot5Error('field '
                    +name
                    +' is of type '
                    +str(self.fields[name].type)
                    +', cannot set it to a variable of type '
                    +str(type(value)))
        if not user in self.users:
            raise Bot5Error('user id '+str(user)+' not found')
        self.users[user].values[name] = value
        return value

    # set redacted to True if the user is unverified and should not be able to use this to gain insight into the server.
    def showUser(self, user: int, redacted=False) -> str:
        if user not in self.users:
            raise Bot5Error('cannot show unknown user')
        u = self.users[user].inGuild()
        outp = []
        def line(name,value):
            outp.append(name+": "+str(value))
        line("User",u.display_name)
        line("Discord Account",u.name+'#'+u.discriminator)
        line("Discord ID",user)
        line("Roles",", ".join([r.name for r in u.roles[1:]]))

        for n in self.fields:
            if self.fields[n].showToUser:
                line(n,self.getField(user,n))

        return "\n".join(outp)

    def loadRawData(self):
        with open(b5path+'/datadump.user','r') as FILE:
            lastid = 0
            for line in FILE.readlines():
                if len(line.strip())==0:
                    print("empty line in datadump")
                    continue
                vals = line.strip().split(':::')
                if vals[0] == 'id':
                    self.add(int(vals[1]))
                    lastid = int(vals[1])
                else:
                    nval = vals[1]
                    if nval == 'True':
                        nval = True
                    elif nval == 'False':
                        nval = False
                    elif nval.isdigit():
                        nval = int(nval)
                    if vals[0] in self.fields:
                        nval = self.fields[val[0]].type(nval)
                    self.users[lastid].values[vals[0]] = vals[1]




    
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
            if ext('user').getField(ctx.author.id,'verified'):
                return True
            else:
                await ctx.send("Dieser Befehl ist nur für verifizierte Benutzer verfügbar.")
                return False
        return False

class UserField:
    # set showToUser to False to exclude it from dsgvo einsicht for everyone.
    def __init__(self, extension: str, t: T, default: Type[T], showToUser: bool=True):
        self.extension = extension
        self.type = t
        self.default = default
        self.showToUser = showToUser

class UserClass:
# note: keep this class pickleable!
    def __init__(self,numid: int):
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

    # NEW GETTER AND SETTER

    def get(self,what: str):
        return b5('user').getField(self.values["id"],what)

    def set(self,what: str,val):
        return b5('user').setField(self.values['id'],what,val)

    # SPIECLIAZED GETTERS

    def inGuild(self):
        m = discord.utils.get(b5('ext').guild().members,id=self.getID())
        return m

    def getID(self):
        return self.values["id"]

    def isAdmin(self):
        return self.isRole("Admin")

    def isRole(self, role: str):
        if discord.utils.get(b5('ext').guild().roles,name=role) in self.inGuild().roles:
            return True
        else:
            return False


    # OTHER METHODS (NO SIDE EFFECTS)
    # (not counting discord output)

    # set redacted to True if the user is unverified and should not be able to use this to gain insight into the server.
    def show(self, redacted=False):
        return b5('user').showUser(self.getID(),redacted)


    # OTHER METHODS (YES SIDE EFFECTS)






    async def sendPM(self,msg):
        u = self.inGuild()
        await u.create_dm()
        await u.dm_channel.send(msg)

    async def notifyAboutPM(self,ctx):
        if ctx.guild is not None:
            await ctx.send("Ich habe dir eine private Nachricht geschickt.")







def setup(bot):
    bot.add_cog(UserCog(bot))
    u = UserBase()
    b5('ext').register('user',u)


def teardown(bot):
    b5('persist').save('users.bot5',b5('user').users)
    b5('ext').unregister('user')
    bot.remove_cog('User')
