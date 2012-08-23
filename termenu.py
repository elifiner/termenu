import sys
sys.path.append("..")

import ansi

def pluggable(method):
    """
    Mark a class method as extendable with plugins.
    """
    def wrapped(self, *args, **kwargs):
        if hasattr(self, "_plugins"):
            # call the last plugin, it may call the previous via self.parent.method
            # creating a call call chain
            return getattr(self._plugins[-1], method.__name__)(*args, **kwargs)
        else:
            return method(self, *args, **kwargs)
    wrapped.original = method
    return wrapped

def register_plugin(host, plugin):
    """
    Register a plugin with a host object. Some @pluggable methods in the host
    will have their behaviour altered by the plugin.
    """
    class OriginalMethods(object):
        def __getattr__(self, name):
            return lambda *args, **kwargs: getattr(host, name).original(host, *args, **kwargs)
    if not hasattr(host, "_plugins"):
        host._plugins = [OriginalMethods()]
    plugin.parent = host._plugins[-1]
    plugin.host = host
    host._plugins.append(plugin)

class Termenu(object):
    class _Option(object):
        def __init__(self, text, result, **attrs):
            self.text = text
            self.result = result
            self.selected = False
            self.attrs = attrs
        def __str__(self):
            return self.text
        def __len__(self):
            return len(self.text)

    def __init__(self, options, results=None, default=None, height=None, multiselect=True, plugins=None):
        self.options = [self._Option(o, r) for o, r in zip(options, results or options)]
        self.height = min(height or 10, len(options))
        self.multiselect = multiselect
        self.cursor = 0
        self.scroll = 0
        self._maxOptionLen = max(len(o) for o in self.options)
        self._aborted = False
        self._set_default(default)
        for plugin in plugins or []:
            register_plugin(self, plugin)
            plugin.init()

    def get_result(self):
        if self._aborted:
            return None
        else:
            selected = [o.result for o in self.options if o.selected]
            if not selected:
                selected.append(self._get_active_option().result)
            return selected

    def show(self):
        import keyboard
        self._print_menu()
        ansi.save_position()
        ansi.hide_cursor()
        try:
            for key in keyboard.keyboard_listener():
                stop = self._on_key(key)
                if stop:
                    return self.get_result()
                ansi.restore_position()
                ansi.up(self.height)
                self._print_menu()
        finally:
            self._clear_menu()
            ansi.show_cursor()

    def _set_default(self, default):
        # handle default selection of multiple options
        if isinstance(default, list) and default:
            if not self.multiselect:
                raise ValueError("multiple defaults passed, but multiselect is False")
            for option in self.options:
                if str(option) in default:
                    option.selected = True
            default = default[0]

        # handle default active option
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
        matches = [i for i, o in enumerate(self.options) if str(o) == s]
        if matches:
            return matches[0]
        else:
            return None

    def _get_active_option(self):
        return self.options[self.scroll+self.cursor] if self.options else None

    def _get_window(self):
        return self.options[self.scroll:self.scroll+self.height]

    def _get_debug_view(self):
        options = []
        for i, option in enumerate(self._get_window()):
            options.append(("(%s)" if i == self.cursor else "%s") % option)
        return " ".join(options)

    @pluggable
    def _on_key(self, key):
        func = "_on_" + key
        if hasattr(self, func):
            return getattr(self, func)()

    def _on_down(self):
        height = min(self.height, len(self.options))
        if self.cursor < height - 1:
            self.cursor += 1
        elif self.scroll + height < len(self.options):
            self.scroll += 1

    def _on_up(self):
        if self.cursor > 0:
            self.cursor -= 1
        elif self.scroll > 0:
            self.scroll -= 1

    def _on_pageDown(self):
        height = min(self.height, len(self.options))
        if self.cursor < height - 1:
            self.cursor = height - 1
        elif self.scroll + height * 2 < len(self.options):
            self.scroll += height
        else:
            self.scroll = len(self.options) - height

    def _on_pageUp(self):
        height = min(self.height, len(self.options))
        if self.cursor > 0:
            self.cursor = 0
        elif self.scroll - height >= 0:
            self.scroll -= height
        else:
            self.scroll = 0

    @pluggable
    def _on_space(self):
        if not self.multiselect:
            return
        option = self._get_active_option()
        option.selected = not option.selected
        self._on_down()

    def _on_esc(self):
        self._aborted = True
        return True # stop loop

    @pluggable
    def _on_enter(self):
        return True # stop loop

    def _clear_menu(self):
        ansi.restore_position()
        for i in xrange(self.height):
            ansi.clear_eol()
            ansi.up()
        ansi.clear_eol()

    @pluggable
    def _print_menu(self):
        _write("\r")
        for index, option in enumerate(self._get_window()):
            # all height to same width
            option = "{0:<{width}}".format(option, width=self._maxOptionLen)

            _write(self._decorate(option, **self._decorate_flags(index)) + "\n")
            ansi.clear_eol()

    @pluggable
    def _decorate_flags(self, index):
        return dict(
            active = (self.cursor == index),
            selected = (self.options[self.scroll+index].selected),
            moreAbove = (self.scroll > 0 and index == 0),
            moreBelow = (self.scroll + self.height < len(self.options) and index == self.height - 1),
        )

    @pluggable
    def _decorate(self, option, **flags):
        active = flags.get("active", False)
        selected = flags.get("selected", False)
        moreAbove = flags.get("moreAbove", False)
        moreBelow = flags.get("moreBelow", False)

        # add selection / cursor decorations
        if active and selected:
            option = "*" + ansi.colorize(option, "red", "white")
        elif active:
            option = " " + ansi.colorize(option, "black", "white")
        elif selected:
            option = "*" + ansi.colorize(option, "red")
        else:
            option = " " + option

        # add more above/below indicators
        if moreAbove:
            option = option + " " + ansi.colorize("^", "white", bright=True)
        elif moreBelow:
            option = option + " " + ansi.colorize("v", "white", bright=True)
        else:
            option = option + "  "

        return option

