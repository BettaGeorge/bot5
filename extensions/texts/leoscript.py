# leoscript_texts.py
# contains the (very long) help texts.

intro = ["""
Introducing: **Leoscript**!

Fehlt dir ein Feature, das ich haben sollte? Brauchst du einen Taschenrechner? Oder wolltest du vielleicht schon immer ein textbasiertes Choose-Your-Own-Adventure programmieren, ohne das Discord-Fenster zu verlassen?

Auf dem fünften Stock kannst du all das und mehr, mit **Leoscript**\N{TRADE MARK SIGN}!

**Leoscript** ist eine nachrichtenbasierte Skriptsprache. Du kannst ein Programm in **Leoscript** schreiben und es an mich schicken, damit ich es ausführe. Dazu schreibst du das Programm entweder in eine Textdatei und schickst diese via Discord an mich (Privatchat, oder mention @Leo und eine beliebige nichtleere Nachricht), oder du verwendest den Befehl `\\leo msg`, um das Skript direkt in eine Nachricht zu schreiben.


**Aktuelle Features:**

* Floating Point-Berechnungen, inklusive \N{GREEK SMALL LETTER PI} und e

* Nachrichten an beliebige Channels schicken

* Input von anderen Nutzern abfragen

* Variablen speichern

* Funktionen definieren

* Turing-vollständige Sprache


**Coming Soon (probably, wenn Adrian weiterhin langweilig ist ...):**

* Angenehmere Syntax

* Praktischere Logik-Konstrukte

* Event Handling (reagieren, wenn etwas auf dem Server passiert)


Beachte, dass die Rechenzeit, die ein Skript beanspruchen darf, begrenzt ist. Wenn du mit einer Endlosschleife den Server blockierst, wird die Ausführung nach einigen Sekunden abgebrochen. Falls du ein cooles Projekt hast, das mehr Rechenzeit benötigt, kannst du von einem Administrator zusätzliche Rechenzeit erbitten.

Die vollständige Spezifikation von **Leoscript** findest du unter `\\leo doc`.
        """]

inhalt = ["""
**Inhaltsverzeichnis**

`\\leo doc 1` oder `\\leo doc grundlagen`: Einführung in die Konzepte.

`\\leo doc 2` oder `\\leo doc aktuell`: Wie funktioniert die "aktuelle Nachricht"?

`\\leo doc 3` oder `\\leo doc befehle`: Auflistung aller eingebauten Funktionen.

`\\leo doc 4` oder `\\leo doc logik`: Logische Ausdrücke, die in Abfragen verwendet werden können.

`\\leo beispiel`: Sammlung von Beispielen zum besseren Verständnis.
"""]

grundlagen = ["""
Diese Dokumentation enthält die vollständige Spezifikation für Leoscript. Eine Kurzeinführung findest du unter `\\leo intro`. Um dir den Einstieg zu erleichtern, gibt es außerdem eine Sammlung von Beispielprogrammen unter `\\leo beispiel`.

Ein Leoscript besteht aus einer oder mehreren Zeilen mit Anweisungen; eine Anweisung pro Zeile. Einrückungen sind optional.

Zusätzlicher Whitespace (Leerzeichen, leere Zeilen, ...) ist erlaubt und wird ignoriert.

Das wichtigste Konzept von Leoscript sind *Nachrichten*. Alles, was in den meisten Programmiersprachen eine *Variable* oder eine *Funktion*/*Methode* wäre, ist in Leoscript eine Nachricht.

Nachrichten besitzen eine\\*n _Empfänger\\*in_, einen _Betreff_ und ihren _Inhalt_. Alle drei dieser Angaben sind optional (siehe weiter unten).

Um eine Variable zu speichern, verfasst du einfach eine Nachricht mit dem passenden Inhalt. Du kannst auf Nachrichten über ihren Betreff zugreifen, sodass der Betreff als Variablenname fungiert.

Du kannst Nachrichten verschicken. Dann wird ihr Inhalt im Chat gepostet. Das ist das, was in anderen Sprachen eine _print_-Methode oder Ähnliches wäre.

Wenn du eine Nachricht nicht in den Chat schickst, sondern an Leo selbst, wird die Nachricht nirgends gepostet, sondern Leo wertet den Inhalt der Nachricht als Leoscript aus. So emulierst du, was in einer anderen Sprache eine Funktion oder Methode wäre.

Zur Verdeutlichung drei kurze Beispiele, jeweils zuerst in Python und dann in Leoscript.

Variable definieren:
```python
grothendieck = 57
```
```
Nachricht namens grothendieck: 57
```

Variable ausgeben:
```python
print(str(grothendieck))
```
```
Sende grothendieck
```

Funktionsaufruf:
```python
def increment(number):
    return number + 1
increment(5)
```""",
"""```
Nachricht namens increment: Berechne number + 1
Nachricht namens number: 5
Sende increment an Leo
```


**Kommentare**

Alles ab dem Zeichen # ist ein Kommentar und wird von Leoscript ignoriert. Möchtest du ein tatsächliches # in einem Text oder Variablennamen (ja, das geht) verwenden, so musst du dazu ein doppeltes ## tippen.
"""]

