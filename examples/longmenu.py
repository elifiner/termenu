import sys
sys.path.insert(0, "..")
import termenu

class IteratorList(object):
    def __init__(self, iter):
        self._iter = iter
        self._list = []

    def __getitem__(self, index):
        try:
            while index >= len(self._list):
                self._list.append(self._iter.next())
        except StopIteration:
            pass
        return self._list[index]

    def __slice__(self, i, j):
        self[j]
        return self._list[i:j]

def show_long_menu(optionsIter, pagesize=30):
    Next = object()
    Previous = object()
    options = IteratorList("%05d" % n for n in optionsIter)
    start = 0
    while True:
        page = options[start:start+pagesize]
        results = page[:]
        if len(page) == pagesize:
            page.append(">>")
            results.append(Next)
        if start > 0:
            page.insert(0, "<<")
            results.insert(0, Previous)
        result = termenu.Termenu(page, results=results).show()
        if not result:
            break
        if result == [Next]:
            start = start + pagesize
        elif result == [Previous]:
            start = start - pagesize
        else:
            break

    return result

if __name__ == "__main__":
    show_long_menu(xrange(500))
