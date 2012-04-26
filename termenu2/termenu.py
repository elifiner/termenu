import sys
sys.path.append("..")

import ansi

class Termenu(object):
    def __init__(self, options, results=None, default=None, height=None, multiselect=True):
        self.options = options
        self.results = results or options
        self.height = height or 10
        self.multiselect = multiselect
        self.cursor = 0
        self.scroll = 0
        self.selected = set()
        self._maxOptionLen = max(len(o) for o in self.options)
        self._set_default(default)

    def get_result(self):
        if self.selected:
            return [self.results[i] for i in sorted(self.selected)]
        else:
            return [self.results[self._get_active_index()]]

    def show(self):
        import keyboard
        self._print_menu()
        ansi.save_position()
        ansi.hide_cursor()
        try:
            for key in keyboard.keyboard_listener():
                self._dispatch(key)
                if key == "enter":
                    return self.get_result()
                elif key == "esc":
                    return None
                ansi.restore_position()
                ansi.up(self.height)
                self._print_menu()
        finally:
            self._clear_menu()
            ansi.show_cursor()

    def _set_default(self, default):
        # handle default selection of multiple items
        if isinstance(default, list) and default:
            if not self.multiselect:
                raise ValueError("multiple defaults passed, but multiselect is False")
            self.selected = set(self._get_index(item) for item in default)
            default = default[0]

        # handle default active item
        index = self._get_index(default)
        if index is not None:
            if index < self.height:
                self.cursor = index % self.height
                self.scroll = 0
            elif index + self.height < len(self.options) - 1:
                self.cursor = 0
                self.scroll = index
            else:
                self.cursor = index % self.height + 1
                self.scroll = len(self.options) - self.height

    def _get_index(self, s):
        try:
            return self.options.index(s)
        except ValueError:
            return None

    def _get_active_index(self):
        return self.scroll + self.cursor

    def _get_visible_items(self):
        return self.options[self.scroll:self.scroll+self.height]

    def _get_debug_view(self):
        items = []
        for i, item in enumerate(self._get_visible_items()):
            items.append(("(%s)" if i == self.cursor else "%s") % item)
        return " ".join(items)

    def _dispatch(self, key):
        func = "_on_" + key
        if hasattr(self, func):
            return getattr(self, func)()

    def _on_down(self):
        if self.cursor < self.height - 1:
            self.cursor += 1
        elif self.scroll + self.height < len(self.options):
            self.scroll += 1

    def _on_up(self):
        if self.cursor > 0:
            self.cursor -= 1
        elif self.scroll > 0:
            self.scroll -= 1

    def _on_pageDown(self):
        if self.cursor < self.height - 1:
            self.cursor = self.height - 1
        elif self.scroll + self.height * 2 < len(self.options):
            self.scroll += self.height
        else:
            self.scroll = len(self.options) - self.height

    def _on_pageUp(self):
        if self.cursor > 0:
            self.cursor = 0
        elif self.scroll - self.height >= 0:
            self.scroll -= self.height
        else:
            self.scroll = 0

    def _on_space(self):
        if not self.multiselect:
            return
        index = self._get_active_index()
        if index in self.selected:
            self.selected.remove(index)
        else:
            self.selected.add(index)
        self._on_down()

    def _clear_menu(self):
        ansi.restore_position()
        for i in xrange(self.height):
            ansi.clear_eol()
            ansi.up()
        ansi.clear_eol()

    def _print_menu(self):
        for i, item in enumerate(self._get_visible_items()):
            _write(self._decorate(item, **self._decorate_flags(i)) + "\n")

    def _decorate_flags(self, i):
        return dict(
            active = (self.cursor == i),
            selected = (self.scroll+i in self.selected),
            moreAbove = (self.scroll > 0 and i == 0),
            moreBelow = (self.scroll + self.height < len(self.options) and i == self.height - 1),
        )

    def _decorate(self, item, active=False, selected=False, moreAbove=False, moreBelow=False):
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

class Minimenu(object):
    def __init__(self, options, default=None):
        self.options = options
        try:
            self.cursor = options.index(default)
        except ValueError:
            self.cursor = 0

    def show(self):
        import keyboard
        ansi.hide_cursor()
        self._print_menu(rewind=False)
        try:
            for key in keyboard.keyboard_listener():
                if key == "enter":
                    self._clear_menu()
                    _write(self.options[self.cursor])
                    return self.options[self.cursor]
                elif key == "esc":
                    self._clear_menu()
                    _write("<esc>")
                    return None
                elif key == "left":
                    self.cursor = max(0, self.cursor - 1)
                elif key == "right":
                    self.cursor = min(len(self.options) - 1, self.cursor + 1)
                self._print_menu(rewind=True)
        finally:
            ansi.show_cursor()
            _write("\n")

    def _make_menu(self, _decorate=True):
        menu = []
        for i, item in enumerate(self.options):
            if _decorate:
                menu.append(ansi.colorize(item, "black", "white") if i == self.cursor else item)
            else:
                menu.append(item)
        menu = " ".join(menu)
        return menu

    def _print_menu(self, rewind):
        menu = self._make_menu()
        if rewind:
            menu = "\b"*len(self._make_menu(decorate=False)) + menu
        _write(menu)

    def _clear_menu(self):
        menu = self._make_menu(decorate=False)
        _write("\b"*len(menu)+" "*len(menu)+"\b"*len(menu))

def _write(s):
    sys.stdout.write(s)
    sys.stdout.flush()

def redirect_std():
    """
    Connect stdin/stdout to controlling terminal even if the scripts input and output
    were redirected. This is useful in utilities based on termenu.
    """
    stdin = sys.stdin
    stdout = sys.stdout
    if not sys.stdin.isatty():
        sys.stdin = open("/dev/tty", "r", 0)
    if not sys.stdout.isatty():
        sys.stdout = open("/dev/tty", "w", 0)
    return stdin, stdout

if __name__ == "__main__":
    menu = Termenu(["option-%06d" % i for i in xrange(1,100)], height=10, default=["option-000019", "option-000021"])
    print menu.show()
#~     print "Would you like to continue? ",
#~     result = Minimenu(["Abort", "Retry", "Fail"], "Fail").show()
#~     print result
