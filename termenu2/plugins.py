def pluggable(method):
    """
    Marks a method to be extendable via plugins.
    When the method is called, the last installed plugin will be called and the 
    call will propagate up the stack of plugins until the original method is called.
    """
    def wrapped(self, *args, **kwargs):
        stack = [lambda *args, **kwargs: method(self, *args, **kwargs)]
        for plugin in self._plugins:
            if hasattr(plugin, method.__name__):
                stack.append(getattr(plugin, method.__name__))
        return call_previous(stack, *args, **kwargs)
    return wrapped

def call_previous(stack, *args, **kwargs):
    """
    Calls the previous plugin in the plugin chain.
    """
    method = stack.pop()
    if stack:
        return method(stack, *args, **kwargs)
    else:
        return method(*args, **kwargs)

class Plugin(object):
    pass

class Server(object):
    def register_plugin(self, plugin):
        if not hasattr(self, "_plugins"):
            self._plugins = []
        self._plugins.append(plugin)

# ----------------------------------------------------------------------

class SampleServer(Server):
    @pluggable
    def foo(self, param):
        print "original %s" % param
        return 7

class SamplePlugin(Plugin):
    def __init__(self, name):
        self.name = name

    def foo(self, stack, param):
        print "%s enter %s" % (self.name, param)
        result = call_previous(stack, param)
        print "%s enter %s" % (self.name, param)
        return result

if __name__ == "__main__":
    plugin1 = SamplePlugin("sample1")
    plugin2 = SamplePlugin("sample2")
    server = SampleServer()
    server.register_plugin(plugin1)
    server.register_plugin(plugin2)
    print server.foo("momo")
