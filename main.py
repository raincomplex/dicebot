#!/usr/bin/python2
import re, random
from ConfigParser import ConfigParser
from ircbot import IRCbot


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
        r = parseRoll(msg)
        if r:
            out = ', '.join('%s=%s' % (a, b) for a, b in r)

            if dest.startswith('#'):
                d = dest
            else:
                d = src[0]
            
            self.send2(None, 'PRIVMSG', [d], out)

class Roll:
    dice = 1
    sides = 6
    offset = 0
    
    def __call__(self):
        t = 0
        for i in range(self.dice):
            t += random.randint(1, self.sides)
        return t + self.offset

    def __str__(self):
        return '%sd%d%s' % (self.dice if self.dice != 1 else '', self.sides, ('+' + str(self.offset)) if self.offset != 0 else '')

re_die = re.compile(r'(\d+)?d(\d+)(?:\+(\d+))?$')

def parseRoll(msg):
    if ',' in msg:
        msg = msg.split(',')
    else:
        msg = [msg]

    result = []
    for w in msg:
        w = w.strip()
        m = re_die.match(w)
        if m:
            r = Roll()
            r.dice = int(m.group(1) or 1)
            r.sides = int(m.group(2))
            r.offset = int(m.group(3) or 0)
            result.append((str(r), r()))
    
    return result

main()
