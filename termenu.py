#!/usr/bin/python
import sys
import ansi

# Get the size of the current terminal
# (http://stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python)
def get_terminal_size():
    import fcntl, termios, struct
    h, w, hp, wp = struct.unpack('HHHH', fcntl.ioctl(sys.stdin,
        termios.TIOCGWINSZ, struct.pack('HHHH', 0, 0, 0, 0)))
    return w, h

class Menu(object):
    """
    An interactive vertical menu to be used in console scripts.

    Example:
        menu = Menu("Select: ", ["item one", "item two", "item three"])
        result = menu.show()
        print result
    """
    def __init__(self, title, options, default=None, height=None, multiSelect=False):
        self.title = title
        self.options = options
        if default is None:
            default = 0
        elif isinstance(default, str):
            try:
                default = options.index(default)
            except ValueError:
                default = 0
        self.selected = max(0, default % len(self.options))
        self.width = max(len(option) for option in self.options)
        maxHeight = get_terminal_size()[1]-2
        if not height or height > maxHeight:
            height = maxHeight
        self.height = min(len(options), height)
        self.first = self.selected - self.selected % self.height
        self.multiSelect = multiSelect
        if multiSelect:
            self.selectedItems = set()
        self.result = None

    def _print(self, data):
        sys.stdout.write(data)
        sys.stdout.flush()

    def _print_menu(self, redraw=False):
        if redraw:
            ansi.restore_position() # go to bottom of menu
            ansi.up(self.height) # go to top of menu
        page = self.options[self.first:self.first+self.height]
        page += [""] * (self.height - len(page))
        for index, option in enumerate(page):
            line = self._build_menu_line(index, option)
            self._print(line + "\n")

    def _build_menu_line(self, index, option):
        line = option + " " * (self.width - len(option))
        line = self._colorize_line(index, line, )
        line = self._build_marker(index) + line
        return line

    def _colorize_line(self, index, line):
        multiSelected = self._is_multi_selected(index)
        if self.first + index == self.selected:
            if multiSelected:
                line = ansi.colorize(line, "red", "white")
            else:
                line = ansi.colorize(line, "black", "white")
        elif multiSelected:
                line = ansi.colorize(line, "red")
        return line

    def _build_marker(self, index):
        if index == 0 and self.first != 0:
            marker = ansi.colorize("^", "white", bright=True)
        elif index == self.height-1 and self.first + self.height < len(self.options):
            marker = ansi.colorize("v", "white", bright=True)
        else:
            marker = " "
        marker += "* " if self._is_multi_selected(index) else "  "
        return marker

    def _is_multi_selected(self, index):
        return self.multiSelect and (self.first + index) in self.selectedItems

    def _on_down(self):
        self.selected += 1
        self._adjust_selected()

    def _on_up(self):
        self.selected -= 1
        self._adjust_selected()

    def _on_pageDown(self):
        if self.selected % self.height < self.height-1:
            self.selected = self.selected - self.selected % self.height + self.height - 1
        else:
            self.selected += self.height
        self._adjust_selected()

    def _on_pageUp(self):
        if self.selected % self.height > 0:
            self.selected = self.selected - self.selected % self.height
        else:
            self.selected -= self.height
        self._adjust_selected()

    def _on_home(self):
        self.selected = 0
        self._adjust_selected()

    def _on_end(self):
        self.selected = len(self.options)-1
        self._adjust_selected()

    def _on_enter(self):
        if self.multiSelect:
            if not self.selectedItems:
                self.selectedItems.add(self.selected)
            self.result = [self.options[i] for i in sorted(self.selectedItems)]
        else:
            self.result = self.options[self.selected]
        return True

    def _on_esc(self):
        self.result = None
        return True

    def _on_space(self):
        if self.multiSelect:
            if self.selected in self.selectedItems:
                self.selectedItems.remove(self.selected)
            else:
                self.selectedItems.add(self.selected)

    def _adjust_selected(self):
        if self.selected < 0:
            self.selected = 0
        if self.selected > len(self.options)-1:
            self.selected = len(self.options)-1
        self.first = self.selected - self.selected % self.height

    def show(self):
        """
        Show the menu and run the keyboard loop. The return value is the text of the chosen option
        if Enter was pressed and None is Esc was pressed.
        """
        import keyboard
        if self.title:
            self._print(ansi.colorize(self.title, "white", bright=True) + "\n")
        self._print_menu(False)
        ansi.save_position() # save bottom-of-menu position for future reference
        ansi.hide_cursor()
        try:
            for key in keyboard.keyboard_listener():
                handler = "_on_" + key
                if hasattr(self, handler):
                    ret = getattr(self, handler)()
                    if ret:
                        return self.result
                self._print_menu(True)
        finally:
            ansi.restore_position()
            lines = self.height
            if self.title:
                lines += 1
            ansi.up(lines)
            for i in xrange(lines):
                ansi.clear_line()
                ansi.down()
            ansi.up(lines)
            ansi.show_cursor()

class MultiSelect(object):
    def __init__(self):
        self.selectedItems = set()

class MultiSelectMenu(MultiSelect, Menu):
    pass

def show_menu(title, options, default=None, height=None, multiSelect=False):
    menu = Menu(title, options, default, height, multiSelect)
    return menu.show()
show_menu
