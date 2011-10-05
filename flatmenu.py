import sys
import keyboard

class Ansi(object):
    startHighlight = "\x1b[0;47;30m"
    endHighlight = "\x1b[m"
    hideCursor = "\x1b[?25l"
    showCursor = "\x1b[?25h"
    clearLine = "\x1b[2K"

def show_menu(options, default=0):
    def _print(data):
        sys.stdout.write(data)
    def _printMenu():
        optionsCopy = list(options)
        optionsCopy[selected] = Ansi.startHighlight + optionsCopy[selected] + Ansi.endHighlight
        _print("\r" + " ".join(optionsCopy))
        sys.stdout.flush()
    selected = max(0, default % len(options))
    _print(Ansi.hideCursor)
    try:
        _printMenu()
        for key in keyboard.keyboard_listener():
            if key == "right":
                selected = (selected + 1) % len(options)
            elif key == "left":
                selected = (selected + len(options) - 1) % len(options)
            elif key == "enter":
                return options[selected]
            elif key == "esc":
                return None
            _printMenu()
    finally:
        _print(Ansi.clearLine + "\r")
        _print(Ansi.showCursor)
    
if __name__ == "__main__":
    print show_menu(["one", "two", "three", "four"], 1)