aktuell = ["""
**Die aktuelle Nachricht**

Leo merkt sich zu jedem Zeitpunkt die "aktuelle Nachricht". Wann immer du eigentlich den Namen (Betreff) einer Nachricht angeben müsstest, das aber nicht tust, verwendet Leo stattdessen die aktuelle Nachricht.

Wann immer du eine Nachricht verfasst, wird diese zur aktuellen Nachricht.

Außerdem wird jeder Rückgabewert eines Funktionsaufrufs automatisch in der aktuellen Nachricht gespeichert.

Ein Beispiel, wie du dieses Feature verwenden kannst: Die beiden folgenden Programme sind äquivalent.

```
Nachricht namens bla: Hallo du!
Sende bla

Nachricht namens Funktion:
    Nachricht namens out: Die Funktion wurde aufgerufen.
    Sende out
    Antworte Dies ist der Rückgabewert.
Danke

Sende Funktion an Leo.
Notiere als Rückgabe
Sende Rückgabe
```
```
Nachricht: Hallo du!
Sende

Nachricht:
    Nachricht: Die Funktion wurde aufgerufen.
    Sende
    Antworte Dies ist der Rückgabewert.
Danke

Sende an Leo
Sende
```
Natürlich leidet die Lesbarkeit unter exzessiver Verwendung der aktuellen Nachricht.

Die aktuelle Nachricht ist lokal an den aktuellen Scope gebunden: Wenn du Funktionen (Nachrichten) oder Schleifen schachtelst, behält sich jede davon ihre eigene aktuelle Nachricht. Um eine Nachricht in der Verschachtelung nach oben oder unten zu geben, musst du sie benennen.
        """]

