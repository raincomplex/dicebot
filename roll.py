import re, random

class Roll:
    dice = 1
    sides = 6
    offset = 0
    
    def __call__(self):
        lst = []
        t = 0
        for i in range(self.dice):
            x = random.randint(1, self.sides)
            lst.append(x)
            t += x
        t += self.offset
        return t, lst

    def __str__(self):
        off = ((('+' if self.offset >= 0 else '') + str(self.offset)) if self.offset != 0 else '')
        return '%sd%d%s' % (self.dice if self.dice != 1 else '', self.sides, off)

re_die = re.compile(r'(\d+)?([dD])(\d+)(?:([-+])(\d+))?$')

def parseRoll(msg):
    if ',' in msg:
        msg = msg.split(',')
    else:
        msg = [msg]

    lst = []
    for w in msg:
        w = w.strip()
        m = re_die.match(w)
        if not m:
            return None

        r = Roll()
        r.dice = int(m.group(1) or 1)
        r.expand = (m.group(2) == 'D')
        r.sides = int(m.group(3))
        if m.group(4):
            sign = (-1 if m.group(4) == '-' else 1)
            num = int(m.group(5))
            r.offset = sign * num
        
        lst.append(r)
    
    return lst
