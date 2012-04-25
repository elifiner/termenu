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

    def down(self):
        if self.cursor < self.lines - 1:
            self.cursor += 1
        elif self.scroll + self.lines < len(self.options):
            self.scroll += 1

    def up(self):
        if self.cursor > 0:
            self.cursor -= 1
        elif self.scroll > 0:
            self.scroll -= 1

    def pagedown(self):
        if self.cursor < self.lines - 1:
            self.cursor = self.lines - 1
        elif self.scroll + self.lines * 2 < len(self.options):
            self.scroll += self.lines
        else:
            self.scroll = len(self.options) - self.lines

    def pageup(self):
        if self.cursor > 0:
            self.cursor = 0
        elif self.scroll - self.lines >= 0:
            self.scroll -= self.lines
        else:
            self.scroll = 0