befehle1 = ["""
**Wichtig**
Mit [ ] eingeklammerte Teile können weggelassen werden.

Ein mehrzeiliger Block (mehrzeilige Nachricht, if-Abfrage) muss mit einer Zeile
```Danke.```
beendet werden. (Der Punkt nach `Danke` ist optional.)

Du kannst Befehle, die sich nur auf eine Zeile erstrecken, optional mit einem Punkt beenden.

Im Folgenden stehen Großbuchstaben für Nachrichten, Kleinbuchstaben für Literale (Strings, Zahlen, ...).


**Liste aller Befehle**
```Nachricht [namens a] [an b]: c```
Speichert eine Nachricht mit Betreff a, Empfänger b und Inhalt c.
Die Nachricht wird außerdem zur aktuellen Nachricht, egal ob der Betreff weggelassen wurde.
Eine Nachricht ohne Empfänger wird bei `Send` in den Channel gepostet, in dem das Skript aufgerufen wurde.

```Nachricht [namens a] [an b]:
    c (beliebig viele Zeilen)
Danke.```
Wie der vorige Befehl, aber mehrere Zeilen, etwa um eine Funktion zu schreiben.
Der Doppelpunkt ist in diesem Fall optional.

```Sende [A] [an b].```
Poste Nachricht A, oder die aktuelle Nachricht. b muss der Name eines Textchannels sein, auf den du Zugriff hast.
Wenn b leer ist, wird in den Channel gepostet, in dem das Skript aufgerufen wurde.
Wenn b 'Leo' ist, wird die Nachricht nicht gepostet, sondern als Leoscript ausgewertet. Die bisher gesetzten Variablen bleiben auch innerhalb dieses neuen Skripts verfügbar, und im neuen Skript gesetzte Variablen sind auch außerhalb verfügbar. Mit anderen Worten, alle Variablen sind global.
Die einzige Ausnahme ist die aktuelle Nachricht, die lokal für jeden Scope ist.

```Antworte [a].```
Beende das aktuelle Programm mit Rückgabewert a, oder mit dem Inhalt der aktuellen Nachricht, falls a weggelassen wurde.
Dies ist das gleiche wie das `return` statement in anderen Sprachen.

""",
"""
```Notiere [A] [als b].```
Speichere den Inhalt von A in einer Nachricht mit Betreff b.
Falls A nicht angegeben ist, notiere den Inhalt der aktuellen Nachricht.
Falls b nicht angegeben ist, notiere den Inhalt _in_ der aktuellen Nachricht.

```Ergänze [A] um [B].```
Hänge den Inhalt von B an den Inhalt von A an. Dies ersetzt Nachricht A durch die längere. Wenn du eine neue Kopie möchtest, solltest du zuerst den `Notiere`-Befehl benutzen, um A in eine neue Nachricht zu kopieren.
Sowohl A als auch B können weggelassen werden und werden dann durch die aktuelle Nachricht ersetzt.
Insbesondere hat die Zeile `Ergänze.` ohne Angaben den Effekt, dass der Inhalt der aktuellen Nachricht verdoppelt wird.

```Frage [in a].```
Fragt Input von einem Benutzer ab. a muss der Name eines Textchannels sein. Die nächste Nachricht, die in a gepostet wird, wird zum Inhalt der aktuellen Nachricht.
Wenn a weggelassen wird, wird der Channel verwendet, in dem das Skript aufgerufen wurde.

```Falls [a],```
Leitet einen konditionalen Block ein. a muss eine logische Formel sein (siehe `\\leo doc logik`).
Wenn a zu _wahr_ auswertet, werden die Zeilen in diesem Block ausgeführt, sonst nicht.
Der Block muss mit `Danke` beendet werden.
Wenn a weggelassen wird, wird der Inhalt der aktuellen Nachricht als logischer Ausdruck ausgewertet.
Das Komma ist optional.""",
"""
```Danke.```
Beendet den aktuellen Block.

```Berechne [a].```
Führt eine Rechnung aus und speichert das Ergebnis als aktuelle Nachricht.
Falls a weggelassen wird, wird der Inhalt der aktuellen Nachricht als Formel ausgewertet.

Dieser Befehl ist komplexer, als er aussieht:
Zuerst wird alles in a, was der Betreff einer existierenden Nachricht ist, durch den Inhalt dieser Nachricht ersetzt. Das erlaubt die Verwendung von Variablen in a.
Danach wird a als mathematische Formel ausgewertet. Diese versteht (Komma-)Zahlen, +, *, -, /, ^ (Exponentiation), Klammern, die Konstanten PI und E, und die Funktionen sin, cos, tan, abs (Betrag), trunc (abrunden), round (echtes Runden) und sgn (Vorzeichen).
Beachte, dass _zuerst_ die Variablenersetzung stattfindet. Das bedeutet, dass deine Nachricht selbst wieder eine Formel enthalten kann, aber keine weiteren Variablennamen.
Nachrichten, deren Betreff Rechenzeichen enthält, werden von diesem Befehl nicht erkannt.
"""]

logik = ["""
Folgende logische Ausdrücke werden aktuell erkannt. Kommt der Name einer Nachricht in einem Ausdruck vor, so wird er durch den Inhalt dieser Variable ersetzt.

```a = b```
Teste a und b auf Gleichheit. Wenn a und b Zahlen sind, bedeutet das mathematische Gleichheit, ansonsten testet Leo, ob es sich um den gleichen String handelt.

```a < b```
Wenn a und b Zahlen sind, testet Leo, ob a die kleinere Zahl ist, ansonsten, ob a weniger Zeichen hat als b.
"""]


exinhalt = ["""
`\\leo beispiel for`: Wie man eine Schleife implementiert, die eine bestimmte Anzahl von Ausführungen durchläuft.

Du kannst jedes Beispiel in Aktion sehen, indem du `\\leo vorführung beispielname` aufrufst.
Die vollständige Dokumentation von leoscript findest du unter `\\leo doc`.
"""]

exfor = ["""
# Implementierung einer for-Schleife mit fünf Wiederholungen

# initialisiere counter für for-Schleife
Nachricht namens counter: 5

# rekursive Schleife
Nachricht namens for

    Falls 0<counter

        # dekrementiere counter
        Berechne counter-1
        Notiere als counter

        Nachricht: Hallo! Nr.
        Ergänze um counter.
        Sende

        # rekursiver Aufruf
        Sende for an Leo
    Danke
Danke.

# hier startet die Ausführung
Sende for an Leo
"""]


beispiele = {
    "0": exinhalt,
    "for": exfor,
}

