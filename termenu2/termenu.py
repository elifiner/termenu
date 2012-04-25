import sys
sys.path.append("..")

import ansi

class Termenu(object):
    def __init__(self, options, lines):
        self.options = options # number of options in the menu
        self.lines = lines     # number of lines visible on screen
        self.cursor = 0        # visible cursor position (0 is top visible option)
        self.scroll = 0        # index of first visible option
        self.selected = set()
        self._maxOptionLen = max(len(o) for o in self.options)

    def get_visible_lines(self):
        return self.options[self.scroll:self.scroll+self.lines]

    def get_active(self):
        return self.options[self.scroll+self.cursor]

    def get_selected(self):
        return [o for i, o in enumerate(self.options) if i in self.selected] 

    def get_result(self):
        if self.selected:
            return self.get_selected()
        else:
            return [self.get_active()]

    def on_down(self):
        if self.cursor < self.lines - 1:
            self.cursor += 1
        elif self.scroll + self.lines < len(self.options):
            self.scroll += 1

    def on_up(self):
        if self.cursor > 0:
            self.cursor -= 1
        elif self.scroll > 0:
            self.scroll -= 1

    def on_pageDown(self):
        if self.cursor < self.lines - 1:
            self.cursor = self.lines - 1
        elif self.scroll + self.lines * 2 < len(self.options):
            self.scroll += self.lines
        else:
            self.scroll = len(self.options) - self.lines

    def on_pageUp(self):
        if self.cursor > 0:
            self.cursor = 0
        elif self.scroll - self.lines >= 0:
            self.scroll -= self.lines
        else:
            self.scroll = 0

    def on_space(self):
        index = self.scroll + self.cursor
        if index in self.selected:
            self.selected.remove(index)
        else:
            self.selected.add(index)
        self.on_down()

    def print_menu(self):
        for i, line in enumerate(self.get_visible_lines()):
            line = self.decorate(line, 
                active = (self.cursor == i), 
                selected = (self.scroll+i in self.selected),
                moreAbove = (self.scroll > 0 and i == 0),
                moreBelow = (self.scroll + self.lines < len(self.options) and i == self.lines - 1),
            )
            print line

    def decorate(self, line, active=False, selected=False, moreAbove=False, moreBelow=False):
        # all lines to same width
        line = "{0:<{width}}".format(line, width=self._maxOptionLen)

        # add selection / cursor decorations
        if active and selected:
            line = "*" + ansi.colorize(line, "red", "white")
        elif active:
            line = " " + ansi.colorize(line, "black", "white")
        elif selected:
            line = "*" + ansi.colorize(line, "red")
        else:
            line = " " + line

        # add more above/below indicators
        if moreAbove:
            line = line + ansi.colorize("^", "white", bright=True)
        elif moreBelow:
            line = line + ansi.colorize("v", "white", bright=True)
        else:
            line = line + " "

        return line

    def clear_menu(self):
        ansi.restore_position()
        for i in xrange(self.lines):
            ansi.clear_eol()
            ansi.up()
        ansi.clear_eol()

    def dispatch_key(self, key):
        func = "on_" + key
        if hasattr(self, func):
            return getattr(self, func)()

    def show(self):
        import keyboard
        self.print_menu()
        ansi.save_position()
        ansi.hide_cursor()
        try:
            for key in keyboard.keyboard_listener():
                self.dispatch_key(key)
                if key == "enter":
                    return self.get_result()
                elif key == "esc":
                    return None
                ansi.restore_position()
                ansi.up(self.lines)
                self.print_menu()
        finally:
            self.clear_menu()
            ansi.show_cursor()

if __name__ == "__main__":
    menu = Termenu(["option-%06d" % i for i in xrange(1,100)], lines=10)
    print menu.show()
