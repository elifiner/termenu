import unittest
from termenu import Termenu

OPTIONS = ["%02d" % i for i in xrange(1,100)]

class TermenuTest(unittest.TestCase):
    def test_init(self):
        menu = Termenu(OPTIONS, lines=3)
        assert menu.make_lines() == "01 02 03".split()
        assert menu.get_selected() == "01"

class Down(unittest.TestCase):
    def test_scroll_top_cursor_top(self):
        menu = Termenu(OPTIONS, lines=3)
        menu.down()
        assert menu.make_lines() == "01 02 03".split()
        assert menu.get_selected() == "02"

    def test_scroll_top_cursor_middle(self):
        menu = Termenu(OPTIONS, lines=3)
        menu.cursor = 1
        menu.down()
        assert menu.make_lines() == "01 02 03".split()
        assert menu.get_selected() == "03"

    def test_scroll_top_cursor_bottom(self):
        menu = Termenu(OPTIONS, lines=3)
        menu.cursor = 2
        menu.down()
        assert menu.make_lines() == "02 03 04".split()
        assert menu.get_selected() == "04"

    def test_scroll_bottom_cursor_bottom(self):
        menu = Termenu(OPTIONS, lines=3)
        menu.scroll = len(OPTIONS) - 3
        menu.cursor = 2
        menu.down()
        assert menu.make_lines() == "97 98 99".split()
        assert menu.get_selected() == "99"

class Up(unittest.TestCase):
    def test_scroll_top_cursor_bottom(self):
        menu = Termenu(OPTIONS, lines=3)
        menu.cursor = 2
        menu.up()
        assert menu.make_lines() == "01 02 03".split()
        assert menu.get_selected() == "02"

    def test_scroll_top_cursor_middle(self):
        menu = Termenu(OPTIONS, lines=3)
        menu.cursor = 1
        menu.up()
        assert menu.make_lines() == "01 02 03".split()
        assert menu.get_selected() == "01"

    def test_scroll_top_cursor_top(self):
        menu = Termenu(OPTIONS, lines=3)
        menu.cursor = 0
        menu.up()
        assert menu.make_lines() == "01 02 03".split()
        assert menu.get_selected() == "01"

    def test_scroll_bottom_cursor_top(self):
        menu = Termenu(OPTIONS, lines=3)
        menu.scroll = len(OPTIONS) - 3
        menu.cursor = 0
        menu.up()
        assert menu.make_lines() == "96 97 98".split()
        assert menu.get_selected() == "96"

class PageDown(unittest.TestCase):
    def test_scroll_top_cursor_top(self):
        menu = Termenu(OPTIONS, lines=4)
        menu.pagedown()
        assert menu.make_lines() == "01 02 03 04".split()
        assert menu.get_selected() == "04"

    def test_scroll_top_cursor_middle(self):
        menu = Termenu(OPTIONS, lines=4)
        menu.cursor = 1
        menu.pagedown()
        assert menu.make_lines() == "01 02 03 04".split()
        assert menu.get_selected() == "04"

    def test_scroll_top_cursor_bottom(self):
        menu = Termenu(OPTIONS, lines=4)
        menu.cursor = 3
        menu.pagedown()
        assert menu.make_lines() == "05 06 07 08".split()
        assert menu.get_selected() == "08"

    def test_scroll_bottom_cursor_bottom(self):
        menu = Termenu(OPTIONS, lines=4)
        menu.scroll = len(OPTIONS) - 4
        menu.cursor = 3
        menu.pagedown()
        assert menu.make_lines() == "96 97 98 99".split()
        assert menu.get_selected() == "99"

    def test_scroll_almost_bottom_cursor_bottom(self):
        menu = Termenu(OPTIONS, lines=4)
        menu.scroll = len(OPTIONS) - 5
        menu.cursor = 3
        menu.pagedown()
        assert menu.make_lines() == "96 97 98 99".split()
        assert menu.get_selected() == "99"

class PageUp(unittest.TestCase):
    pass

if __name__ == "__main__":
    unittest.main()
