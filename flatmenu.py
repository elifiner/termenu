# An attempt to implement a one-line menu in the terminal

import os
import sys
import fcntl
import termios
import select
import errno

STDIN = sys.stdin.fileno()
    
class Keyboard(object):
    enabled = False
    def start(self):
        self._oldterm = termios.tcgetattr(STDIN)
        newattr = termios.tcgetattr(STDIN)
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(STDIN, termios.TCSANOW, newattr)
        self._old = fcntl.fcntl(STDIN, fcntl.F_GETFL)
        fcntl.fcntl(STDIN, fcntl.F_SETFL, self._old | os.O_NONBLOCK)
        self.enabled = True
    def end(self, *args):
        if self.enabled:
            termios.tcsetattr(STDIN, termios.TCSAFLUSH, self._oldterm)
            fcntl.fcntl(STDIN, fcntl.F_SETFL, self._old)
        self.enabled = False
    def getKey(self):
        select.select([STDIN], [], [])
        return sys.stdin.read(1)
    def getKeyCode(self):
        return ord(self.getKey())
    def getSequence(self):
        sequence = []
        select.select([STDIN], [], [])
        while True:
            try:
                sequence.append(ord(sys.stdin.read(1)))
            except IOError, e:
                if e.errno == errno.EAGAIN:
                    break
        return sequence

    def __enter__(self):
        self.start()
        return self
    def __exit__(self, *args):
        self.end()

if __name__ == "__main__":
    with Keyboard() as keyboard:
        while True:
            sequence = keyboard.getSequence()
            print sequence

