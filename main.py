#!/usr/bin/python2
from ConfigParser import ConfigParser
from ircbot import IRCbot
from roll import parseRoll

def main():
    cp = ConfigParser()

    if not cp.read('dice.conf'):
        f = open('dice.conf', 'w')
        print >> f, '[bot]'
        print >> f, 'nickname = dicebot'
        print >> f, 'channel = #dicebot'
        print >> f, 'server = irc.freenode.org'
        f.close()

        print 'Please modify dice.conf and restart.'
        exit(1)

    nickname = cp.get('bot', 'nickname')
    channel = cp.get('bot', 'channel')
    server = cp.get('bot', 'server')

    bot = DiceBot(nickname, [channel])
    bot.connect(server, 6667)

class DiceBot(IRCbot):
    def privmsg(self, src, dest, msg):
        rolls = parseRoll(msg)
        if not rolls:
            return

        lst = []
        for r in rolls:
            name = str(r)
            total, indiv = r()
            if r.expand:
                i = ','.join(map(str, indiv))
                s = '%s (%s) = %s' % (name, i, total)
            else:
                s = '%s = %s' % (name, total)
            lst.append(s)

        out = '%s: [%s]' % (src[0], '] ['.join(lst))

        if dest.startswith('#'):
            d = dest
        else:
            d = src[0]

        self.send2(None, 'PRIVMSG', [d], out)

main()
