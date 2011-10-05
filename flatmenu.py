# An attempt to implement a one-line menu in the terminal

import os
import sys
import fcntl
import termios
import select
import errno
import contextlib

STDIN = sys.stdin.fileno()

class Keys(object):
    ESC = [27]
    RETURN = [10]
    RIGHT = [27, 91, 68]
    TOP = [27, 91, 65]
    LEFT = [27, 91, 65]
    BOTTOM = [27, 91, 66]

class RawTerminal(object):
    def __init__(self, blocking=True):
        self._blocking = blocking

    def open(self):
        # Set raw mode
        self._oldterm = termios.tcgetattr(STDIN)
        newattr = termios.tcgetattr(STDIN)
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(STDIN, termios.TCSANOW, newattr)

        # Set non-blocking IO on stdin
        self._old = fcntl.fcntl(STDIN, fcntl.F_GETFL)
        if not self._blocking:
            fcntl.fcntl(STDIN, fcntl.F_SETFL, self._old | os.O_NONBLOCK)

    def close(self):
        # Restore previous terminal mode
        termios.tcsetattr(STDIN, termios.TCSAFLUSH, self._oldterm)
        fcntl.fcntl(STDIN, fcntl.F_SETFL, self._old)

    def __enter__(self):
        self.open()

    def __exit__(self, *args):
        self.close()

def key_listener():
    with RawTerminal(blocking=False):
        # return keys
        sequence = []
        while True:
            # wait for keys to become available
            select.select([STDIN], [], [])
            # read all available keys
            while True:
                try:
                    sequence.append(ord(sys.stdin.read(1)))
                except IOError, e:
                    if e.errno == errno.EAGAIN:
                        break
            # handle ANSI arrow keys sequence
            if len(sequence) in [3, 4] and sequence[0] == 27 and sequence[1] in [91, 79]:
                yield sequence
                sequence = []
            # handle normal keys
            else:
                for key in sequence:
                    yield [key]
                sequence = []
    
if __name__ == "__main__":
    for key in key_listener():
        print key

