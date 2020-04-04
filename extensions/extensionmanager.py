# extensionmanager.py
# VERY SPECIAL EXTENSION!
# this extension is loaded on startup and should load all other extensions if the ExtensionManager.setup() routine is called.
# it also manages all the variables from extensions which should be available everywhere. This is implemented as follows:
# any extension can register with the Manager by calling bot5utils.ext('ext').register with the desired identifier and an object reference.
# The Manager then makes that object globally available via the bot5utils.ext(identifier) function for interextension information exchange.
# Interextension information exchange. Say that three times fast.
#
# extensionmanager tries to load the extensions listed in the config file.
# as extensions may have startup dependencies, we need a way to specify those.
# Any bot5 extension other than this one and logging has to contain as its first line a comment of the following form:
# BOT5 EXTENSION
# The second line may optionally be a comment formatted like:
# DEPENDS: a,b,c
# The dependencies are given as a comma-separated list of extension names, without .py.

from bot5utils import *
import bot5utils
from bot5utils import ext as b5

import traceback

FIRSTLINE = '# BOT5 EXTENSION'
DEPENDS = '# DEPENDS: '

## the list of extensions to load on startup
#extlist = [
#        "persistence",
#        "user",
#        "admin",
#        "authentication",
#        "misc",
#        "email",
#        "whiteboard",
#        "dsgvo",
#        "leoscript",
#        "komraum",
#        ]

class ExtensionError(Bot5Error):
    pass

class CircularDependencyError(ExtensionError):
    pass

class ExtensionNotLoadedError(ExtensionError):
    def __init__(self):
        self.message='Tried to unload an unloaded extension'

