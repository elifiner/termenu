import sys
import keyboard

class Ansi(object):
    startHighlight = "\x1b[0;47;30m"
    endHighlight = "\x1b[m"
    hideCursor = "\x1b[?25l"
    showCursor = "\x1b[?25h"
    clearLine = "\x1b[2K"

# Get the size of the current terminal
# (http://stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python)
def get_terminal_size():
    import fcntl, termios, struct
    h, w, hp, wp = struct.unpack('HHHH',
        fcntl.ioctl(0, termios.TIOCGWINSZ,
        struct.pack('HHHH', 0, 0, 0, 0)))
    return w, h

def show_menu(header, options, default=0, clearOnExit=False, separator=" | ", maxItems=7):
    def _print(data):
        sys.stdout.write(data)
        sys.stdout.flush()
    def _print_menu():
        first = selected - selected % maxItems
        optionsCopy = list(options)
        optionsCopy[selected] = Ansi.startHighlight + optionsCopy[selected] + Ansi.endHighlight
        optionsStr = separator.join(optionsCopy[first:first+maxItems])
        if first > 0:
            optionsStr = "< " + optionsStr
        if first + maxItems < len(options):
            optionsStr = optionsStr + " >"
        _print(Ansi.clearLine + "\r")
        _print(header + optionsStr)
        sys.stdout.flush()
    selected = max(0, default % len(options))
    _print(Ansi.hideCursor)
    try:
        _print_menu()
        for key in keyboard.keyboard_listener():
            if key == "right":
                selected = (selected + 1) % len(options)
            elif key == "left":
                selected = (selected + len(options) - 1) % len(options)
            elif key == "enter":
                return options[selected]
            elif key == "esc":
                return None
            _print_menu()
    finally:
        if clearOnExit:
            _print(Ansi.clearLine + "\r")
        else:
            _print("\n")
        _print(Ansi.showCursor)
    
if __name__ == "__main__":
    print show_menu("Select: ", ["one", "two", "three", "four", "five", "six", "seven"], maxItems=3)
