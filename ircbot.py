import socket, select, time, sys, re

class IRCbot:
    name = 'ircbot'
    default_channels = None
    loggedin = False
    
    def __init__(self, name, chans):
        '''This default constructor is entirely optional,
        although it is highly recommended that you set 'name'.
        '''
        self.name = name
        self.default_channels = chans
    
    def send(self, cmd):
        'a simple command sending convenience function'
        self.obuf += cmd + '\r\n'
    
    def send2(self, src, cmd, args, cstr):
        '''sends a command of the form:
        :src CMD args... :cstr
        
        Any or all of src, args, and cstr may be None.
        '''
        if src: self.obuf += ':%s ' % src
        self.obuf += cmd
        if args:
            if type(args) not in (tuple, list): args = [args]
            self.obuf += ' '  + ' '.join(args)
        if cstr: self.obuf += ' :' + cstr
        self.obuf += '\r\n'
    
    def handleline(self, src, cmd, args, cstr):
        '''default line handler---a few simple actions:
        - join channels when login succeeds
        - respond to pings
        - call privmsg() callback
        
        src = ('name',) or ('name', 'specificname')
        cmd = 'COMMAND'
        args = ['cmd', 'args']
        cstr = 'a message or something'
        
        returns True if the line was handled, False otherwise
        
        override this method to provide your own linehandling.
        to include this method's functionality in yours, use:
        if IRCbot.handleline(self, src, cmd, args, cstr): return True
        '''
        if cmd == '001' and self.default_channels:
            self.loggedin = True
            for channel in self.default_channels:
                self.send('JOIN %s' % channel)
            return True
        
        if cmd == 'PING':
            self.send2(None, 'PONG', None, cstr)
            return True
        
        if cmd == 'PRIVMSG' and len(args) == 1 and cstr:
            self.privmsg(src, args[0], cstr)
        
        return False
    
    def privmsg(self, src, dest, msg):
        '''Private message callback called by IRCbot.handleline();
        will only work if you don't override that method, or if you
        call it explicitly in your method.
        To provide functionality, override this method.
        
        src = as for handleline()
        dest = '#channel' or 'nick'
        msg = 'message from src to dest'
        '''
        pass
    
    def parseline(self, line):
        '''Internal method to parse a line from the server.
        There should be no reason to override this method.
        
        Calls self.handleline() with the parsed line.'''
        m = re.match(r'((?::\S+ )?)(\S+(?: [^:]\S*)*)((?: :.*)?)$', line)
        if not m:
            print >> sys.stderr, 'WARNING: Failed to match line', repr(line)
            return
        src, cmd, cstr = m.groups()
        if src: src = tuple(src[1:-1].split('!', 1))
        cmd = cmd.split()
        cmd, args = cmd[0].upper(), cmd[1:]
        if cstr: cstr = cstr[2:]
        self.handleline(src, cmd, args, cstr)
    
    def tick(self):
        'called approximately every second---by default, does nothing'
        pass
    
    def connect(self, host, port = 6667):
        '''Connect to a server. Only returns when there is an error
        or the connection is otherwise closed. Call this to start
        your bot.'''
        while 1:
            try:
                sock = socket.socket()
                sock.connect((host, port))
            except KeyboardInterrupt: raise
            except:
                print >> sys.stderr, 'Failed to connect. Retrying in 10...'
                time.sleep(10)
            else: break
        
        self.obuf = ''
        self.send('USER %s * 0 : %s' % (self.name, self.name))
        self.send('NICK %s' % self.name)
        
        ibuf = ''
        while 1:
            try: rd, wr, ex = select.select([sock], [], [sock], 0)
            except KeyboardInterrupt: break
            if rd:
                try: rd = sock.recv(1024)
                except:
                    print >> sys.stderr, 'Read error.'
                    break
                if rd == '':
                    print >> sys.stderr, 'Connection closed.'
                    break
                ibuf += rd
                while '\r\n' in ibuf:
                    line, ibuf = ibuf.split('\r\n', 1)
                    self.parseline(line)
            if ex:
                print >> sys.stderr, 'Socket error.'
                break
            
            if self.obuf:
                try: rd, wr, ex = select.select([], [sock], [], 0)
                except KeyboardInterrupt: break
                if wr:
                    try: i = sock.send(self.obuf)
                    except:
                        print >> sys.stderr, 'Write error.'
                        break
                    self.obuf = self.obuf[i:]
            
            self.tick()
            time.sleep(1)
        
        try: sock.close()
        except: pass


# example echo bot
# say something like: !echo hello

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print >> sys.stderr, 'Usage: %s HOST[:PORT] #CHANNEL'
        exit(1)
    
    # parse sys.argv
    host = sys.argv[1]
    port = 6667
    if ':' in host:
        host, port = host.split(':', 1)
        port = int(port)
    channel = sys.argv[2]
    
    # class to control echobot's behavior
    class EchoBot(IRCbot):
        def privmsg(self, src, dest, msg):
            if msg.startswith('!echo '):
                if dest.startswith('#'): d = dest
                else: d = src[0]
                self.send2(None, 'PRIVMSG', [d], msg[6:])
    
    # create and run the bot
    bot = EchoBot('echobot', [channel])
    bot.connect(host, port)
