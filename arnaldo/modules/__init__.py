def comanda(regex):
    def d(f):
        f.regex = regex
        return f
    return d

class Arnaldigno(object):
    def __init__(self, arnaldo):
        self.arnaldo = arnaldo

        for name, thing in self.__class__.__dict__.iteritems():
            regexp = getattr(thing, 'regex', None)
            if regexp:
                self.arnaldo.register_command(regexp, thing)

    def r(self, e, m):
        self.arnaldo.reply(e, m)
        
