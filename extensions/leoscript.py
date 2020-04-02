# leoscript.py
# oh God, why am I doing this even

import bot5utils
from bot5utils import *
from bot5utils import ext as b5

import pyparsing as pyp
import math
import operator
import traceback
import asyncio

import importlib
import extensions.texts.leoscript as lt
# we might need to reimport help texts
importlib.reload(lt)

import re
re_command = re.compile('^\\\\')
# stripComments: match if at least one char before a #, and the char right before # is not a backslash.
#reStripComments = re.compile('([^#]*[^#\\\\])#')

FORBIDDENCHARS = '[^\\s.:,]'# chars you cannot use in variable names

def regex(r: str):
    reg = r.replace('[VAR]',FORBIDDENCHARS)
    return re.compile(reg)

reSetVar = regex('^Nachricht( namens ([VAR]*))?( an ([VAR]*))?:?$')
reSetVarInline = regex('^Nachricht( namens ([VAR]*))?( an ([VAR]*))?: ?(.+)$')
reEndMessage = regex('^Danke\\.?$')
rePrintVar = regex('^Sende((?! an ) ([VAR]*))?( an ([VAR]*))?\\.?$')
reIf = regex('^Falls( ([^,]+))?,?$')
#reIfInline = regex('^Falls( ([VAR]+))?, ?([VAR]*)?$')
reSaveInVar = regex('^Notiere( ((?!als )[VAR]+))? als ([VAR]+)\\.?$')
reReturn = regex('^Antworte( ([^.]+))?\\.?$')
reCompute = regex('^Berechne( (((?!\\.$).)+))?\\.?$')
reInput = regex('^Frage( in (\\S+))?\\.?$')
reConcat = regex('^Ergänze( ((?!um )[VAR]+))?( um ([VAR]+))?\\.?$')

reCondEq = regex('^([VAR]+) ?= ?([VAR]+)$')
reCondLess = regex('^([VAR]+) ?< ?([VAR]+)$')

reInt = regex('^\\d+$')
reNum = regex('^\\d+(\\.\\d+)?$')

#COMPCHARS = '*^+\\-()/' # this should contain everything NumberParser could interpret as an operator.
#reWord = re.compile('([^'+COMPCHARS+']+)')

# this list should hold all constructs that can be ended by a reEndMessage.
ENDABLES = [reSetVar, reIf]

# special "to" field to execute a message
TOEXEC = 'Leo'

# how long user scripts are allowed to run (in seconds)
TIMEOUT = 10