class Plugin(object):
    def init(self):
        pass

    def __getattr__(self, name):
        # allow calls to fall through to parent plugins if a method isn't defined
        return getattr(self.parent, name)

class FilterPlugin(Plugin):
    def __init__(self):
        self.text = None

    def init(self):
        self._allOptions = self.host.options[:]

    def _on_key(self, key):
        prevent = False
        if len(key) == 1 and 32 < ord(key) <= 127:
            if not self.text:
                self.text = []
            self.text.append(key)
            self._refilter()
        elif self.text and key == "backspace":
            del self.text[-1]
            self._refilter()
        elif self.text is not None and key == "esc":
            self.text = None
            ansi.hide_cursor()
            prevent = True
            self._refilter()

        if not prevent:
            return self.parent._on_key(key)

    def _print_menu(self):
        self.parent._print_menu()

        for i in xrange(0, self.host.height - len(self.host.options)):
            ansi.clear_eol()
            _write("\n")
        if self.text is not None:
            _write("/" + "".join(self.text))
            ansi.show_cursor()
        ansi.clear_eol()

    def _refilter(self):
        self.host.options = []
        text = "".join(self.text or []).lower()
        for option in self._allOptions:
            if text in str(option).lower() or option.attrs.get("showAlways"):
                self.host.options.append(option)
        #FIXME: it would be better to keep the selection
        self.host.cursor = 0
        self.host.scroll = 0

class HeaderPlugin(Plugin):
    def __init__(self, headers):
        self.headers = headers

    def init(self):
        options = []
        for i, option in enumerate(self.host.options):
            if i in self.headers:
                options.append(self.host._Option(self.headers[i], result=None, header=True, showAlways=True))
            options.append(option)
        self.host.options = options

    def _on_enter(self):
        # can't select a header
        if self.host._get_active_option().attrs.get("header") and self.host.get_result() == [None]:
            return False
        else:
            return self.parent._on_enter()

    def _on_space(self):
        if self.host._get_active_option().attrs.get("header"):
            self.host._on_down()
        else:
            self.parent._on_space()

    def _decorate_flags(self, index):
        flags = self.parent._decorate_flags(index)
        flags["header"] = self.host.options[self.host.scroll+index].attrs.get("header")
        return flags

    def _decorate(self, option, **flags):
        active = flags.get("active", False)
        header = flags.get("header", False)
        if header:
            if active:
                option = " " + ansi.colorize(option, "white", "black", bright=True)
            else:
                option = " " + ansi.colorize(option, "white", bright=True)
            return option
        else:
            return self.parent._decorate(option, **flags)

class Precolored(Plugin):
    def _decorate(self, option, **flags):
        active = flags.get("active", False)
        selected = flags.get("selected", False)
        moreAbove = flags.get("moreAbove", False)
        moreBelow = flags.get("moreBelow", False)

        # add selection / cursor decorations
        option = ("=> " if selected else "   ") + option
        if active:
            option = ansi.highlight(option, "black")

        # add more above/below indicators
        if moreAbove:
            option = option + " " + ansi.colorize("^", "white", bright=True)
        elif moreBelow:
            option = option + " " + ansi.colorize("v", "white", bright=True)
        else:
            option = option + "  "

        return option

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
        for i, option in enumerate(self.options):
            if _decorate:
                menu.append(ansi.colorize(option, "black", "white") if i == self.cursor else option)
            else:
                menu.append(option)
        menu = " ".join(menu)
        return menu

    def _print_menu(self, rewind):
        menu = self._make_menu()
        if rewind:
            menu = "\b"*len(self._make_menu(_decorate=False)) + menu
        _write(menu)

    def _clear_menu(self):
        menu = self._make_menu(_decorate=False)
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
    menu = Termenu(["option-%06d" % i for i in xrange(1,100)], height=10, plugins=[HeaderPlugin({0:"One",2:"Three",16:"Seventeen"}), FilterPlugin()])
#~     menu = Termenu(["option-%06d" % i for i in xrange(1,100)], height=10, plugins=[Precolored()])
    print menu.show()
#~     print "Would you like to continue? ",
#~     result = Minimenu(["Abort", "Retry", "Fail"], "Fail").show()
#~     print result
