# vim: set fileencoding=utf-8:

from arnaldo.modules import Arnaldigno, comanda
import arnaldo.brain

def pritaicsa(text):
    icsa=""
    for row in range(int(brain.brain.get("asciitable:rows"))):
        for c in text:
            icsa=str(icsa)+str(brain.brain.lindex("asciitable:%s"%c,row))
        icsa=icsa+'\n'
    icsa=icsa+'\n'
    return icsa

class Icsah(Arnaldigno):
    @comanda('^icsah (.+)')
    def icsah(self, e, match):
        try:    ggallin = match.groups()[0]
        except: ggallin = None;

        if not ggallin:
            return

        try:
            icsa = pritaicsa(ggallin)
            self.reply(e, icsa)
        except:
            pass

    @comanda('^bamba$')
    def rosa(self, e, match):
        icsa = pritaicsa("rosa")
        self.reply(e,icsa)