class LeoCog(commands.Cog,name="LeoScript"):

    def __init__(self,bot):
        self.bot = bot

    @commands.group(name="leo",brief="Die Leoscript-Programmiersprache.")
    async def leoscript(self,ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Dieser Befehl ist zur Benutzung von **Leoscript** gedacht. Für generelle Hilfe verwende den Befehl `\\hilfe`.\nWenn du mehr zu **Leoscript** wissen möchtest, tippe `\\leo intro` oder `\\leo doc`.')

    @leoscript.command(name="intro",brief="Kurze Erläuterung zu **Leoscript**.")
    async def leoscriptintro(self,ctx):
        for h in lt.intro:
            await b5('user').get(ctx.author.id).sendPM(h)

        await b5('user').get(ctx.author.id).notifyAboutPM(ctx)

    @leoscript.command(name="doc",brief="Die vollständige Spezifikation von Leoscript.")
    async def leoscriptdoc(self, ctx, *args):
        helpcmd = ""
        if len(args) == 0:
            helpcmd = "0"
        else:
            helpcmd = " ".join(args)

        helptext = []
        helptext2 = None

        if helpcmd == "0":
            helptext =  lt.inhalt

        elif helpcmd == "1" or helpcmd == "grundlagen":

            helptext = lt.grundlagen
        
        elif helpcmd in ["2","aktuell"]:

                helptext = lt.aktuell
                 
        elif helpcmd in ["3","befehle", "befehle 1"]:
            helptext = lt.befehle1
        

        elif helpcmd in ["4","logik"]:
            helptext = lt.logik

        else:
            helptext = ["Ich konnte die angegebene Seite nicht finden. Gib `\\leo doc` ein, um ins Inhaltsverzeichnis zu gelangen."]

        for h in ["**__Leoscript: Dokumentation__**"]+helptext:
            await b5('user').get(ctx.author.id).sendPM(h)

        #if helptext2 is not None:
            #await b5('user').get(ctx.author.id).sendPM(helptext2)

        await b5('user').get(ctx.author.id).notifyAboutPM(ctx)

    @leoscript.command(name="beispiel",brief="Kommentierte Beispiele zum Verständnis.")
    async def leoscriptbeispiel(self, ctx, *args):
        helpcmd = ""
        if len(args) == 0:
            helpcmd = "0"
        else:
            helpcmd = " ".join(args)

        helptext = []

        if helpcmd in lt.beispiele:

            helptext = lt.beispiele[helpcmd]
        

        else:
            helptext = ["Ich konnte die angegebene Seite nicht finden. Gib `\\leo beispiel` ein, um ins Inhaltsverzeichnis zu gelangen."]

        ht = helptext.copy()
        if helpcmd != "0":
            ht = ["```"+h+"```" for h in ht]
        for h in ["**__Leoscript: Beispiele__**"]+ht:
            await b5('user').get(ctx.author.id).sendPM(h)
        helpcmd != "0" and await b5('user').get(ctx.author.id).sendPM("Nutze `\\leo vorführung "+helpcmd+"`, um den Output dieses Beispiels zu sehen.")

        await b5('user').get(ctx.author.id).notifyAboutPM(ctx)


    @leoscript.command(name="vorführung",brief="Führt den Beispielcode aus.")
    async def leoscriptvor(self, ctx, *args):
        helpcmd = ""
        if len(args) == 0:
            helpcmd = "0"
        else:
            helpcmd = " ".join(args)

        if helpcmd == "0":
            for h in lt.beispiele[helpcmd]:
                await b5("user").get(ctx.author.id).sendPM(h)
            await b5('user').get(ctx.author.id).notifyAboutPM(ctx)
            return

        if helpcmd in lt.beispiele:

            helptext = "".join(lt.beispiele[helpcmd])
            # helptext is now one long string containing a valid leoscript
            interpreter = LeoInterpreter(helptext,ctx.channel,b5("user").get(ctx.author.id))
            async with ctx.channel.typing():
                try:
                    ret = await asyncio.wait_for(interpreter.run(),timeout=TIMEOUT)
                except (asyncio.TimeoutError):
                    await b5('user').get(ctx.author.id).sendPM("Dein Leoscript wurde abgebrochen, weil das Zeitlimit von "+str(TIMEOUT)+" Sekunden überschritten wurde.")
                else:
                    await ctx.send("Ergebnis: "+str(ret)+".")
            await ctx.send("Ausführung beendet.")


        else:
            await ctx.send("Dieses Beispiel kenne ich nicht. Rufe `\\leo beispiel` auf, um eine Liste aller verfügbaren Beispiele zu sehen.")






    @leoscript.command(name="msg",brief="Führt deine nächste Nachricht als Leoscript aus.")
    async def leoscriptmsg(self,ctx):
        await ctx.send("Ich werde deine nächste Nachricht als Skript interpretieren.")
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        msg = await self.bot.wait_for('message',check=check)
        interpreter = LeoInterpreter(msg.content, ctx.channel, b5("user").get(ctx.author.id))
        async with ctx.channel.typing():
            try:
                ret = await asyncio.wait_for(interpreter.run(),timeout=TIMEOUT)
            except (asyncio.TimeoutError):
                await b5('user').get(ctx.author.id).sendPM("Dein Leoscript wurde abgebrochen, weil das Zeitlimit von "+str(TIMEOUT)+" Sekunden überschritten wurde.")
            else:
                await ctx.send("Ergebnis: "+str(ret)+".")
        await ctx.send("Ausführung beendet.")

    @commands.Cog.listener()
    async def on_message(self,message):
        if message.author == self.bot.user:
            return

        if self.bot.user in message.mentions or message.guild is None:
            if not re_command.match(message.content):
                if len(message.attachments) > 0:
                    await message.channel.send("Ich versuche dein Skript auszuführen.")
                    await message.attachments[0].save('scripts/'+str(message.author.id))
                    code = ""
                    with open('scripts/'+str(message.author.id),'r') as scr:
                        code = scr.read()
                    interpreter = LeoInterpreter(code, message.channel, b5("user").get(message.author.id))
                    try:
                        ret = await asyncio.wait_for(interpreter.run(),timeout=TIMEOUT)
                    except (asyncio.TimeoutError):
                        await b5('user').get(message.author.id).sendPM("Dein Leoscript wurde abgebrochen, weil das Zeitlimit von "+str(TIMEOUT)+" Sekunden überschritten wurde.")
                    else:
                        await message.channel.send("Ergebnis: "+str(ret)+".")
                    await message.channel.send("Ausführung beendet.")



#class LeoScript:
#    # the main instance registered with b5('ext').
#    def __init__(self):
#        pass


class LeoInterpreter:
    # spawn one of these for each script being interpreted
    # script is the linebreak-separated script.
    # ctx is a Discord channel. None is NOT valid.
    # user is the invoking user, that is, a b5('user').UserClass object.
    # var is the variable scope of the invoking LeoInterpreter, if any.
    # scope is the name of the current scope. May be None to indicate toplevel instance.
    def __init__(self, script: str, ctx, user, var={}, scope=None):
        self.ctx = ctx
        self.user = user
        self.current = LeoMessage("",None,None) # the currently active variable
        self.var = var # dict of all variables
        self.skip = [] # lines to skip (e.g. because they contain an end statement we have already parsed)
        self.scope = scope # the name of this scope
        self.currentLine = 0 # always holds the line currently being interpreted
        self.script = self.preprocess(script)
        print("LEOSCRIPT INITIALIZED WITH "+str(len(self.script))+" LINES")

    def preprocess(self,script: str):
        scriptLines = script.splitlines()
        cleanLines = []

        if self.scope is not None:
            # we are in a method call; do not process for comments again
            for i in range(0,len(scriptLines)):
                cleanLines.append(LeoLine(self.stripWhitespace(scriptLines[i]),i))
            return cleanLines

        # first, strip comments.
        for i in range(0,len(scriptLines)):
            line = scriptLines[i]
            clean = ""
            #m = reStripComments.match(line)

            # if the line contains a comment, extract non-comment part:
            #if m is not None:
            #    if m.group(1) is not None:
            #        clean = self.stripWhitespace(m.group(1))

            # if not, check whether the entire line is a comment.
            #else:
            #    if len(line) > 0 and line[0] != '#':
            #        clean = self.stripWhitespace(line)
            skipnext = False
            for j in range(0,len(line)):
                if skipnext:
                    skipnext = False
                    continue
                if line[j] == '#':
                    if j >= len(line)-1 or line[j+1] != '#':
                        break
                    else:
                        skipnext = True
                clean = clean+line[j]

            clean = self.stripWhitespace(clean)

            if len(clean) > 0:
                cleanLines.append(LeoLine(clean,i))
        return cleanLines

    def stripWhitespace(self,line: str):
        return line.strip()

    async def run(self):
        try:
            r = await self.interpretRecursive(0,len(self.script)-1)
        except LeoError as e:
            await self.ctx.send("FEHLER: Ich komme nicht mit deinen Anweisungen klar.\n"+str(e.message))
            return e
        except asyncio.CancelledError as e: # this implies we hit a timeout
            return e
        except Exception as e:
            trace = traceback.format_exc()
            trace = trace[0:1000] # cut down to a size we can send via discord
            await self.ctx.send("FEHLER im Python-Code. Die Ausführung endete in Scope "+str(self.scope)+" in Zeile "+str(self.script[self.currentLine].line)+"\n"+str(trace))
            return e
        else:
            return r

    # pos is the current position in the code, i.e. the line where the statement is opened.
    # this returns the line on which the statement is closed, or raises an Exception if it is never closed.
    def findEndStatement(self, pos: int):
        j = pos+1
        skip = 0 # counts the EndMessages to skip because of additional blocks encountered
        while True:
            if j not in self.skip:
                if j > len(self.script)-1:
                    raise LeoError(self,'Diese mehrzeilige Nachricht endet nie.')
                line = self.script[j].code
                if reEndMessage.match(line):
                    if skip <= 0:
                        break
                    else:
                        skip -= 1
                else:
                    for r in ENDABLES:
                        if r.match(line):
                            skip += 1
                            break
            j += 1

        # we have found the appropriate end statement. It should not be found by further blocks.
        self.skip.append(j)
        print("LEOSCRIPT END: "+str(j))
        return j

    # takes a starting and ending line, BOTH INCLUSIVE
    async def interpretRecursive(self, startln: int, endln: int):

        i = startln
        while i < endln+1:
            print("LEOSCRIPT LINE "+str(i))
            print("LEOSCRIPT skip = "+str(self.skip))
            line = self.script[i].code
            self.currentLine = i

            #mEndMessage = reEndMessage.match(line)
            m = reSetVar.match(line)
            mSetVarInline = reSetVarInline.match(line)
            m2 = rePrintVar.match(line)
            mIf = reIf.match(line)
            mSaveInVar = reSaveInVar.match(line)
            mReturn = reReturn.match(line)
            mCompute = reCompute.match(line)
            mInput = reInput.match(line)
            mConcat = reConcat.match(line)

            if i in self.skip:
                # simply ignore lines marked for skipping
                pass

            elif mCompute:
                computation = mCompute.group(1)
                if computation is None or computation == "":
                    computation = self.current.message
                print("LEOSCRIPT: sending '"+computation+"' to ParseComputation")
                self.current = LeoMessage(self.parseComputation(computation),None,None)
                

            elif mSetVarInline:
                varName = mSetVarInline.group(2)
                varTo = mSetVarInline.group(4)
                varVal = mSetVarInline.group(5)
                self.setVar(varVal,varName,varTo)

            elif m:
                varName = m.group(2)
                varTo = m.group(4)
                #varVal = m.group(5)

                # are name and to valid?
                # actually, nevermind. I'm fine with either of them being empty.

                # if no value was provided, then this must be a multiline message.
                # search for the ending line, then put all the lines inbetween into the variable.
                #if varVal is None or len(varVal) == 0:
                j = self.findEndStatement(i)
                varVal = "\n".join([ln.code for ln in self.script[i+1:j]])

                # we found the value. Let's save it.
                self.setVar(varVal,varName,varTo)

                i = j

            elif m2: #m2 := rePrintVar.match(line):
                varName = m2.group(2)
                varTo = m2.group(4)

                if varName is None or varName == "":
                    v = self.current
                else:
                    try:
                        v = self.var[varName]
                    except KeyError:
                        raise LeoError(self,varName+' ist nicht definiert.')

                # if the user did not override the saved recipient, use that:
                if varTo is None or varTo == "":
                    varTo = v.to

                # if there is still no recipient, send to context.
                if varTo is None or varTo == "":
                    await self.ctx.send(v.message)
                elif varTo == TOEXEC:
                    newscope = str(v.name)
                    if newscope is None or newscope == "":
                        newscope = '#aktuelle Nachricht#'
                    interpreter = LeoInterpreter(v.message,self.ctx,self.user,self.var,str(v.name))
                    ret = await interpreter.run()
                    self.current = LeoMessage(ret,None,None)
                else:
                    c = discord.utils.get(bot5utils.GUILD.channels,name=varTo)
                    if c is None:
                        raise LeoError(self,'Ich kenne keinen Channel '+varTo+'.')
                    perm = c.permissions_for(self.user.inGuild())
                    if perm.send_messages:
                        await c.send(v.message)
                    else:
                        raise LeoError(self,'Du hast keine Berechtigung, im Channel '+varTo+' zu posten.')

            elif mIf:
                condition = mIf.group(2)
                print("LEOSCRIPT if "+condition)

                j = self.findEndStatement(i)
                if self.checkConditional(condition):
                    print("condition was true")
                    pass # the condition holds, so simply execute the next line
                else:
                    print("condition was false")
                    i = j # skip to the end of the if block
                    
                    
            # TODO: actually implement inline-if

            elif mSaveInVar:
                toSave = mSaveInVar.group(2)
                varName = mSaveInVar.group(3)

                if toSave is None or toSave == "":
                    toSave = self.current
                else:
                    try:
                        toSave = self.var[toSave]
                    except KeyError:
                        raise LeoError(self,"Ich kann die Nachricht namens "+toSave+" nicht speichern, weil ich sie nicht kenne.")

                self.var[varName] = LeoMessage(toSave.message,varName,toSave.to)

            elif mReturn:
                ret = mReturn.group(2)
                if ret is None or ret == "":
                    return self.current.message
                else:
                    return ret

            elif mInput:
                targetChannel = mInput.group(2)
                if targetChannel is None or targetChannel == "":
                    targetChannel = self.ctx
                else:
                    try:
                        targetChannel = discord.utils.get(bot5utils.GUILD.channels,name=targetChannel)
                    except:
                        raise LeoError(self,"Ich kann den Channel "+str(mInput.group(2))+" nicht finden.")

                # targetChannel should now be a discord.Channel.

                perm = targetChannel.permissions_for(self.user.inGuild())
                if not perm.read_messages:
                    raise LeoError(self,'Du hast keine Berechtigung auf den Channel '+targetChannel.name+' zuzugreifen-')

                def check(m):
                    return m.channel == targetChannel
                ret = await b5("ext").bot.wait_for('message',check=check)
                self.current = LeoMessage(ret.content,None,None)

            elif mConcat:
                targetName = mConcat.group(2)
                toAppendName = mConcat.group(4)
                target = None
                toAppend = None

                if targetName is None or targetName == "":
                    target = self.current
                else:
                    try:
                        target = self.var[targetName]
                    except KeyError:
                        raise LeoError(self,"Ich kenne keine Nachricht namens "+targetName+".")

                if toAppendName is None or toAppendName == "":
                    toAppend = self.current
                else:
                    try:
                        toAppend = self.var[toAppendName]
                    except KeyError:
                        raise LeoError(self,"Ich kenne keine Nachricht namens "+toAppendName+".")

                target.append(toAppend)

                

            else:
                raise LeoError(self,"Diesen Befehl verstehe ich nicht.")

            i += 1
        return self.current.message

    def parseComputation(self,computation: str):
        comp = computation
        # replace every occurrence of a variable name by its value
        #matches = reWord.findall(comp)
        #for m in matches:
        #    if m in self.var:
        #        r = re.compile('(?<=^|['+COMPCHARS+'])'+m+'(?=$|['+COMPCHARS+'])')
        #        comp = r.sub(self.var[m].message)
        print("LEOSCRIPT vars: "+str(self.var.keys()))
        for var in sorted(self.var.keys(), key=len, reverse=True):
            print(var+" contains "+self.var[var].message)
            comp = comp.replace(var, self.var[var].message)
        nsp = NumericStringParser()
        print("LEOSCRIPT NumericStringParser: "+comp)
        return nsp.eval(comp)


    def checkConditional(self, cond: str):
        mEq = reCondEq.match(cond)
        mLess = reCondLess.match(cond)
        if mEq:
            leftEx = mEq.group(1)
            rightEx = mEq.group(2)

            # if a bareword matches a variable name, it is interpreted as that variable. We're wacky like that.
            if leftEx in self.var:
                leftEx = self.var[leftEx].message
            if rightEx in self.var:
                rightEx = self.var[rightEx].message

            if leftEx == rightEx:
                return True
            else:
                return False
        elif mLess:
            leftEx = mLess.group(1)
            rightEx = mLess.group(2)

            # if a bareword matches a variable name, it is interpreted as that variable. We're wacky like that.
            if leftEx in self.var:
                leftEx = self.var[leftEx].message
            if rightEx in self.var:
                rightEx = self.var[rightEx].message

            print("LEOSCRIPT leftEx: "+str(leftEx))
            print("LEOSCRIPT rightEx: "+str(rightEx))


            if reNum.match(leftEx) and reNum.match(rightEx):
                return float(leftEx) < float(rightEx)
            else:
                return len(leftEx) < len(rightEx)

        else:
            raise LeoError(self,"Die Bedingung '"+cond+"' verstehe ich nicht.")

    def setVar(self, val: str, name: str, to: str):
        v = LeoMessage(val,name,to)
        self.current = v
        if name is not None and len(name) > 0:
            self.var[name] = v
        print(self.current.message)

class LeoLine:
    # a script line.
    def __init__(self, code: str, linenumber: int):
        self.code = code
        self.line = linenumber


class LeoMessage:
    # these are the variable objects of LeoScript.

    def __init__(self, msg, name: str, to: str):
        self.message = str(msg) # we force convert to string -- someone might want to write a number in here after a computation.
        self.name = name
        self.to = to

    def append(self, msg: 'LeoMessage'):
        self.message = self.message+msg.message


class NumericStringParser(object):
    '''
    Most of this code comes from the fourFn.py pyparsing example
    http://pyparsing.wikispaces.com/file/view/fourFn.py
    http://pyparsing.wikispaces.com/message/view/home/15549426
    __author__='Paul McGuire'
    '''
    def pushFirst(self, strg, loc, toks ):
        self.exprStack.append( toks[0] )
    def pushUMinus(self, strg, loc, toks ):
        if toks and toks[0] == '-':
            self.exprStack.append( 'unary -' )
    def __init__(self):
        """
        expop   :: '^'
        multop  :: '*' | '/'
        addop   :: '+' | '-'
        integer :: ['+' | '-'] '0'..'9'+
        atom    :: PI | E | real | fn '(' expr ')' | '(' expr ')'
        factor  :: atom [ expop factor ]*
        term    :: factor [ multop factor ]*
        expr    :: term [ addop term ]*
        """
        point = pyp.Literal( "." )
        e     = pyp.CaselessLiteral( "E" )
        fnumber = pyp.Combine( pyp.Word( "+-"+pyp.nums, pyp.nums ) +
                           pyp.Optional( point + pyp.Optional( pyp.Word( pyp.nums ) ) ) +
                           pyp.Optional( e + pyp.Word( "+-"+pyp.nums, pyp.nums ) ) )
        ident = pyp.Word(pyp.alphas, pyp.alphas+pyp.nums+"_$")
        plus  = pyp.Literal( "+" )
        minus = pyp.Literal( "-" )
        mult  = pyp.Literal( "*" )
        div   = pyp.Literal( "/" )
        lpar  = pyp.Literal( "(" ).suppress()
        rpar  = pyp.Literal( ")" ).suppress()
        addop  = plus | minus
        multop = mult | div
        expop = pyp.Literal( "^" )
        pi    = pyp.CaselessLiteral( "PI" )
        expr = pyp.Forward()
        atom = ((pyp.Optional(pyp.oneOf("- +")) +
                 (pi|e|fnumber|ident+lpar+expr+rpar).setParseAction(self.pushFirst))
                | pyp.Optional(pyp.oneOf("- +")) + pyp.Group(lpar+expr+rpar)
                ).setParseAction(self.pushUMinus)
        # by defining exponentiation as "atom [ ^ factor ]..." instead of
        # "atom [ ^ atom ]...", we get right-to-left exponents, instead of left-to-right
        # that is, 2^3^2 = 2^(3^2), not (2^3)^2.
        factor = pyp.Forward()
        factor << atom + pyp.ZeroOrMore( ( expop + factor ).setParseAction(
            self.pushFirst ) )
        term = factor + pyp.ZeroOrMore( ( multop + factor ).setParseAction(
            self.pushFirst ) )
        expr << term + pyp.ZeroOrMore( ( addop + term ).setParseAction( self.pushFirst ) )
        self.bnf = expr
        # map operator symbols to corresponding arithmetic operations
        epsilon = 1e-12
        self.opn = { "+" : operator.add,
                "-" : operator.sub,
                "*" : operator.mul,
                "/" : operator.truediv,
                "^" : operator.pow }
        self.fn  = { "sin" : math.sin,
                "cos" : math.cos,
                "tan" : math.tan,
                "abs" : abs,
                "trunc" : lambda a: int(a),
                "round" : round,
                # For Python3 compatibility, cmp replaced by ((a > 0) - (a < 0)). See
                # https://docs.python.org/3.0/whatsnew/3.0.html#ordering-comparisons
                "sgn" : lambda a: abs(a)>epsilon and ((a > 0) - (a < 0)) or 0}
        self.exprStack = []

    def evaluateStack(self, s ):
        op = s.pop()
        if op == 'unary -':
            return -self.evaluateStack( s )
        if op in "+-*/^":
            op2 = self.evaluateStack( s )
            op1 = self.evaluateStack( s )
            return self.opn[op]( op1, op2 )
        elif op == "PI":
            return math.pi # 3.1415926535
        elif op == "E":
            return math.e  # 2.718281828
        elif op in self.fn:
            return self.fn[op]( self.evaluateStack( s ) )
        elif op[0].isalpha():
            return 0
        else:
            return float( op )

    def eval(self, num_string, parseAll = True):
        self.exprStack = []
        results = self.bnf.parseString(num_string, parseAll)
        val = self.evaluateStack( self.exprStack[:] )
        return val

#nsp = NumericStringParser()
#print(nsp.eval('1+2'))


class LeoError(Exception):
    def __init__(self, instance: LeoInterpreter, msg: str):
        self.message = 'Zeile '+str(instance.script[instance.currentLine].line)+' in Scope '+str(instance.scope)+': '+msg+"\n in \""+str(instance.script[instance.currentLine].code+"\"")





def setup(bot):
    bot.add_cog(LeoCog(bot))
    #u = LeoScript()
    #b5('ext').register('leo',u)


def teardown(bot):
    #b5('ext').unregister('leo')
    bot.remove_cog('LeoScript')
