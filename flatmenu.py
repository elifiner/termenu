import sys
import keyboard

class Ansi(object):
    startHighlight = "\x1b[0;47;30m"
    endHighlight = "\x1b[m"
    hideCursor = "\x1b[?25l"
    showCursor = "\x1b[?25h"
    clearLine = "\x1b[2K"

class Menu(object):
    def __init__(self, *options):
        self.options = options
        self.selected = 0
    def _printMenu(self):
        optionsCopy = list(self.options)
        optionsCopy[self.selected] = Ansi.startHighlight + optionsCopy[self.selected] + Ansi.endHighlight
        self._print("\r" + " ".join(optionsCopy))
        sys.stdout.flush()
    def _print(self, data):
        sys.stdout.write(data)
    def run(self):
        self._print(Ansi.hideCursor)
        try:
            self._printMenu()
            for key in keyboard.keyboard_listener():
                if key == "right":
                    self.selected = (self.selected + 1) % len(self.options)
                elif key == "left":
                    self.selected = (self.selected + len(self.options) - 1) % len(self.options)
                elif key == "enter":
                    return self.options[self.selected]
                elif key == "esc":
                    return None
                self._printMenu()
        finally:
            self._print("\r" + Ansi.clearLine + Ansi.showCursor)
    
if __name__ == "__main__":
    menu = Menu("one", "two", "tree", "boom")
    print menu.run()
