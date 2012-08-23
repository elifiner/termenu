def pluggable(method):
    def wrapped(self, *args, **kwargs):
        return getattr(self._plugins[-1], method.__name__)(*args, **kwargs)
    wrapped.original = method
    return wrapped

class Host(object):
    def register_plugin(self, plugin):
        if not hasattr(self, "_plugins"):
            server = self
            class OriginalMethods(object):
                def __getattr__(self, name):
                    return lambda *args, **kwargs: getattr(server, name).original(server, *args, **kwargs)
            self._plugins = [OriginalMethods()]
        plugin.base = self._plugins[-1]
        self._plugins.append(plugin)

# ----------------------------------------------------------------------

if __name__ == "__main__":
    class SampleHost(Host):
        @pluggable
        def foo(self, param):
            print "original %s" % param
            return 7

    class SamplePlugin(object):
        def __init__(self, name):
            self.name = name

        def foo(self, param):
            print "%s enter %s" % (self.name, param)
            result = self.base.foo(param)
            print "%s enter %s" % (self.name, param)
            return result

    plugin1 = SamplePlugin("sample1")
    plugin2 = SamplePlugin("sample2")
    server = SampleHost()
    server.register_plugin(plugin1)
    server.register_plugin(plugin2)
    print server.foo("momo")
