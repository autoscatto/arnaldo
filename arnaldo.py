#! /usr/bin/env python
# vim: set fileencoding=utf-8:

import irc.bot
import irc.strings
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr
import cStringIO
from random import choice, randint
import json
import re
import urllib
import urllib2
import time
import sys, traceback
import bleach
from BeautifulSoup import BeautifulSoup
import random
import signal
import sys
import os.path
import os
import time

MULTILINE_TOUT = 0.5

traceback_template = '''Tracefazza (most recent call last):
  File "%(filename)s", line %(lineno)s, in %(name)s
  %(type)s: %(message)s\n'''

URL_RE = re.compile(ur'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))')

def tdecode(bytes):
    try:
        text = bytes.decode('utf-8')
    except UnicodeDecodeError:
        try:
            text = bytes.decode('iso-8859-1')
        except UnicodeDecodeError:
            text = bytes.decode('cp1252')
    return text


def tencode(bytes):
    try:
        text = bytes.encode('utf-8')
    except UnicodeEncodeError:
        try:
            text = bytes.encode('iso-8859-1')
        except UnicodeEncodeError:
            text = bytes.encode('cp1252')
    return text


class TestBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.commands = []

        self.cy = file('SUB-EST2011-01.csv', 'r').read()
        self.nn = file('nounlist.txt', 'r').read()

        self.parliamo_summary = None
        self.BAM = None

        self.register_command('ANAL', self.anal)
        self.register_command('e allora\\?$', self.eallora)
        self.register_command('^allivello\\?', self.allivello)
        self.register_command('parliamo di', self.allivello)
        self.register_command('parliamone', self.checcazzo)
        self.register_command('anche no', self.ancheno)
        self.register_command('beuta', self.beuta)
        self.register_command('^facci (.+)', self.accollo)
        self.register_command('boobs please', self.bombe)
    
    def on_muori(self,a,b):
        msg=None
        author=None
        message=None
        if os.path.isfile('arnaldo.commit'):
            try:
                f=open('arnaldo.commit',"r")
                allo=f.readline()
                f.close()
                allo=allo.split(':')
                author=allo[0]
                message=":".join(allo[1:])
            except:
                pass
        if author!=None and message!=None:
            message='[%s ha committato "%s"]'%(author, message)
        self.connection.privmsg(self.channel, message if message !=None else "speriamo venga la guerra!" )
        self.connection.disconnect("mi levo di 'ulo.")
        sys.exit(0)

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_privmsg(self, c, e):
        self.do_command(e)

    def on_pubmsg(self, c, e):
        self.do_command(e)

    def register_command(self, regexp, handler, admin=False):
        self.commands.append((re.compile(regexp), handler))

    def do_command(self, e):
        self.BAMBAM(e)
        for r, callback in self.commands:
            match = r.search(e.arguments[0])
            if match:
                try:
                    callback(e, match)
                    return True
                except Exception as ex:
                    excfazza="Error in"
                    for frame in traceback.extract_tb(sys.exc_info()[2]):
                        fname,lineno,fn,text = frame
                        excfazza=excfazza+ "%s on line %d; " % (fname, lineno)
                    self.reply(e, excfazza+'      Exception: ' + str(ex).replace('\n', ' - '))
                    continue

        self.oembed_link(e)
    
    def bombe(self, e, match):
        urlo = "http://imgur.com/r/boobies/new/day/page/%d/hit?scrolled"
        response = urllib2.urlopen(urlorandom.randint(1,50)).read()
        soup = BeautifulSoup(response)
        l=soup.findAll("div",{"class":"post"})
        i=choice(l)
        self.reply(e, "http://i.imgur.com/%s.jpg"%i.get("id"))

    def reply(self, e, m):
        target = e.source.nick if e.target == self.connection.get_nickname() else e.target
        if '\n' in m:
            ll=m.split('\n')
            if len(ll)>12:
                self.connection.privmsg(target, "flodda tu ma'")
            else:
                for l in ll:
                  self.connection.privmsg(target, l)
                  time.sleep(MULTILINE_TOUT)
        else:
            self.connection.privmsg(target, m)

    def anal(self, e, match):
        self.reply(e, self.ANAL())

    def allivello(self, e, match):
        self.reply(e, self.parliamo())

    def eallora(self, e, match):
        self.reply(e, "e allora le foibe?")
    
    def accollo(self, e, match):
        ggallin=None;
        try:
            ggallin=match.groups()[0]
        except:
            pass
        if ggallin:
            urlo="http://shell.appspot.com/shell.do"
            session="agVzaGVsbHITCxIHU2Vzc2lvbhjdlpXJnooGDA"
            response = urllib2.urlopen(urlo+"?&"+urllib.urlencode((("statement",ggallin.replace("@t","    ").replace("@n","\n")),("session",session)))).read()
        self.reply(e,response)
            

    def ANAL(self):
        citta=choice([[a.split(',')[1] for a in (self.cy).split(",,,,")[6:-11]]][0])
        citta=citta.upper()
        citta=citta.replace("(BALANCE)",'').replace("CITY",'')
        if citta[-1:]==" ":
            citta=citta[:-1]
        nome=choice(self.nn.split('\n')).upper()
        return "%s ANAL %s"%(citta,nome)

    def request_oembed(self, url):
        query = urllib.urlencode((('url', url),))
        data = urllib2.urlopen('http://noembed.com/embed?' + query)
        respa = json.loads(data.read()) #meglio una raspa d'una ruspa
        return respa

    def beuta(self,e, match):
        cocktail_id=random.randint(1, 4750)
        data=urllib2.urlopen("http://www.cocktaildb.com/recipe_detail?id=%d"%cocktail_id)
        soup = BeautifulSoup(data.read())
        directions=soup.findAll("div", { "class" : "recipeDirection" })
        measures=soup.findAll("div", { "class" : "recipeMeasure" })

        s="== %s ==\n"%(soup.find("h2").text)

        for m in measures:
            s=s+u' '.join(m.findAll(text=True))+"\n"

        for d in directions:
            s=s+u' '.join(d.findAll(text=True))+"\n"
        self.reply(e, ';'.join(s.split('\n')))

    def parliamo(self):
        wikipedia_url = 'http://it.wikipedia.org/wiki/Speciale:PaginaCasuale#'
        wikipedia_url += str(time.time())
        respa = self.request_oembed(wikipedia_url)
        corpo=respa.get('html',None)
        text="macche'"
        if corpo != None:
            soup = BeautifulSoup(respa['html'])
            if soup.p:
                text=bleach.clean(soup.p,tags=[], strip=True)
        self.parliamo_summary = ' '.join(text.split('\n'))
        return u'Parliamo di ' + respa.get('title',"macche'")

    def checcazzo(self, e, match):
        if self.parliamo_summary:
            self.reply(e, self.parliamo_summary[:430])
            self.parliamo_summary = None

    def oembed_link(self, e):
        allurls = URL_RE.findall(e.arguments[0])
        if len(allurls) != 1:
            pass

        try:
            respa = self.request_oembed(allurls[0][0])
            self.reply(e, respa['title'])
        except:
            pass

    def BAMBAM(self, e):
        t = e.arguments[0]
        if self.BAM == t:
            self.reply(e, self.BAM)
            self.BAM = None
        else:
            try:
                if self.BAM.lower() == self.BAM and \
                        self.BAM.upper() == t:
                    marks = re.compile("([!?.;:]+)$")
                    m = marks.search(t)
                    if m:
                        m = m.groups()[0]
                        t = marks.sub('', t)
                    else:
                        m = ''
                    t = re.sub('i?[aeiou]$', '', t, flags=re.IGNORECASE)
                    self.reply(e, "%sISSIMO%s" % (t, m))
                    self.BAM = None
                else:
                    self.BAM = t
            except:
                self.BAM = t


    def ancheno(self, e, match):
        if self.parliamo_summary:
            self.reply(e, u'ಥ_ಥ  ockay')
            self.parliamo_summary = u'┌∩┐(◕_◕)┌∩┐'

def main():
    import sys
    if len(sys.argv) != 4:
        print "Usage: testbot <server[:port]> <channel> <nickname>"
        sys.exit(1)

    s = sys.argv[1].split(":", 1)
    server = s[0]
    if len(s) == 2:
        try:
            port = int(s[1])
        except ValueError:
            print "Error: Erroneous port."
            sys.exit(1)
    else:
        port = 6667
    channel = sys.argv[2]
    nickname = sys.argv[3]

    bot = TestBot(channel, nickname, server, port)
    signal.signal(signal.SIGUSR1, bot.on_muori)
    bot.start()

if __name__ == "__main__":
    main()
