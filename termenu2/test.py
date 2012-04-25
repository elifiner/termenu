import unittest
from termenu import Termenu

OPTIONS = ["%02d" % i for i in xrange(1,100)]

def strmenu(menu):
    s = " ".join(menu.get_visible_lines())
    s = s.replace(menu.get_selected(), "(%s)" % menu.get_selected())
    return s

class Down(unittest.TestCase):
    def test_cursor_top(self):
        menu = Termenu(OPTIONS, lines=3)
        assert strmenu(menu) == "(01) 02 03"
        menu.down()
        assert strmenu(menu) == "01 (02) 03"

    def test_cursor_middle(self):
        menu = Termenu(OPTIONS, lines=3)
        menu.cursor = 1
        assert strmenu(menu) == "01 (02) 03"
        menu.down()
        assert strmenu(menu) == "01 02 (03)"

    def test_cursor_bottom(self):
        menu = Termenu(OPTIONS, lines=3)
        menu.cursor = 2
        assert strmenu(menu) == "01 02 (03)"
        menu.down()
        assert strmenu(menu) == "02 03 (04)"

    def test_scroll_bottom_cursor_bottom(self):
        menu = Termenu(OPTIONS, lines=3)
        menu.scroll = len(OPTIONS) - 3
        menu.cursor = 2
        assert strmenu(menu) == "97 98 (99)"
        menu.down()
        assert strmenu(menu) == "97 98 (99)"

class Up(unittest.TestCase):
    def test_cursor_top(self):
        menu = Termenu(OPTIONS, lines=3)
        menu.cursor = 0
        assert strmenu(menu) == "(01) 02 03"
        menu.up()
        assert strmenu(menu) == "(01) 02 03"

    def test_cursor_middle(self):
        menu = Termenu(OPTIONS, lines=3)
        menu.cursor = 1
        assert strmenu(menu) == "01 (02) 03"
        menu.up()
        assert strmenu(menu) == "(01) 02 03"

    def test_cursor_bottom(self):
        menu = Termenu(OPTIONS, lines=3)
        menu.cursor = 2
        assert strmenu(menu) == "01 02 (03)"
        menu.up()
        assert strmenu(menu) == "01 (02) 03"

    def test_scroll_bottom_cursor_top(self):
        menu = Termenu(OPTIONS, lines=3)
        menu.scroll = len(OPTIONS) - 3
        menu.cursor = 0
        assert strmenu(menu) == "(97) 98 99"
        menu.up()
        assert strmenu(menu) == "(96) 97 98"

class PageDown(unittest.TestCase):
    def test_cursor_top(self):
        menu = Termenu(OPTIONS, lines=4)
        assert strmenu(menu) == "(01) 02 03 04"
        menu.pagedown()
        assert strmenu(menu) == "01 02 03 (04)"

    def test_cursor_middle(self):
        menu = Termenu(OPTIONS, lines=4)
        menu.cursor = 1
        assert strmenu(menu) == "01 (02) 03 04"
        menu.pagedown()
        assert strmenu(menu) == "01 02 03 (04)"

    def test_cursor_bottom(self):
        menu = Termenu(OPTIONS, lines=4)
        menu.cursor = 3
        assert strmenu(menu) == "01 02 03 (04)"
        menu.pagedown()
        assert strmenu(menu) == "05 06 07 (08)"

    def test_scroll_bottom_cursor_bottom(self):
        menu = Termenu(OPTIONS, lines=4)
        menu.scroll = len(OPTIONS) - 4
        menu.cursor = 3
        assert strmenu(menu) == "96 97 98 (99)"
        menu.pagedown()
        assert strmenu(menu) == "96 97 98 (99)"

    def test_scroll_almost_bottom_cursor_bottom(self):
        menu = Termenu(OPTIONS, lines=4)
        menu.scroll = len(OPTIONS) - 5
        menu.cursor = 3
        assert strmenu(menu) == "95 96 97 (98)"
        menu.pagedown()
        assert strmenu(menu) == "96 97 98 (99)"

class PageUp(unittest.TestCase):
    def test_cursor_top(self):
        menu = Termenu(OPTIONS, lines=4)
        assert strmenu(menu) == "(01) 02 03 04"
        menu.pageup()
        assert strmenu(menu) == "(01) 02 03 04"

    def test_cursor_middle(self):
        menu = Termenu(OPTIONS, lines=4)
        menu.cursor = 2
        assert strmenu(menu) == "01 02 (03) 04"
        menu.pageup()
        assert strmenu(menu) == "(01) 02 03 04"

    def test_cursor_bottom(self):
        menu = Termenu(OPTIONS, lines=4)
        menu.cursor = 3
        assert strmenu(menu) == "01 02 03 (04)"
        menu.pageup()
        assert strmenu(menu) == "(01) 02 03 04"

    def test_scroll_bottom_cursor_top(self):
        menu = Termenu(OPTIONS, lines=4)
        menu.scroll = len(OPTIONS) - 4
        assert strmenu(menu) == "(96) 97 98 99"
        menu.pageup()
        assert strmenu(menu) == "(92) 93 94 95"

    def test_scroll_almost_top_cursor_top(self):
        menu = Termenu(OPTIONS, lines=4)
        menu.scroll = 1 
        assert strmenu(menu) == "(02) 03 04 05"
        menu.pageup()
        assert strmenu(menu) == "(01) 02 03 04"

if __name__ == "__main__":
    unittest.main()
