# An attempt to implement a one-line menu in the terminal

import os
import sys
import fcntl
import termios
import select
import errno

STDIN = sys.stdin.fileno()

class Keys(object):
    ESC = [27]
    RETURN = [10]
    RIGHT = [27, 91, 68]
    TOP = [27, 91, 65]
    LEFT = [27, 91, 65]
    BOTTOM = [27, 91, 66]

def key_listener():
    # initialize terminal
    oldterm = termios.tcgetattr(STDIN)
    newattr = termios.tcgetattr(STDIN)
    newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
    termios.tcsetattr(STDIN, termios.TCSANOW, newattr)
    old = fcntl.fcntl(STDIN, fcntl.F_GETFL)
    fcntl.fcntl(STDIN, fcntl.F_SETFL, old | os.O_NONBLOCK)

    try:
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
    finally:
        # reset terminal
        termios.tcsetattr(STDIN, termios.TCSAFLUSH, oldterm)
        fcntl.fcntl(STDIN, fcntl.F_SETFL, old)
    
if __name__ == "__main__":
    for key in key_listener():
        print key

