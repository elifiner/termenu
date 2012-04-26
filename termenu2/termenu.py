import sys
sys.path.append("..")

import ansi

class Termenu(object):
    def __init__(self, options, default=None, height=None):
        self.options = options
        self.height = height or 10
        self.cursor = 0
        self.scroll = 0
        self.selected = set()
        self._maxOptionLen = max(len(o) for o in self.options)
        self.set_default(default)

    def set_default(self, default):
        try:
            index = self.options.index(default)
            if index < self.height:
                self.cursor = index % self.height
                self.scroll = 0
            elif index + self.height < len(self.options) - 1:
                self.cursor = 0
                self.scroll = index
            else:
                self.cursor = index % self.height + 1
                self.scroll = len(self.options) - self.height
        except ValueError:
            return

    def get_visible_items(self):
        return self.options[self.scroll:self.scroll+self.height]

    def get_active(self):
        return self.options[self.scroll+self.cursor]

    def get_selected(self):
        return [o for i, o in enumerate(self.options) if i in self.selected]

    def get_result(self):
        if self.selected:
            return self.get_selected()
        else:
            return [self.get_active()]

    def dispatch_key(self, key):
        func = "on_" + key
        if hasattr(self, func):
            return getattr(self, func)()

    def on_down(self):
        if self.cursor < self.height - 1:
            self.cursor += 1
        elif self.scroll + self.height < len(self.options):
            self.scroll += 1

    def on_up(self):
        if self.cursor > 0:
            self.cursor -= 1
        elif self.scroll > 0:
            self.scroll -= 1

    def on_pageDown(self):
        if self.cursor < self.height - 1:
            self.cursor = self.height - 1
        elif self.scroll + self.height * 2 < len(self.options):
            self.scroll += self.height
        else:
            self.scroll = len(self.options) - self.height

    def on_pageUp(self):
        if self.cursor > 0:
            self.cursor = 0
        elif self.scroll - self.height >= 0:
            self.scroll -= self.height
        else:
            self.scroll = 0

    def on_space(self):
        index = self.scroll + self.cursor
        if index in self.selected:
            self.selected.remove(index)
        else:
            self.selected.add(index)
        self.on_down()

    def clear_menu(self):
        ansi.restore_position()
        for i in xrange(self.height):
            ansi.clear_eol()
            ansi.up()
        ansi.clear_eol()

    def print_menu(self):
        for i, item in enumerate(self.get_visible_items()):
            _write(self.decorate(item, **self.decorate_flags(i)) + "\n")

    def decorate_flags(self, i):
        return dict(
            active = (self.cursor == i),
            selected = (self.scroll+i in self.selected),
            moreAbove = (self.scroll > 0 and i == 0),
            moreBelow = (self.scroll + self.height < len(self.options) and i == self.height - 1),
        )

    def decorate(self, item, active=False, selected=False, moreAbove=False, moreBelow=False):
        # all height to same width
        item = "{0:<{width}}".format(item, width=self._maxOptionLen)

        # add selection / cursor decorations
        if active and selected:
            item = "*" + ansi.colorize(item, "red", "white")
        elif active:
            item = " " + ansi.colorize(item, "black", "white")
        elif selected:
            item = "*" + ansi.colorize(item, "red")
        else:
            item = " " + item

        # add more above/below indicators
        if moreAbove:
            item = item + " " + ansi.colorize("^", "white", bright=True)
        elif moreBelow:
            item = item + " " + ansi.colorize("v", "white", bright=True)
        else:
            item = item + "  "

        return item

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
                ansi.up(self.height)
                self.print_menu()
        finally:
            self.clear_menu()
            ansi.show_cursor()

class Minimenu(object):
    def __init__(self, options, default=None):
        self.options = options
        try:
            self.cursor = options.index(default)
        except ValueError:
            self.cursor = 0

    def make_menu(self, decorate=True):
        menu = []
        for i, item in enumerate(self.options):
            if decorate:
                menu.append(ansi.colorize(item, "black", "white") if i == self.cursor else item)
            else:
                menu.append(item)
        menu = " ".join(menu)
        return menu

    def print_menu(self, rewind):
        menu = self.make_menu()
        if rewind:
            menu = "\b"*len(self.make_menu(decorate=False)) + menu
        _write(menu)

    def clear_menu(self):
        menu = self.make_menu(decorate=False)
        _write("\b"*len(menu)+" "*len(menu)+"\b"*len(menu))

    def show(self):
        import keyboard
        ansi.hide_cursor()
        self.print_menu(rewind=False)
        try:
            for key in keyboard.keyboard_listener():
                if key == "enter":
                    self.clear_menu()
                    _write(self.options[self.cursor])
                    return self.options[self.cursor]
                elif key == "esc":
                    self.clear_menu()
                    _write("<esc>")
                    return None
                elif key == "left":
                    self.cursor = max(0, self.cursor - 1)
                elif key == "right":
                    self.cursor = min(len(self.options) - 1, self.cursor + 1)
                self.print_menu(rewind=True)
        finally:
            ansi.show_cursor()
            _write("\n")

def _write(s):
    sys.stdout.write(s)
    sys.stdout.flush()

if __name__ == "__main__":
    menu = Termenu(["option-%06d" % i for i in xrange(1,100)], height=10, default="option-000017")
    print menu.show()
#~     print "Would you like to continue? ",
#~     result = Minimenu(["Abort", "Retry", "Fail"], "Fail").show()
#~     print result
