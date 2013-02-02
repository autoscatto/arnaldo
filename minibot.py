# This Python file uses the following encoding: utf-8

import sys
import socket
import string
import re

class MiniBot(object):
    def __init__(self, host, port, chan, nick, ident='Anna', realname='Anna', verbose=True):
        # user-defined attributes
        self.host = host
        self.port = port
        self.chan = chan
        self.nick = nick
        self.ident = ident
        self.realname = realname
        self.verbose = verbose

        # commands management (requires runtime setup)
        self.admins = [] # nicknames with admin privileges
        self.__user_commands = []
        self.__admin_commands = []

        # private data
        self.__sock = socket.socket()
        self.__connected = False

        self.__strip_name = re.compile('^\s*(' + self.nick + ')?[,:]?\s*')

    ############################# Public methods ###############################

    def start(self):
        self.__join()

        # start the main loop
        while True:
            message = self.__read()
            tokens = message.split()

            # server message
            if len(tokens) > 0 and tokens[0] == "PING":
                self.__ping_reply(tokens[1])
            elif len(tokens) > 0 and tokens[0] == 'ERROR':
                print "ERROR: %s" % message
                sys.exit()

            # user meesage
            elif len(tokens) > 3 and tokens[1] == "PRIVMSG":
                private = tokens[2] == self.nick # public / private message
                if tokens[3].startswith(':'+'\x01'): # action
                    self.__process_action_message(message, private)
                else :
                    self.__process_message(message, private) # normal message

    def register_command(self, regexp, handler, admin=False):
        command = self.__admin_commands if admin else self.__user_commands
        command.append((re.compile(regexp), handler))

    def write_message(self, text, receiver=None):
        if receiver is None:
            receiver = self.chan

        self.__sock.send("PRIVMSG %s :%s\r\n" % (receiver, text))

    ############# Protected methods (are meant to be overridden) ###############

    def _on_message(self, author, content, private):
        """Invoked when a new message is published on the channel.

        This method is meant to be overridden in order to implement customized
        bot behaviors.

        Arguments
        ---------
        author  --  Nickname of the sender.
        content --  Message content.
        private --  True if the message has been sent to the bot.

        """
        pass

    def _on_action(self, author, action, private):
        """Invoked when a user performs an ACTION through the /me command.

        This method is meant to be overridden in order to implement customized
        bot behaviors.

        Arguments
        ---------
        author  --  Nickname of the sender.
        action  --  User action (string).
        private --  True if the action is performed in query.

        """
        pass


    ############################ Private methods ###############################

    def __join(self):
        self.__deb("Connecting %s as %s..." % (self.chan, self.nick))
        if not self.__connected: # connect only once
            self.__sock.connect((self.host, self.port))
            self.__sock.send("NICK %s\r\n" % self.nick)
            self.__sock.send("USER %s %s 0 :%s\r\n" % (self.ident, self.host, self.realname))
            self.__sock.send("JOIN :%s\r\n" % self.chan)
            self.__connected = True
            self.__deb("...done!")
        else:
            self.__deb("...already connected")

    def __read(self):
        return string.split(self.__sock.recv(2048), "\n")[0].strip()

    def __ping_reply(self, ping):
        self.__sock.send("PONG %s\r\n" % ping)

    def __process_message(self, message, private):
        def parse_commands(stripped_content, commands):
            for r, callback in commands:
                match = r.search(stripped_content)
                if match:
                    try:
                        callback(match)
                        return True
                    except e:
                        self.write_message('Exception: ' + str(e).replace('\n', ' - '))
                        continue

            return False

        self.__deb("Message: %s" % message)

        author, content  = self.__get_author_and_content(message)
        stripped_content = self.__strip_name.sub('', content)
        consumed         = False

        if author in self.admins:
            consumed = parse_commands(stripped_content, self.__admin_commands)

        if consumed:
            return

        consumed = parse_commands(stripped_content, self.__user_commands)
        if consumed:
            return

        self._on_message(author, content, private)

    def __process_action_message(self, message, private):
        try:
            self.__deb("Action: %s" % message)
            author, content = self.__get_author_and_content(message)
            action = content[content.index(' ')+1 : -1]
            self._on_action(author, action, private)
        except:
            pass

    def __get_author_and_content(self, message):
        tokens = message.split()
        author = tokens[0][1 : tokens[0].index('!')]
        content = " ".join(tokens[3:]).strip()[1:]
        return (author, content)

    def __deb(self, msg):
        if self.verbose:
            print msg


################################################################################
################################################################################


# TEST
class BotTest(MiniBot):

    def __init__(self):
        MiniBot.__init__(self, 'irc.freenode.net', 6667, '#fattaccimiei', 'BotTest')

    def _on_message(self, author, content, private):
        if author in self.admins:
            self.write_message("""Hai per caso detto: "%s"? """ % content)

    def _on_action(self, author, action, private):
        self.write_message("Quando %s %s è veramente ridicolo" % (author, action))


if __name__ == "__main__":
    print "Starting Minibot 0.1 Test"
    bot = BotTest()
    bot.admins = ['Cassapanco']
    def eh(s, a, c, p):
        s.write_message("puppa!")
        return True
    bot.register_command("eh?", eh)
    def chisono(s, a, c, p):
        s.write_message("sei %s" % a)
        return True
    bot.register_command("chisono", chisono)
    bot.start()

################################################################################
################################################################################

# BONUS TEST: ROBERTIZE!

#from minibot import MiniBot

#class BotRoberto(MiniBot):

#    def __init__(self):
#        MiniBot.__init__(self, 'irc.freenode.net', 6667, '#fattaccimiei', 'roberto__')
#        import random

#    def _on_message(self, author, content, private):
#        if random.randint(0, 100) <= 50 :
#            print "Robertize!"
#            rob = self.process(content)
#            if rob != '' and rob != content :
#                self.write_message(rob)

#    def process(self, text):
#        tokens = text.split()
#        for i, tok in enumerate(tokens):
#            if random.random() > 0.5:
#                tokens[i] = self.robertize(tok)
#                if random.random() > 0.5: # robertize twice
#                    tokens[i] = self.robertize(tok)
#        return " ".join(tokens)

#    def robertize(self, word):
#        word = list(word)
#        char = word.pop(random.randint(0, len(word)-1))
#        word.insert(random.randint(0, len(word)), char)
#        return "".join(word)


#if __name__ == "__main__":
#    print "Starting BotRoberto 1.0"
#    bot = BotRoberto()
#    bot.start()
