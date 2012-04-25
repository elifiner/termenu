import sys
sys.path.append("..")

import ansi

class Termenu(object):
    def __init__(self, options, lines):
        self.options = options # number of options in the menu
        self.lines = lines     # number of lines visible on screen
        self.cursor = 0        # visible cursor position (0 is top visible option)
        self.scroll = 0        # index of first visible option

    def get_visible_lines(self):
        return self.options[self.scroll:self.scroll+self.lines]

    def get_selected(self):
        return self.options[self.scroll+self.cursor]

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

    def on_enter(self):
        return True

    def on_esc(self):
        return True

    def print_menu(self):
        for i, line in enumerate(self.get_visible_lines()):
            if self.cursor == i:
                print "*" + line
            else:
                print " " + line

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
        ansi.save_position() # save bottom-of-menu position for future reference
        ansi.hide_cursor()
        try:
            for key in keyboard.keyboard_listener():
                ret = self.dispatch_key(key)
                if ret:
                    return self.get_selected()
                ansi.restore_position() # go to bottom of menu
                ansi.up(self.lines) # go to top of menu
                self.print_menu()
        finally:
            self.clear_menu()
            ansi.show_cursor()

if __name__ == "__main__":
    menu = Termenu(["option-%06d" % i for i in xrange(1,100)], lines=5)
    print menu.show()
