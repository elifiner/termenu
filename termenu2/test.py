import sys
sys.path.append("..")
import unittest
import ansi
from termenu import Termenu

OPTIONS = ["%02d" % i for i in xrange(1,100)]

def strmenu(menu):
    s = " ".join(menu.get_visible_lines())
    s = s.replace(menu.get_active(), "(%s)" % menu.get_active())
    return s

class Down(unittest.TestCase):
    def test_cursor_top(self):
        menu = Termenu(OPTIONS, lines=3)
        assert strmenu(menu) == "(01) 02 03"
        menu.on_down()
        assert strmenu(menu) == "01 (02) 03"

    def test_cursor_middle(self):
        menu = Termenu(OPTIONS, lines=3)
        menu.cursor = 1
        assert strmenu(menu) == "01 (02) 03"
        menu.on_down()
        assert strmenu(menu) == "01 02 (03)"

    def test_cursor_bottom(self):
        menu = Termenu(OPTIONS, lines=3)
        menu.cursor = 2
        assert strmenu(menu) == "01 02 (03)"
        menu.on_down()
        assert strmenu(menu) == "02 03 (04)"

    def test_scroll_bottom_cursor_bottom(self):
        menu = Termenu(OPTIONS, lines=3)
        menu.scroll = len(OPTIONS) - 3
        menu.cursor = 2
        assert strmenu(menu) == "97 98 (99)"
        menu.on_down()
        assert strmenu(menu) == "97 98 (99)"

class Up(unittest.TestCase):
    def test_cursor_top(self):
        menu = Termenu(OPTIONS, lines=3)
        menu.cursor = 0
        assert strmenu(menu) == "(01) 02 03"
        menu.on_up()
        assert strmenu(menu) == "(01) 02 03"

    def test_cursor_middle(self):
        menu = Termenu(OPTIONS, lines=3)
        menu.cursor = 1
        assert strmenu(menu) == "01 (02) 03"
        menu.on_up()
        assert strmenu(menu) == "(01) 02 03"

    def test_cursor_bottom(self):
        menu = Termenu(OPTIONS, lines=3)
        menu.cursor = 2
        assert strmenu(menu) == "01 02 (03)"
        menu.on_up()
        assert strmenu(menu) == "01 (02) 03"

    def test_scroll_bottom_cursor_top(self):
        menu = Termenu(OPTIONS, lines=3)
        menu.scroll = len(OPTIONS) - 3
        menu.cursor = 0
        assert strmenu(menu) == "(97) 98 99"
        menu.on_up()
        assert strmenu(menu) == "(96) 97 98"

class PageDown(unittest.TestCase):
    def test_cursor_top(self):
        menu = Termenu(OPTIONS, lines=4)
        assert strmenu(menu) == "(01) 02 03 04"
        menu.on_pageDown()
        assert strmenu(menu) == "01 02 03 (04)"

    def test_cursor_middle(self):
        menu = Termenu(OPTIONS, lines=4)
        menu.cursor = 1
        assert strmenu(menu) == "01 (02) 03 04"
        menu.on_pageDown()
        assert strmenu(menu) == "01 02 03 (04)"

    def test_cursor_bottom(self):
        menu = Termenu(OPTIONS, lines=4)
        menu.cursor = 3
        assert strmenu(menu) == "01 02 03 (04)"
        menu.on_pageDown()
        assert strmenu(menu) == "05 06 07 (08)"

    def test_scroll_bottom_cursor_bottom(self):
        menu = Termenu(OPTIONS, lines=4)
        menu.scroll = len(OPTIONS) - 4
        menu.cursor = 3
        assert strmenu(menu) == "96 97 98 (99)"
        menu.on_pageDown()
        assert strmenu(menu) == "96 97 98 (99)"

    def test_scroll_almost_bottom_cursor_bottom(self):
        menu = Termenu(OPTIONS, lines=4)
        menu.scroll = len(OPTIONS) - 5
        menu.cursor = 3
        assert strmenu(menu) == "95 96 97 (98)"
        menu.on_pageDown()
        assert strmenu(menu) == "96 97 98 (99)"

