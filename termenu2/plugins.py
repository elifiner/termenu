def pluggable(method):
    def wrapped(self, *args, **kwargs):
        stack = [method]
        for plugin in self.plugins:
            stack.append(getattr(plugin, method.__name__))
        return call_previous(stack, *args, **kwargs)
    return wrapped

def call_previous(stack, *args, **kwargs):
    return stack[-1](stack[:-1], *args, **kwargs)

class Plugin(object):
    pass

class Termenu(object):
    def __init__(self, plugins):
        self.plugins = plugins

    @pluggable
    def dummy(self, param):
        print "original %s" % param
        return 7

class SamplePlugin(Plugin):
    def __init__(self, name):
        self.name = name

    def dummy(self, stack, param):
        print "%s enter %s" % (self.name, param)
        result = call_previous(stack, param)
        print "%s enter %s" % (self.name, param)
        return result

if __name__ == "__main__":
    plugin1 = SamplePlugin("sample1")
    plugin2 = SamplePlugin("sample2")
    menu = Termenu([plugin1, plugin2])
    print menu.dummy("momo")
