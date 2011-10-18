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
    def __init__(self, header, options, default=0, clearOnExit=True, separator="  "):
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
        ansi.clear_line()
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
        ansi.hide_cursor()
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
                ansi.clear_line()
                self._print("\r")
            else:
                self._print("\n")
            ansi.show_cursor()

class VerticalMenu(object):
    def __init__(self, header, options, default=0, clearOnExit=True):
        self.header = header
        self.options = options
        self.selected = max(0, default % len(self.options))
        self.width = max(len(option) for option in self.options)
        self.clearOnExit = clearOnExit

    def _print(self, data):
        sys.stdout.write(data)
        sys.stdout.flush()

    def _printSelected(self, highlighted):
        ansi.restore_position()
        moveUp = len(self.options)-self.selected-1
        if moveUp:
            ansi.up(moveUp)
        option = self.options[self.selected]
        option += " " * (self.width - len(option))
        option = " %s " % option
        if highlighted:
            self._print(ansi.colorize(option, "black", "white"))
        else:
            self._print(option)
        ansi.restore_position()

    def show(self):
        self._print(ansi.colorize(self.header, "white", bright=True) + "\n")
        ansi.hide_cursor()
        for option in self.options[:-1]:
            self._print(" " + option + "\n")
        self._print(" " + self.options[-1] + "\r")
        ansi.save_position()
        self._printSelected(True)
        try:
            for key in keyboard.keyboard_listener():
                if key == "down":
                    self._printSelected(highlighted=False)
                    self.selected = (self.selected + 1) % len(self.options)
                    self._printSelected(highlighted=True)
                elif key == "up":
                    self._printSelected(highlighted=False)
                    self.selected = (self.selected + len(self.options) - 1) % len(self.options)
                    self._printSelected(highlighted=True)
                elif key == "enter":
                    return self.options[self.selected]
                elif key == "esc":
                    return None
        finally:
            ansi.restore_position()
            if self.clearOnExit:
                lines = len(self.options) + 1
                ansi.up(lines)
                for i in xrange(lines):
                    ansi.down()
                    ansi.clear_line()
                ansi.up(lines-1)
            ansi.show_cursor()

def show_menu(header, options, default=0, clearOnExit=True, separator="  "):
    menu = Menu(header, options, default, clearOnExit, separator)
    return menu.show()

def show_vertical_menu(header, options, default=0, clearOnExit=True):
    menu = VerticalMenu(header, options, default, clearOnExit)
    return menu.show()
    
if __name__ == "__main__":
    import __builtin__
    builtin = show_menu("Show help for: ", sorted(dir(__builtin__), key=lambda v: v.lower()), clearOnExit=True)
#~     builtin = show_vertical_menu("Show help for:", list(sorted(dir(__builtin__), key=lambda v: v.lower()))[10:30])
    if builtin:
#~         print builtin
        help(getattr(__builtin__, builtin))
