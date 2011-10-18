import sys

COLORS = dict(black=0, red=1, green=2, yellow=3, blue=4, magenta=5, cyan=6, white=7, default=9)

def _print(text):
    sys.stdout.write(text)
    sys.stdout.flush()

def up(n=1):
    _print("\x1b[%dA" % n)

def down(n=1):
    _print("\x1b[%dB" % n)

def forward(n=1):
    _print("\x1b[%dC" % n)

def back(n=1):
    _print("\x1b[%dD" % n)

def move_horizontal(column=1):
    _print("\x1b[%dG" % column)

def move(row, column):
    _print("\x1b[%d;%dH" % (row, column))

def clear_screen():
    _print("\x1b[2J")

def clear_line():
    _print("\x1b[2K")

def save_position():
    _print("\x1b[s")

def restore_position():
    _print("\x1b[u")

def hide_cursor():
    _print("\x1b[?25l")

def show_cursor():
    _print("\x1b[?25h")

def colorize(string, color, background=None, bright=False):
    color = 30 + COLORS.get(color, COLORS["default"])
    background = 40 + COLORS.get(background, COLORS["default"])
    return "\x1b[0;%d;%d;%dm%s\x1b[0;m" % (int(bright), color, background, string)

if __name__ == "__main__":
    # Print all colors
    colors = [name for name, color in sorted(COLORS.items(), key=lambda v: v[1])]
    for bright in [False, True]:
        for background in colors:
            for color in colors:
                print colorize("Hello World!", color, background, bright),
            print
        print
