# vim: set fileencoding=utf-8:

from __future__ import unicode_literals
from BeautifulSoup import BeautifulSoup
from blinker import signal as lasigna
import irc.bot
import irc.strings

import os
import os.path
import sys
import re
import time
import json

import urllib
import urllib2
import traceback
import bleach
import random
import signal
import hashlib
import datetime

##

from utieffa import *
from vedetta import Vedetta

import brain

##

from modules.sproloquio import Sproloquio
from modules.parliamo import Parliamo
from modules.quotatore import Quotatore
from modules.accolli import Accolli
from modules.icsah import Icsah
from modules.bam import BAM

print "meglio una raspa di una ruspa"

dimme = lasigna('dimmelo')

URL_RE = re.compile(ur'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))')

def check_SI(p):
    mapping = [(-24,('y','yocto')),(-21,('z','zepto')),(-18,('a','atto')),(-15,('f','femto')),(-12,('p','pico')),
               (-9, ('n','nano')),(-6, ('u','micro')),(-3, ('m','mili')),(-2, ('c','centi')),(-1, ('d','deci')),
               (3,  ('k','kilo')),(6,  ('M','mega')),(9,  ('G','giga')),(12, ('T','tera')),(15, ('P','peta')),
               (18, ('E','exa')),(21, ('Z','zetta')),(24, ('Y','yotta'))]

    for check, value in mapping:
        if p <= check:
            return value

class Arnaldo(irc.bot.SingleServerIRCBot):

    def __init__(self, channel, nickname, server, port=6667):
        irc.client.ServerConnection.buffer_class = BambaRosaNasaBuffer
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.nickname = nickname
        self.channel = channel
        self.commands = []

        dimme.connect(self.dimmeame)

        self.modules = []
        self.modules.append(Sproloquio(self))
        self.modules.append(Parliamo(self))
        self.modules.append(Quotatore(self))
        self.modules.append(Accolli(self))
        self.modules.append(Icsah(self))
        self.modules.append(BAM(self))

    def dimmeame(self,msg):
        conn= self.connection

        if type(msg) == type(()):
           conn.privmsg(self.channel, '<%s>: %s' % msg)
        else:
           conn.privmsg(self.channel, '* %s' % msg)

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
        for r, callback in self.commands:
            match = r.search(e.arguments[0])
            if match:
                try:
                    if not callback(e, match):
                        return True
                except Exception as ex:
                    excfazza="Error in"
                    for frame in traceback.extract_tb(sys.exc_info()[2]):
                        fname,lineno,fn,text = frame
                        excfazza=excfazza+ "%s on line %d; " % (fname, lineno)
                    self.reply(e, excfazza+'      Exception: ' + str(ex).replace('\n', ' - '))
                    continue

        self.oembed_link(e)
    
    def reply(self, e, m):
        MULTILINE_TOUT = 0.5
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


    def request_oembed(self, url):
        query = urllib.urlencode((('url', url),))
        data = urllib2.urlopen('http://noembed.com/embed?' + query)
        respa = json.loads(data.read()) #meglio una raspa d'una ruspa
        return respa

    def oembed_link(self, e):
        allurls = URL_RE.findall(e.arguments[0])
        if len(allurls) != 1:
            pass

        #tipo goto ma peggio
        try:
            try:    respa = self.request_oembed(allurls[0][0])
            except: pass

            thaurlhash= hashlib.md5(allurls[0][0]).hexdigest()
            hashish=brain.brain.get("urlo:%s"%thaurlhash)

            if hashish == None: #NO FUMO NO FUTURE
                ts=time.time()
                nic=e.source.nick
                brain.brain.set("urlo:%s"%thaurlhash,"%f:%s:%d"%(ts,nic,1))
                self.reply(e, respa['title'])
            else:
                SECONDIANNO=31556926 #num secondi in un anno youdontsay.png
                ts,nic,v=hashish.split(':')
                ts=float(ts)
                delta=time.time() -ts
                v=int(v)+1
                brain.brain.set("urlo:%s"%thaurlhash,"%f:%s:%d"%(ts,nic,v))
                manti,expo=map(float,("%e"%(delta/SECONDIANNO)).split("e"))
                symb,todo=check_SI(expo*v)
                dignene="%.2f %sGaggo [postato da %s il %s]"%(manti+v,symb,nic,datetime.datetime.fromtimestamp(ts).strftime('%d/%m/%y %H:%M:%S'))
                self.reply(e, dignene)

        except:
            pass
def main():
    if len(sys.argv) != 4:
        print "Usage: arnaldo <server[:port]> <channel> <nickname>"
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

    T800 = Vedetta()
    T800.start() #I'm a friend of Sarah Connor. I was told she was here. Could I see her please?

    bot = Arnaldo(channel, nickname, server, port)
    signal.signal(signal.SIGUSR1, bot.on_muori)
    bot.start()

