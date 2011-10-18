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
    """
    An interactive one line menu to be used in console scripts.

    Example:
        menu = Menu("Select: ", ["item one", "item two", "item three"])
        result = menu.show()
        print result
    """

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

    def _print_menu(self):
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
        """
        Show the menu and run the keyboard loop. The return value is the text of the chosen option
        if Enter was pressed and None is Esc was pressed.
        """
        ansi.hide_cursor()
        try:
            self._print_menu()
            for key in keyboard.keyboard_listener():
                if key == "right":
                    self.selected = (self.selected + 1) % len(self.options)
                elif key == "left":
                    self.selected = (self.selected + len(self.options) - 1) % len(self.options)
                elif key == "enter":
                    return self.options[self.selected]
                elif key == "esc":
                    return None
                self._print_menu()
        finally:
            if self.clearOnExit:
                ansi.clear_line()
                self._print("\r")
            else:
                self._print("\n")
            ansi.show_cursor()

class VerticalMenu(object):
    """
    An interactive vertical menu to be used in console scripts.

    Example:
        menu = VerticalMenu("Select: ", ["item one", "item two", "item three"])
        result = menu.show()
        print result
    """
    def __init__(self, header, options, default=0, clearOnExit=True, height=None):
        self.header = header
        self.options = options
        self.selected = max(0, default % len(self.options))
        self.width = max(len(option) for option in self.options)
        self.clearOnExit = clearOnExit
        maxHeight = get_terminal_size()[1]-2
        if not height or height > maxHeight:
            height = maxHeight
        self.height = min(len(options), height)
        self.first = self.selected - self.selected % self.height

    def _print(self, data):
        sys.stdout.write(data)
        sys.stdout.flush()

    def _print_menu(self, redraw=False):
        if redraw:
            ansi.restore_position() # go to bottom of menu
            ansi.up(self.height) # go to top of menu
        options = self.options[self.first:self.first+self.height]
        options += [""] * (self.height - len(options))
        for i, option in enumerate(options):
            if i == 0 and self.first != 0:
                marker = ansi.colorize("^ ", "white", bright=True)
            elif i == self.height-1 and self.first + self.height < len(self.options):
                marker = ansi.colorize("v ", "white", bright=True)
            else:
                marker = "  "
            line = option + " " * (self.width - len(option))
            if self.first + i == self.selected:
                line = ansi.colorize(line, "black", "white")
            line = marker + line + "\n"
            self._print(line)

    def show(self):
        """
        Show the menu and run the keyboard loop. The return value is the text of the chosen option
        if Enter was pressed and None is Esc was pressed.
        """
        self._print(ansi.colorize(self.header, "white", bright=True) + "\n")
        self._print_menu(False)
        ansi.save_position() # save bottom-of-menu position for future reference
        ansi.hide_cursor()
        try:
            for key in keyboard.keyboard_listener():
                if key == "down":
                    self.selected += 1
                elif key == "up":
                    self.selected -= 1
                elif key == "pageDown":
                    if self.selected % self.height < self.height-1:
                        self.selected = self.selected - self.selected % self.height + self.height - 1
                    else:
                        self.selected += self.height
                elif key == "pageUp":
                    if self.selected % self.height > 0:
                        self.selected = self.selected - self.selected % self.height
                    else:
                        self.selected -= self.height
                elif key == "home":
                    self.selected = 0
                elif key == "end":
                    self.selected = len(self.options)-1
                elif key == "enter":
                    return self.options[self.selected]
                elif key == "esc":
                    return None
                if self.selected < 0:
                    self. selected = 0
                if self.selected > len(self.options)-1:
                    self.selected = len(self.options)-1
                self.first = self.selected - self.selected % self.height
                self._print_menu(True)
        finally:
            if self.clearOnExit:
                ansi.restore_position()
                ansi.up(self.height+1)
                for i in xrange(self.height+1):
                    ansi.clear_line()
                    ansi.down()
                ansi.up(self.height+1)
            ansi.show_cursor()

def show_menu(header, options, default=0, clearOnExit=True):
    menu = Menu(header, options, default, clearOnExit)
    return menu.show()

def show_vertical_menu(header, options, default=0, clearOnExit=True, height=None):
    menu = VerticalMenu(header, options, default, clearOnExit, height)
    return menu.show()
    
if __name__ == "__main__":
    import __builtin__
    builtin = show_vertical_menu("Show help for: ", sorted(dir(__builtin__), key=lambda v: v.lower()), clearOnExit=True, height=20)
    if builtin:
        print builtin
