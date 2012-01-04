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
    MAX_COLUMNS = 5
    def __init__(self, title, options, default=None, rows=None, columns=None, maxColumnWidth=None, encoding=None):
        self.title = title
        self.options = options
        self.maxColumnWidth = maxColumnWidth
        self.width = max(len(option) for option in self.options)
        if self.maxColumnWidth:
            self.width = min(self.maxColumnWidth, self.width)
        self.columns = self._compute_columns(columns)
        self.selected = self._compute_default(default)
        self.rows = self._compute_rows(rows)
        self.first = self.selected - self.selected % self.rows
        self.encoding = encoding

    def _reset_result(self):
        self.result = None

    def _shorten(self, text, width):
        if width and len(text) > width:
            text = text[:width/2-2]+"..."+text[-width/2+1:]
        return text

    def _compute_rows(self, rows):
        maxHeight = get_terminal_size()[1]-2
        if rows is None:
            rows = maxHeight
        return min(len(self.options), rows, maxHeight)

    def _compute_columns(self, columns):
        if columns is None:
            columns = self.MAX_COLUMNS
        return min(columns, get_terminal_size()[0] / (self.width + 2))

    def _compute_default(self, default):
        if default is None:
            default = 0
        else:
            try:
                default = self.options.index(default)
            except ValueError:
                default = 0
        return max(0, default % len(self.options))

    def _print(self, data):
        sys.stdout.write(data)
        sys.stdout.flush()

    def _print_menu(self):
        page = self.options[self.first:self.first+self.rows*self.columns]
        for row in xrange(self.rows):
            lineItemIndexes = range(row, row+len(page), self.rows)
            items = []
            for index in lineItemIndexes:
                if index < len(page):
                    items.append(self._build_menu_item(self.first + index, page[index]))
            self._print(" ".join(items))
            ansi.clear_eol()
            self._print("\n")

    def _build_menu_item(self, index, option):
        option = self._shorten(option, self.maxColumnWidth)
        if self.rows > 1:
            item = option + " " * (self.width - len(option))
        else:
            item = option
        if self.encoding:
            item = item.encode(self.encoding)
        item = self._colorize_item(index, item, )
        item = self._build_left_marker(index) + item + self._build_right_marker(index)
        return item

    def _build_left_marker(self, index):
        if index > 0 and index == self._top_left():
            marker = ansi.colorize("^", "white", bright=True)
        elif self._top_left() <= index <= self._bottom_left():
            marker = " "
        else:
            marker = ""
        return marker

    def _build_right_marker(self, index):
        if index < len(self.options) - 1 and index == self._bottom_right():
            marker = ansi.colorize("v", "white", bright=True)
        elif self._top_right() <= index <= self._bottom_right():
            marker = " "
        else:
            marker = ""
        return marker

    def _colorize_item(self, index, item):
        if index == self.selected:
            item = ansi.colorize(item, "black", "white")
        return item

    def _items_in_page(self):
        return min(self.rows * self.columns, len(self.options))

    def _top_right(self):
        return self.first + self.rows * (self.columns - 1)

    def _bottom_right(self):
        return self.first + self.rows * self.columns - 1

    def _top_left(self):
        return self.first

    def _bottom_left(self):
        return self.first + self.rows - 1

    def _on_down(self):
        if self.selected == self.first + self._items_in_page() - 1:
            self.first += 1
        self.selected += 1
        self._adjust_selected()

    def _on_up(self):
        if self.selected == self.first:
            self.first -= 1
        self.selected -= 1
        self._adjust_selected()

    def _on_right(self):
        if self.selected >= self._top_right():
            if self.selected < self._bottom_right():
                self.selected = self._bottom_right()
            elif self.selected == self._bottom_right():
                self.first += self.rows
                self.selected += self.rows
        else:
            self.selected += self.rows
        self._adjust_selected()

    def _on_left(self):
        if self.selected <= self._bottom_left():
            if self.selected > self._top_left():
                self.selected = self._top_left()
            elif self.selected == self._top_left():
                self.first -= self.rows
                self.selected -= self.rows
        else:
            self.selected -= self.rows
        self._adjust_selected()

    def _on_pageDown(self):
        if self.selected == self.first + self._items_in_page() - 1:
            self.selected += self._items_in_page()
            self.first += self._items_in_page()
        else:
            self.selected = self.first + self._items_in_page() - 1
        self._adjust_selected()

    def _on_pageUp(self):
        if self.selected == self.first:
            self.selected -= self._items_in_page()
            self.first -= self._items_in_page()
        else:
            self.selected = self.first
        self._adjust_selected()

    def _on_home(self):
        self.selected = 0
        self.first = 0
        self._adjust_selected()

    def _on_end(self):
        self.selected = len(self.options)-1
        self.first = self.selected - self._items_in_page() + 1
        self._adjust_selected()

    def _on_enter(self):
        self.result = self.options[self.selected]
        return True

    def _on_esc(self):
        self._reset_result()
        return True

    def _dispatch_key(self, key):
        handler = "_on_" + key
        if hasattr(self, handler):
            return getattr(self, handler)()

    def _adjust_selected(self):
        if self.selected < 0:
            self.selected = 0
        if self.selected > len(self.options)-1:
            self.selected = len(self.options)-1
        if self.first < 0:
            self.first = 0
        if self.first > (len(self.options) - self._items_in_page()):
            self.first = len(self.options) - self._items_in_page()

    def _clear_menu(self):
        ansi.restore_position()
        lines = self.rows
        if self.title:
            lines += 1
        ansi.up(lines)
        for i in xrange(lines):
            ansi.clear_line()
            ansi.down()
        ansi.clear_line()
        ansi.up(lines)

    def show(self):
        """
        Show the menu and run the keyboard loop. The return value is the text of the chosen option
        if Enter was pressed and None is Esc was pressed.
        """
        import keyboard
        if self.title:
            self._print(ansi.colorize(self.title, "white", bright=True) + "\n")
        self._print_menu()
        ansi.save_position() # save bottom-of-menu position for future reference
        ansi.hide_cursor()
        try:
            for key in keyboard.keyboard_listener():
                ret = self._dispatch_key(key)
                if ret:
                    return self.result
                ansi.restore_position() # go to bottom of menu
                ansi.up(self.rows) # go to top of menu
                self._print_menu()
        finally:
            self._clear_menu()
            ansi.show_cursor()

