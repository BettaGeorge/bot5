# extensionmanager.py
# VERY SPECIAL EXTENSION!
# this extension is loaded on startup and should load all other extensions if the ExtensionManager.setup() routine is called.
# it also manages all the variables from extensions which should be available everywhere. This is implemented as follows:
# any extension can register with the Manager by calling bot5utils.ext('ext').register with the desired identifier and an object reference.
# The Manager then makes that object globally available via the bot5utils.ext(identifier) function for interextension information exchange.
# Interextension information exchange. Say that three times fast.

from bot5utils import *
import bot5utils
from bot5utils import ext as b5


# the list of extensions to load on startup
extlist = [
        "persistence",
        "user",
        "admin",
        "authentication",
        "misc",
        "email",
        "whiteboard",
        "dsgvo",
        "leoscript",
        "komraum",
        ]

class ExtensionManager(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

        # this holds references to everything we have registered. it is globally accessible through the get() method, which in turn is globally accessible as bot5utils.ext().
        self.vars = {}
        self.verifyCheck = None
        self.commandWhitelist = [] # a list of commands, by cog and name, that can be executed by unverified users. Do not access directly; use whitelistCommand and unwhitelistCommand.

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

        # load everything we should load at startup
        for extension in extlist:
            msg = self.loadExtension(extension)
            await b5('log').log(msg)

        # add a global check for verified users:
        #self.bot.add_check(b5check('user',check='verified'))
        async def _b5check(ctx):
            cogname = None if ctx.command.cog is None else ctx.command.cog.qualified_name
            if (cogname,ctx.command.qualified_name) in self.commandWhitelist:
                return True
            try:
                return await b5('user').b5check(ctx,check='verified')
            except Exception as e:
                print("EXTENSION MANAGER: B5CHECK: exception")
                print(str(e))
                return False
        self.verifyCheck = _b5check
        self.bot.add_check(_b5check)

    async def teardown(self):
        print("EXTENSION MANAGER: shutting down")
        self.verifyCheck is not None and self.bot.remove_check(self.verifyCheck)
        for extension in reversed(extlist):
            msg = self.unloadExtension(extension)
            await b5('log').log(msg)
        print(self.unloadExtension("logging"))
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

    def test(self):
        print("ExtensionManager TEST!!!!!!!!")

    def get(self,identifier):
        return self.vars[identifier]

    # tries to (re)load an extension. Returns a string that should be logged in an appropriate place (since it doesn't know the context in which it was called!)
    # depending where you called this, either log the string in something like ctx.send(), or simply print() it to stdout or a file.
    def loadExtension(self,extension):
        try:
            self.bot.load_extension("extensions."+extension)
        except Exception as e:
            return "LOAD_EXTENSION "+extension+": Exception encountered\n"+str(e)
        else:
            return "LOAD_EXTENSION "+extension+": Success"

    def reloadExtension(self,extension):
        try:
            self.bot.reload_extension("extensions."+extension)
        except Exception as e:
            return "RELOAD_EXTENSION "+extension+": Exception encountered\n"+str(e)
        else:
            return "RELOAD_EXTENSION "+extension+": Success"

    def unloadExtension(self, extension):
        try:
            self.bot.unload_extension("extensions."+extension)
        except Exception as e:
            return "UNLOAD_EXTENSION "+extension+": Exception encountered\n"+str(e)
        else:
            return "UNLOAD_EXTENSION "+extension+": Done."


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