class PageUp(unittest.TestCase):
    def test_cursor_top(self):
        menu = Termenu(OPTIONS, lines=4)
        assert strmenu(menu) == "(01) 02 03 04"
        menu.on_pageUp()
        assert strmenu(menu) == "(01) 02 03 04"

    def test_cursor_middle(self):
        menu = Termenu(OPTIONS, lines=4)
        menu.cursor = 2
        assert strmenu(menu) == "01 02 (03) 04"
        menu.on_pageUp()
        assert strmenu(menu) == "(01) 02 03 04"

    def test_cursor_bottom(self):
        menu = Termenu(OPTIONS, lines=4)
        menu.cursor = 3
        assert strmenu(menu) == "01 02 03 (04)"
        menu.on_pageUp()
        assert strmenu(menu) == "(01) 02 03 04"

    def test_scroll_bottom_cursor_top(self):
        menu = Termenu(OPTIONS, lines=4)
        menu.scroll = len(OPTIONS) - 4
        assert strmenu(menu) == "(96) 97 98 99"
        menu.on_pageUp()
        assert strmenu(menu) == "(92) 93 94 95"

    def test_scroll_almost_top_cursor_top(self):
        menu = Termenu(OPTIONS, lines=4)
        menu.scroll = 1 
        assert strmenu(menu) == "(02) 03 04 05"
        menu.on_pageUp()
        assert strmenu(menu) == "(01) 02 03 04"

class MultiSelect(unittest.TestCase):
    def test_select(self):
        menu = Termenu(OPTIONS, lines=4)
        assert strmenu(menu) == "(01) 02 03 04"
        menu.on_space()
        menu.on_space()
        assert strmenu(menu) == "01 02 (03) 04"
        assert " ".join(menu.get_selected()) == "01 02"
        assert " ".join(menu.get_result()) == "01 02"

    def test_deselect(self):
        menu = Termenu(OPTIONS, lines=4)
        assert strmenu(menu) == "(01) 02 03 04"
        menu.on_space()
        menu.on_up()
        menu.on_space()
        assert strmenu(menu) == "01 (02) 03 04"
        assert " ".join(menu.get_selected()) == ""
        assert " ".join(menu.get_result()) == "02"

def active(s):
    return ansi.colorize(s, "black", "white")

def selected(s):
    return ansi.colorize(s, "red")

def active_selected(s):
    return ansi.colorize(s, "red", "white")

def white(s):
    return ansi.colorize(s, "white", bright=True)

class Decorate(unittest.TestCase):
    def test_active(self):
        menu = Termenu(OPTIONS, lines=4)
        assert menu.decorate("text", active=True) == " " + active("text") + " "

    def test_selected(self):
        menu = Termenu(OPTIONS, lines=4)
        assert menu.decorate("text", selected=True) == "*" + selected("text") + " "

    def test_active_selected(self):
        menu = Termenu(OPTIONS, lines=4)
        assert menu.decorate("text", active=True, selected=True) == "*" + active_selected("text") + " "

    def test_more_above(self):
        menu = Termenu(OPTIONS, lines=4)
        assert menu.decorate("text", active=True, selected=True, moreAbove=True) == "*" + active_selected("text") + white("^")

    def test_more_below(self):
        menu = Termenu(OPTIONS, lines=4)
        assert menu.decorate("text", active=True, selected=True, moreBelow=True) == "*" + active_selected("text") + white("v")

    def test_max_option_len(self):
        menu = Termenu("one three fifteen twenty eleven".split(), lines=4)
        assert menu.decorate("three", active=True, selected=True) == "*" + active_selected("three  ") + " "

if __name__ == "__main__":
    unittest.main()