class ExtensionManager(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

        # this holds references to everything we have registered. it is globally accessible through the get() method, which in turn is globally accessible as bot5utils.ext().
        self.vars = {}
        self.verifyCheck = None
        self.commandWhitelist = [] # a list of commands, by cog and name, that can be executed by unverified users. Do not access directly; use whitelistCommand and unwhitelistCommand.

        self.extensions = [] # a list of loaded extensions, mainly for dependency checking
        # most importantly, extensions are stored in self.extensions in the order in which they were loaded, so at runtime we can safely assume any dependency is in the list BEFORE the extension that depends on it.
        # This means that we can safely unload in reverse order.
        self.neededBy = {} # dict a=>[b], where [b] are the extensions depending on a. We use this to not accidentally unload a dependency
        self.dependsOn = {} # and this is the other direction


    # call this once when the bot starts. Extensions you add later should be loaded manually instead.
    async def setup(self):
        print("EXTENSION MANAGER: setup. trying to set up logging.")
        # we always load the logging extension. if we are unable to log, give up.
        try:
            self.bot.load_extension("extensions.logging")
        except Exception as e:
            print(e)
            print("EXTENSION MANAGER: unable to set up logging, so shutting down")
            await self.bot.logout()

        # we should have logging now
        print("Bot5 online. Further messages shall be delivered through Discord.")
        await b5('log').log("Hallo! Ich bin jetzt wach. Lass mich noch meine Sachen zusammensuchen ...")

        # see whether the user wants startup extensions
        if 'extensions' in b5config.sections():
            for extension in b5config['extensions']:
                if extension not in self.extensions:
                    self.loadExtension(extension)
                    await b5('log').log("Loaded extension "+extension+".")

        # add a global check for verified users:
        #self.bot.add_check(b5check('user',check='verified'))
        async def _b5check(ctx):
            cogname = None if ctx.command.cog is None else ctx.command.cog.qualified_name
            if (cogname,ctx.command.qualified_name) in self.commandWhitelist:
                return True
            try:
                return await b5('user').b5check(ctx,check='verified')
            except Exception as e:
                trace = traceback.format_exc()
                print("EXTENSION MANAGER: B5CHECK: exception")
                print(str(e))
                print(str(trace))
                return False
        self.verifyCheck = _b5check
        self.bot.add_check(_b5check)

    async def teardown(self):
        print("EXTENSION MANAGER: shutting down")
        self.verifyCheck is not None and self.bot.remove_check(self.verifyCheck)
        for extension in reversed(self.extensions):
            if extension in self.extensions:
                unloaded = self.unloadExtension(extension)
                await b5('log').log("Unloaded extensions: "+str(unloaded))
        self.bot.unload_extension("extensions.logging")
        print("EXTENSION MANAGER: all extensions removed.")

    def registerSelf(self):
        self.register('ext',self)

    def unregisterSelf(self):
        self.unregister('ext')

    # your extension should call this on setup with the (unique) identifier and a reference to the object you want to share
    def register(self,identifier: str, ref):
        self.vars[identifier] = ref

    def unregister(self,identifier: str):
        self.vars.pop(identifier,None)

    def whitelistCommand(self,cog: str, cmd: str):
        self.commandWhitelist.append((cog,cmd))

    def unwhitelistCommand(self, cog: str, cmd: str):
        try:
            self.commandWhitelist.remove((cog,cmd))
        except ValueError as e:
            print("EXTENSION MANAGER: tried to unwhitelist '"+name+"', but was not whitelisted in the first place")

    def get(self,identifier):
        return self.vars[identifier]

    # tries to (re)load an extension. Returns a string that should be logged in an appropriate place (since it doesn't know the context in which it was called!)
    # depending on where you called this, either log the string in something like ctx.send(), or simply print() it to stdout or a file.
    # "pending" is a list of extensions that are not allowed as dependencies right now so as to not allow circular dependencies.
    # the actual loading is only done once we have made sure that all dependencies exist so we can roll back to before in case of an error.
    # Sadly, this means we have to create a temporary copy of neededBy and dependsOn and hand it up through the recursion.
    # Thus, this returns a tuple (a,b,c), where a is a list of extensions to actually load, b is the new version of neededBy if the loading succeeds, and c is the new dependsOn.
    def loadExtension(
            self,
            extension: str,
            pending: Optional[Tuple[
                List[str],
                Dict[str,List[str]],
                Dict[str,List[str]]]] = None
            ) -> Optional[Tuple[
                List[str],
                Dict[str,List[str]],
                Dict[str,List[str]]]]:

        # first, see whether this extension exists and is a proper bot5 extension.
        with open("extensions/"+extension+".py","r") as FILE:
            if FILE.readline().strip() != FIRSTLINE:
                raise ExtensionError('first line of '+extension+' was not '+FIRSTLINE+'; is this really a bot5 extension?')
            secondLine = FILE.readline().strip()

        if pending is None:
            tmpNeededBy = self.neededBy.copy()
            tmpDependsOn = self.dependsOn.copy()
            pendingExtensions = []
        else:
            tmpNeededBy = pending[1]
            tmpDependsOn = pending[2]
            pendingExtensions = pending[0]

        # are there dependencies?
        depends = []
        if secondLine[0:len(DEPENDS)] == DEPENDS:
            depends = [l.strip() for l in secondLine[len(DEPENDS):].split(',')]

        tmpDependsOn[extension] = depends
        for d in depends:
            if not d in tmpNeededBy:
                tmpNeededBy[d] = []
            tmpNeededBy[d].append(extension)

        toLoad = []
        for d in depends:
            if d in self.extensions:
                continue # dependency already loaded: great!
            if d in pendingExtensions:
                raise CircularDependencyError(d+' depends on '+extension+', which in turn depends on '+d+'. Do you see the problem here?')
            ret = self.loadExtension(d,(pendingExtensions+[extension],tmpNeededBy,tmpDependsOn))
            for t in ret[0]:
                t in toLoad or toLoad.append(t)
            tmpNeededBy = ret[1]
            tmpDependsOn = ret[2]


        # if we have passed that loop without encountering an exception, we must have managed to find all dependencies.
        toLoad.append(extension)
        # toLoad now contains a list of extensions we should actually load, in order.
        # We only want to load every extension once, so we only do this if we are the toplevel loadExtension call (pending is None).
        # Otherwise, just hand toLoad up to the next call.

        if pending is not None:
            return (toLoad,tmpNeededBy,tmpDependsOn)

        else:
            for i in range(0,len(toLoad)):
                try:
                    self.bot.load_extension("extensions."+toLoad[i])
                except Exception as e:
                    # we might have already loaded stuff. Cleanly undo what we have done so far before raising the exception.
                    for j in reversed(range(0,i)):
                        self.bot.unload_extension("extensions."+toLoad[j])
                    raise e
            # we have passed the loading loop, so we must have loaded everything. Success.
            self.extensions = self.extensions + toLoad
            self.dependsOn = tmpDependsOn
            self.neededBy = tmpNeededBy
            if not extension in self.dependsOn:
                self.dependsOn[extension] = []
            if not extension in self.neededBy:
                self.neededBy[extension] = []
            return None

    # if recursive is set to True, also unload everything that depends on this.
    # returns a list of all unloaded extensions.
    def unloadExtension(self, extension: str, recursive = False) -> List[str]:
        if not extension in self.extensions:
            raise ExtensionNotLoadedError
        if not recursive and self.neededBy[extension] != []:
            raise ExtensionError('cannot unload '+extension+' because it is needed by '+str(self.neededBy[extension]))

        unloaded = []
        if recursive:
            for ext in self.neededBy[extension]:
                unloaded = unloaded + self.unloadExtension(ext,recursive=True)
        self.bot.unload_extension("extensions."+extension)
        unloaded.append(extension)

        self.neededBy.pop(extension)
        self.dependsOn.pop(extension)
        for extlist in self.neededBy.values():
            if extension in extlist:
                extlist.remove(extension)
        self.extensions.remove(extension)

        return unloaded

    # reloadExtension is implemented by unloading, then reloading.
    # To preserve dependency structure and not leave you with a volatile state, this also reloads ALL extensions that depend on the current one. This impacts performance, but is ultimately safest.
    # (Also, it was really easy to implement that way.)
    def reloadExtension(self,extension):
        unloaded = self.unloadExtension(extension,recursive=True)

        for ext in reversed(unloaded):
            self.loadExtension(ext)

    def guild(self):
        return  discord.utils.get(self.bot.guilds,name=bot5utils.GUILDNAME)



def setup(bot):
    bot.add_cog(ExtensionManager(bot))

    # this sets up the magic that makes the ExtensionManager.get() function globally available:
    bot5utils.extensionVariables = bot.get_cog('ExtensionManager')

    # and register the Manager with itself:
    bot.get_cog('ExtensionManager').registerSelf()

def teardown(bot):
    # unset the global access to ExtensionManager so bot5utils.py can properly handle future calls with an exception:
    bot5utils.extensionVariables = None

    # and remove ourselves from the bot
    bot.remove_cog("ExtensionManager")
