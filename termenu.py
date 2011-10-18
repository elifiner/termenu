import sys
import ansi
import keyboard

# Get the size of the current terminal
# (http://stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python)
def get_terminal_size():
    import fcntl, termios, struct
    h, w, hp, wp = struct.unpack('HHHH',
        fcntl.ioctl(0, termios.TIOCGWINSZ,
        struct.pack('HHHH', 0, 0, 0, 0)))
    return w, h

class Menu(object):
    MARGIN = 5
    def __init__(self, header, options, default=0, clearOnExit=False, separator="  "):
        self.header = header
        self.options = list(options)
        self.default = default
        self.clearOnExit = clearOnExit
        self.separator = separator
        self.selected = max(0, self.default % len(self.options))
        self.slices = lambda: self._paginate(options, get_terminal_size()[0])

    def _print(self, data):
        sys.stdout.write(data)
        sys.stdout.flush()

    def _printMenu(self):
        [(first, last)] = [(start, end) for start, end in self.slices() if start <= self.selected < end]
        optionsCopy = list(self.options)
        optionsCopy[self.selected] = ansi.colorize(optionsCopy[self.selected], "black", "white")
        optionsStr = self.separator.join(optionsCopy[first:last])
        if first > 0:
            optionsStr = "< " + optionsStr
        if last < len(self.options):
            optionsStr = optionsStr + " >"
        ansi.clearline()
        self._print("\r")
        self._print(ansi.colorize(self.header, "white", bright=True) + optionsStr)

    def _paginate(self, options, maxWidth):
        slices = []
        start = 0
        contents = []
        for i, option in enumerate(options):
            contents.append(option)
            if len(self.header) + len(self.separator.join(contents)) + self.MARGIN > maxWidth:
                slices.append((start, i))
                start = i
                contents = [option]
        slices.append((start, len(options)))
        return slices

    def show(self):
        ansi.hidecur()
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
            if self.clearOnExit:
                ansi.clearline()
                self._print("\r")
            else:
                self._print("\n")
            ansi.showcur()

def show_menu(header, options, default=0, clearOnExit=False, separator="  "):
    menu = Menu(header, options, default, clearOnExit, separator)
    return menu.show()
    
if __name__ == "__main__":
    import __builtin__
    builtin = show_menu("Show help for: ", sorted(dir(__builtin__), key=lambda v: v.lower()), clearOnExit=True)
    if builtin:
        help(getattr(__builtin__, builtin))