class FilterMixin(object):
    def __init__(self, *args, **kwargs):
        super(FilterMixin, self).__init__(*args, **kwargs)
        self.filterMode = False
        self.filterText = ""
        self._allOptions = self.options
        self._fullHeight = self.rows
        self._refilter()

    def _print_menu(self):
        if self.options:
            super(FilterMixin, self)._print_menu()
        else:
            for i in xrange(self.rows):
                ansi.clear_line()
                ansi.down()
        ansi.clear_line()
        if self.filterMode:
            self._print("/" + self.filterText)

    def _start_filter(self):
        if not self.filterMode:
            self.filterText = ""
            self.filterMode = True
            ansi.show_cursor()

    def _stop_filter(self):
        if self.filterMode:
            self.filterMode = False
            ansi.hide_cursor()
            self._refilter()

    def _refilter(self):
        if self.filterMode:
            filtered = [(i, o) for i, o in enumerate(self._allOptions) if self.filterText.lower() in o.lower()]
            self.options = [o for i,o in filtered]
            self._indexes = [i for i,o in filtered]
        else:
            self.options = self._allOptions
            self._indexes = xrange(len(self._allOptions))
        self.selected = 0
        self.first = 0

    def _on_backspace(self):
        if self.filterMode and self.filterText:
            self.filterText = self.filterText[:-1]
            self._refilter()

    def _on_esc(self):
        if self.filterMode:
            self._stop_filter()
            return False
        else:
            return super(FilterMixin, self)._on_esc()

    def _dispatch_key(self, key):
        if len(key) == 1 and 32 < ord(key) < 127:
            self._start_filter()
            self.filterText += key
            self._refilter()
        else:
            return super(FilterMixin, self)._dispatch_key(key)

class SearchMixin(object):
    def __init__(self, *args, **kwargs):
        super(SearchMixin, self).__init__(*args, **kwargs)
        self.options.sort()
        self.searchMode = False
        self.searchText = ""

    def _print_menu(self):
        super(SearchMixin, self)._print_menu()
        ansi.clear_line()
        if self.searchMode:
            self._print("/" + self.searchText)

    def _start_search(self):
        if not self.searchMode:
            self.searchText = ""
            self.searchMode = True
            ansi.show_cursor()

    def _stop_search(self):
        if self.searchMode:
            self.searchMode = False
            ansi.hide_cursor()

    def _on_backspace(self):
        if self.searchMode and self.searchText:
            self.searchText = self.searchText[:-1]

    def _on_esc(self):
        if self.searchMode:
            self._stop_search()
            return False
        else:
            return super(SearchMixin, self)._on_esc()

    def _dispatch_key(self, key):
        if len(key) == 1 and 32 < ord(key) < 127:
            self._start_search()
            # search longer text
            self.searchText += key
            lowerSearchText = self.searchText.lower()
            matches = [i for i, option in enumerate(self.options) if option.lower().startswith(lowerSearchText)]
            if matches:
                self.selected = matches[0]
                if self.selected >= self.first + self._items_in_page() - 1:
                    self.first = self.selected - self._items_in_page() + 1
        else:
            if key in "up down left right pageUp pageDown home end".split():
                self._stop_search()
            return super(SearchMixin, self)._dispatch_key(key)

class MultiSelectMixin(object):
    def __init__(self, *args, **kwargs):
        super(MultiSelectMixin, self).__init__(*args, **kwargs)
        self.selectedItems = set()

    def _build_left_marker(self, index):
        marker = super(MultiSelectMixin, self)._build_left_marker(index)
        marker += "*" if self._is_multi_selected(index) else " "
        return marker

    def _build_right_marker(self, index):
        marker = super(MultiSelectMixin, self)._build_right_marker(index)
        marker = " " + marker
        return marker

    def _colorize_item(self, index, item):
        multiSelected = self._is_multi_selected(index)
        if index == self.selected:
            if multiSelected:
                item = ansi.colorize(item, "red", "white", bright=True)
            else:
                item = ansi.colorize(item, "black", "white")
        elif multiSelected:
                item = ansi.colorize(item, "red", bright=True)
        return item

    def _is_multi_selected(self, index):
        return index < len(self.options) and self.options[index] in self.selectedItems

    def _on_enter(self):
        if not self.selectedItems:
            self.selectedItems.add(self.options[self.selected])
        self.result = list(sorted(self.selectedItems))
        return True

    def _on_space(self):
        option = self.options[self.selected]
        if option in self.selectedItems:
            self.selectedItems.remove(option)
        else:
            self.selectedItems.add(option)
        self._on_down()

def show_menu(title, options, default=None, rows=None, columns=None, maxColumnWidth=None, multiSelect=False):
    if multiSelect:
        class MenuClass(MultiSelectMixin, FilterMixin, Menu):
            pass
    else:
        class MenuClass(FilterMixin, Menu):
            pass
    menu = MenuClass(title, options, default, rows, columns, maxColumnWidth)
    return menu.show()
