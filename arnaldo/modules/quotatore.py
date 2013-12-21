# vim: set fileencoding=utf-8:

from arnaldo.modules import Arnaldigno, comanda
import arnaldo.brain

import time
from random import choice
import re

class Quotatore(Arnaldigno):
    @comanda('^%s[:, \\t]*addquote (.*)')
    def add_quote(self, e, match):
        author = e.source.nick
        quote = match.groups()[0]
        maxa = max([int(x.split(':')[1]) for x in brain.keys('quote:*')])
        q = {"author": author, "date": str(time.time()), "id": str(maxa+1), "quote":quote }
        braind.set("quote:%d"%(maxa+1),q)

    # prima che qualche faccia di merda si lamenti
    # e' l'eval per ritrasformare il tostring di un 
    # dizionario (di stringhe per giunta) di nuovo
    # nel dizionario originale.
    # vale la regola, se riuscite a romperlo bravi/lode/avete ragione
    # altrimenti ANDATE IN CULO.

    @comanda('^%s[:, \\t]*quote$')
    def random_quote(self, e, match):
        q = brain.get(choice(brain.keys("quote:*")))

        if q is None:
            return

        q = eval(q)
        self.r(e, '#%s: %s' % (q['id'], q['quote'].decode('utf8')))

    @comanda('^%s[:, \\t]*quote (.*)$')
    def search_quote(self, e, match):
        pattern = match.groups()[0]

        regex = re.compile(".*(%s).*"%pattern)

        # <PAZO>
        k = brain.keys("quote:*")
        listo = [eval(l) for l in brain.mget(*k)]
        resp = [r for r in listo if regex.search(r['quote'])]
        # </PAZO>

        r = choice(resp) if len > 0 else None
        if r is None:
            self.r(e, 'no such quote')
            return None

        self.r(e, '#%s: %s' % r['id'], r['quote'].decode('utf8'))

if __name__ == '__main__':
    random_quote()
    
