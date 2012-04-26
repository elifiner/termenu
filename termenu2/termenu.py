import sys
sys.path.append("..")

import ansi

class Termenu(object):
    def __init__(self, options, height):
        self.options = options # options in the menu
        self.height = height   # number of height visible on screen
        self.cursor = 0        # visible cursor position (0 is top visible option)
        self.scroll = 0        # index of first visible option
        self.selected = set()
        self._maxOptionLen = max(len(o) for o in self.options)

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
            print self.decorate(item, **self.decorate_flags(i))

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
    def __init__(self, options):
        self.options = options
        self.cursor = 0

    def get_visible_items(self):
        return self.options

    def get_active(self):
        return self.options[self.cursor]

    def on_left(self):
        if self.cursor < len(self.options) - 1:
            self.cursor += 1

    def on_right(self):
        if self.cursor > 0:
            self.cursor -= 1

if __name__ == "__main__":
    menu = Termenu(["option-%06d" % i for i in xrange(1,100)], height=10)
    print menu.show()
